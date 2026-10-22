"""Score saved production pages. This program does not call any service."""
import argparse
import datetime
import hashlib
import json
import platform
import resource
import sys
import time
from pathlib import Path

RULES = ["empty_page", "short_page", "no_match_page", "token_only", "token_and_coverage", "bounded_checked"]


def evaluate(pages, target, rule, maximum):
    found = set()
    read = []
    for page in pages:
        read.append(page)
        found.update(a for a in page["aliases"] if a == target)
        final = page["next_token_sha256"] is None
        stop = final
        if rule == "empty_page":
            stop |= page["connector_exposed_item_count"] == 0
        if rule == "short_page":
            stop |= page["connector_exposed_item_count"] < maximum
        if rule == "no_match_page":
            stop |= target not in page["aliases"]
        if rule == "bounded_checked":
            stop |= len(read) == 2
        if stop:
            break
    last = read[-1]
    token_remaining = last["next_token_sha256"] is not None
    known_complete_coverage = all(p["coverage_status"] == "complete" for p in read)
    if rule in ["token_and_coverage", "bounded_checked"]:
        claims_complete = not token_remaining and known_complete_coverage
    else:
        claims_complete = True
    return {
        "target": target,
        "rule": rule,
        "pages_read": len(read),
        "found": sorted(found),
        "token_remaining": token_remaining,
        "coverage_status": "complete" if known_complete_coverage else "unknown",
        "claims_complete": claims_complete,
        "result": "complete_claim" if claims_complete else "unknown",
        "unsupported_page_chain_claim": claims_complete and token_remaining,
        "incorrect_complete_inventory": claims_complete and found != {target},
        "false_absence": claims_complete and not found,
    }


def analyze(trace):
    cases = []
    inventory = []
    providers = {}
    for name, value in trace["providers"].items():
        pages, targets = value["pages"], value["targets"]
        assert 0 < len(pages) <= value["page_budget"]
        assert len(set(targets)) == len(targets) == 4
        last_hash = None
        output_hashes = set()
        all_aliases = []
        for i, page in enumerate(pages, 1):
            assert page["page"] == i
            assert page["request_token_sha256"] == last_hash
            assert page["connector_exposed_item_count"] == len(page["aliases"])
            assert set(page["aliases"]) <= set(targets)
            assert page["coverage_status"] == "unknown" and not page["coverage_fields"]
            assert (page["next_token_sha256"] is not None) == (i < len(pages))
            last_hash = page["next_token_sha256"]
            if last_hash:
                assert last_hash not in output_hashes
                output_hashes.add(last_hash)
            all_aliases += page["aliases"]
        assert set(all_aliases) == set(targets), "Cannot score false absence without a complete fixture inventory"
        assert len(all_aliases) == len(set(all_aliases)), "Repeated record in chain"
        control = value["empty_control"]
        assert not control["aliases"] and control["connector_exposed_item_count"] == 0
        assert control["next_token_sha256"] is None
        assert control["request_token_sha256"] is None
        providers[name] = {
            "page_calls": len(pages),
            "pages_with_continuation": sum(p["next_token_sha256"] is not None for p in pages),
            "returned_order": all_aliases,
            "distinct_fixtures": len(set(all_aliases)),
            "duplicate_returns": len(all_aliases) - len(set(all_aliases)),
            "manifest_equal": set(all_aliases) == set(targets),
            "final_token": pages[-1]["next_token_sha256"] is None,
            "coverage_status": "unknown",
            "empty_control_calls": 1,
            "nonfinal_empty_pages": sum(not p["aliases"] and p["next_token_sha256"] is not None for p in pages),
            "nonfinal_short_pages": sum(p["connector_exposed_item_count"] < value["requested_maximum"] and p["next_token_sha256"] is not None for p in pages),
        }
        for policy, used in [("first_page_baseline", pages[:1]), ("token_traversal", pages), ("two_page_bound", pages[:2])]:
            found = set(a for p in used for a in p["aliases"])
            remaining = used[-1]["next_token_sha256"] is not None
            claims = policy != "two_page_bound"
            inventory.append({
                "provider": name,
                "policy": policy,
                "pages_read": len(used),
                "found": sorted(found),
                "missing": sorted(set(targets)-found),
                "token_remaining": remaining,
                "claims_fixture_inventory_complete": claims,
                "fixture_inventory_equal": found == set(targets),
                "result": "unknown" if policy == "two_page_bound" else "fixture_inventory_verified" if policy == "token_traversal" else "complete_claim",
                "provider_wide_coverage": "unknown",
            })
        for target in targets:
            for rule in RULES:
                cases.append(dict(provider=name, **evaluate(pages, target, rule, value["requested_maximum"])))
    summaries = {}
    for rule in RULES:
        rows = [x for x in cases if x["rule"] == rule]
        summaries[rule] = {
            "paired_local_cases": len(rows),
            "complete_claims": sum(x["claims_complete"] for x in rows),
            "unknown": sum(not x["claims_complete"] for x in rows),
            "unsupported_page_chain_claims": sum(x["unsupported_page_chain_claim"] for x in rows),
            "incorrect_complete_inventories": sum(x["incorrect_complete_inventory"] for x in rows),
            "false_absence_claims": sum(x["false_absence"] for x in rows),
            "target_found": sum(bool(x["found"]) for x in rows),
            "pages_read_total": sum(x["pages_read"] for x in rows),
        }
    return {
        "schema": 1,
        "evidence_kind": "local policy replay on two real provider page chains",
        "not_independent_trials": True,
        "providers": providers,
        "measured_provider_page_calls": sum(v["page_calls"] for v in providers.values()),
        "empty_control_calls": len(providers),
        "paired_local_target_cases": sum(len(v["targets"]) for v in trace["providers"].values()),
        "rule_outcomes": len(cases),
        "summaries": summaries,
        "inventory_controls": inventory,
        "cases": cases,
        "untested": ["nonfinal empty page", "nonfinal short page", "native incompleteSearch=true", "shared or secondary account scope", "token expiry", "changing records during traversal", "browser-agent policy adherence"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, default=Path(__file__).with_name("live_trace.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("live_results.json"))
    parser.add_argument("--execution", type=Path, default=Path(__file__).with_name("live_execution.json"))
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    wall, cpu = time.perf_counter(), time.process_time()
    data = args.trace.read_bytes()
    results = analyze(json.loads(data))
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    execution = {
        "started_at_utc": started,
        "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wall_seconds": time.perf_counter()-wall,
        "cpu_seconds": time.process_time()-cpu,
        "python": sys.version,
        "platform": platform.platform(),
        "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "trace_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "cpu_limit_seconds": 30,
        "network_calls": 0,
        "model_calls": 0,
    }
    args.execution.write_text(json.dumps(execution, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "pass", "provider_page_calls": results["measured_provider_page_calls"], "rule_outcomes": results["rule_outcomes"], "summaries": results["summaries"]}, sort_keys=True))


if __name__ == "__main__":
    main()
