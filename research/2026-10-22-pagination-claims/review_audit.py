"""Independent local audit. Needs private evidence; makes no service calls.

The reviewer read the author's implementation before writing this audit.
The score calculation uses target positions and prefix endpoints, and does
not import or call the author's scoring code.
"""
import datetime
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRIVATE = ROOT / "private"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token_sha(value):
    return hashlib.sha256(value.encode()).hexdigest() if value else None


def object_sha(value):
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    checks = []

    def check(value, description):
        if not value:
            raise AssertionError(description)
        checks.append(description)

    cfg_path = PRIVATE / "pagination/query_freeze.json"
    cfg = read(cfg_path)
    pub_cfg = read(HERE / "query_freeze.json")
    trace = read(HERE / "live_trace.json")
    results = read(HERE / "live_results.json")
    manifest = read(PRIVATE / "manifest.json")
    freeze = datetime.datetime.fromisoformat(cfg["frozen_at_utc"])
    check(sha(cfg_path) == pub_cfg["private_query_freeze_sha256"], "private query freeze hash")
    for name, digest in cfg["plan_hashes"].items():
        check(sha(ROOT / name) == digest, "unchanged frozen plan: " + name)
    for name, digest in read(HERE / "analysis_freeze.json")["sha256"].items():
        check(sha(HERE / name) == digest, "unchanged frozen analysis: " + name)

    raw_records = []
    evidence_paths = [cfg_path]
    sensitive = set()
    independent_cases = []
    checked_inventory_rows = 0
    provider_orders = {}
    for provider in ("drive", "calendar"):
        identities = cfg["target_ids"][provider]
        inverse = {identity: alias for alias, identity in identities.items()}
        check(len(inverse) == 4, provider + " four unique frozen IDs")
        check(list(identities) == pub_cfg["target_aliases"][provider], provider + " alias freeze")
        for alias, identity in identities.items():
            check(manifest[provider + ":" + alias]["id"] == identity, provider + " manifest ID " + alias)
            setup_path = PRIVATE / ("setup-" + provider + "-" + alias + ".json")
            setup = read(setup_path)
            body = setup["result"]["structuredContent"]
            check(body["id"] == identity, provider + " setup ID " + alias)
            check(not setup["result"].get("isError"), provider + " setup has no tool error " + alias)
            check(datetime.datetime.fromisoformat(setup["ended"]) < freeze, provider + " setup before query freeze " + alias)
            if provider == "calendar":
                check(body["reminders"] == {"use_default": False, "overrides": []}, "no saved reminders " + alias)
                check(setup["args"]["attendees"] == [], "no requested attendees " + alias)
                organizer = body["organizer"]
                attendees = body["attendees"]
                check(len(attendees) == 1 and attendees[0].get("email") == organizer.get("email"), "self organizer only " + alias)
            evidence_paths.append(setup_path)
            sensitive.add(identity)
        pub = trace["providers"][provider]
        previous = None
        previous_end = freeze
        pages = []
        paths = sorted((PRIVATE / "pagination").glob(provider + "-page-*.json"))
        paths.append(PRIVATE / "pagination" / (provider + "-empty-control.json"))
        for path in paths:
            record = read(path)
            raw_records.append(record)
            evidence_paths.append(path)
            control = record["kind"] == "empty_control"
            number = record["page"]
            public = pub["empty_control"] if control else pub["pages"][number - 1]
            check(record["provider"] == provider and record["tool"] == cfg["tools"][provider], path.name + " provider/tool")
            started = datetime.datetime.fromisoformat(record["started_at_utc"])
            ended = datetime.datetime.fromisoformat(record["finished_at_utc"])
            check(freeze < started <= ended, path.name + " time after freeze")
            if not control:
                check(started >= previous_end, path.name + " sequential calls")
                previous_end = ended
            expected = dict(cfg["empty_control_queries" if control else "queries"][provider])
            token_key = "page_token" if provider == "drive" else "next_page_token"
            if not control and number > 1:
                expected[token_key] = previous
            check(record["request"] == expected, path.name + " exact query and prior token")
            response = record["response"]
            check(not response.get("isError") and "tool_exception" not in response, path.name + " no error")
            body = response["structuredContent"]
            items = body["results" if provider == "drive" else "events"]
            check(all(item["id"] in inverse for item in items), path.name + " frozen membership")
            aliases = [inverse[item["id"]] for item in items]
            nxt = body.get("next_page_token")
            check(not any("incomplete" in key.lower() or "coverage" in key.lower() for key in body), path.name + " absent coverage field")
            expected_public = {
                "page": number,
                "started_at_utc": record["started_at_utc"],
                "finished_at_utc": record["finished_at_utc"],
                "aliases": aliases,
                "connector_exposed_item_count": len(items),
                "request_token_sha256": token_sha(record["request"].get(token_key)),
                "next_token_sha256": token_sha(nxt),
                "next_token_representation": "absent" if "next_page_token" not in body else "null" if nxt is None else "empty_string" if nxt == "" else "value",
                "coverage_status": "unknown",
                "coverage_fields": {},
                "private_record_sha256": sha(path),
                "response_sha256": object_sha(response),
            }
            check(expected_public == public, path.name + " complete sanitized projection")
            if nxt:
                sensitive.add(nxt)
            if control:
                check(not items and not nxt, provider + " empty terminal control")
            else:
                check(number == len(pages) + 1, provider + " ordered page number")
                pages.append((aliases, nxt))
                previous = nxt
        order = [alias for page, _ in pages for alias in page]
        provider_orders[provider] = order
        check(len(pages) == 4 and all(len(page) == 1 for page, _ in pages), provider + " four singleton pages")
        check(len(order) == len(set(order)) == 4 and set(order) == set(identities), provider + " exact fixture inventory")
        check(all(token for _, token in pages[:-1]) and not pages[-1][1], provider + " final token only on fourth page")
        check(len({token for _, token in pages[:-1]}) == 3, provider + " distinct continuation tokens")

        # Independent score: locate each target and the first stop endpoint.
        # Do not import the submitted evaluate() or analyze() functions.
        for target in identities:
            position = order.index(target) + 1
            for rule in ("empty_page", "short_page", "no_match_page", "token_only", "token_and_coverage", "bounded_checked"):
                endpoint = 2 if rule == "bounded_checked" else (2 if position == 1 else 1) if rule == "no_match_page" else 4
                found = [target] if position <= endpoint else []
                remaining = endpoint < 4
                claims = rule not in ("token_and_coverage", "bounded_checked")
                independent_cases.append({
                    "provider": provider, "target": target, "rule": rule,
                    "pages_read": endpoint, "found": found,
                    "token_remaining": remaining, "coverage_status": "unknown",
                    "claims_complete": claims,
                    "result": "complete_claim" if claims else "unknown",
                    "unsupported_page_chain_claim": claims and remaining,
                    "incorrect_complete_inventory": claims and not found,
                    "false_absence": claims and not found,
                })
        for policy, endpoint in (("first_page_baseline", 1), ("token_traversal", 4), ("two_page_bound", 2)):
            actual = next(row for row in results["inventory_controls"] if row["provider"] == provider and row["policy"] == policy)
            found = sorted(order[:endpoint])
            expected = {
                "provider": provider, "policy": policy, "pages_read": endpoint,
                "found": found, "missing": sorted(set(order) - set(found)),
                "token_remaining": endpoint < 4,
                "claims_fixture_inventory_complete": policy != "two_page_bound",
                "fixture_inventory_equal": endpoint == 4,
                "result": "unknown" if policy == "two_page_bound" else "fixture_inventory_verified" if policy == "token_traversal" else "complete_claim",
                "provider_wide_coverage": "unknown",
            }
            check(actual == expected, provider + " inventory rule " + policy)
            checked_inventory_rows += 1

    by_key = lambda row: (row["provider"], row["target"], row["rule"])
    check(sorted(independent_cases, key=by_key) == sorted(results["cases"], key=by_key), "all 48 full outcome rows")
    for rule, actual in results["summaries"].items():
        rows = [row for row in independent_cases if row["rule"] == rule]
        expected = {
            "paired_local_cases": len(rows),
            "complete_claims": sum(row["claims_complete"] for row in rows),
            "unknown": sum(not row["claims_complete"] for row in rows),
            "unsupported_page_chain_claims": sum(row["unsupported_page_chain_claim"] for row in rows),
            "incorrect_complete_inventories": sum(row["incorrect_complete_inventory"] for row in rows),
            "false_absence_claims": sum(row["false_absence"] for row in rows),
            "target_found": sum(bool(row["found"]) for row in rows),
            "pages_read_total": sum(row["pages_read"] for row in rows),
        }
        check(actual == expected, "summary rule " + rule)

    # Search public files for exact native IDs, tokens, account emails, and URLs.
    for path in evidence_paths:
        text = path.read_text()
        sensitive.update(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))
        sensitive.update(re.findall(r'https?://[^\s"<>]+', text))
    for query in cfg["queries"].values():
        sensitive.update(re.findall(r"'([^']+)' in parents", json.dumps(query)))
    public_paths = [p for p in HERE.iterdir() if p.is_file() and p.suffix in (".md", ".json", ".py", ".log")]
    matches = []
    for path in public_paths:
        text = path.read_text()
        for value in sensitive:
            if value and value in text:
                matches.append(path.name)
    check(not matches, "public files contain no exact tested private values")
    result = {
        "status": "pass", "review_date": "2026-10-22",
        "checks_passed": len(checks), "check_names": checks,
        "private_records_checked": len(raw_records), "fixture_setup_receipts_checked": 8,
        "full_case_rows_checked": len(independent_cases), "inventory_rows_checked": checked_inventory_rows,
        "provider_orders": provider_orders, "sensitive_values_checked": len(sensitive),
        "public_files_scanned": len(public_paths), "sensitive_matches": 0,
        "independent_method": "target position and prefix endpoint; author code not imported",
        "reviewer_read_author_code_before_audit": True,
        "account_calls": 0, "human_review": False,
        "live_trace_sha256": sha(HERE / "live_trace.json"),
        "live_results_sha256": sha(HERE / "live_results.json"),
        "review_audit_sha256": sha(Path(__file__)),
    }
    (HERE / "review_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "checks_passed", "private_records_checked", "full_case_rows_checked", "inventory_rows_checked", "sensitive_matches")}, sort_keys=True))


if __name__ == "__main__":
    main()
