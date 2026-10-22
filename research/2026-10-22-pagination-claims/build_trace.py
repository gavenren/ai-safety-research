"""Make an alias-only trace from private connector evidence. No network calls."""
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIVATE = HERE.parent / "private" / "pagination"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest() if token else None


def read_record(path, cfg, provider, kind, prior=None):
    r = json.loads(path.read_text())
    assert r["provider"] == provider and r["kind"] == kind
    assert r["tool"] == cfg["tools"][provider]
    assert not r["response"].get("isError") and "tool_exception" not in r["response"]
    assert datetime.datetime.fromisoformat(r["started_at_utc"]) > datetime.datetime.fromisoformat(cfg["frozen_at_utc"])
    body = r["response"]["structuredContent"]
    token_name = "page_token" if provider == "drive" else "next_page_token"
    expected = dict(cfg["queries" if kind == "chain" else "empty_control_queries"][provider])
    if prior is not None:
        expected[token_name] = prior["response"]["structuredContent"]["next_page_token"]
    assert r["request"] == expected, "Query or token changed"
    inverse = {i: a for a, i in cfg["target_ids"][provider].items()}
    items = body["results" if provider == "drive" else "events"]
    assert isinstance(items, list)
    assert all(x["id"] in inverse for x in items), "Unexpected identity"
    token = body.get("next_page_token")
    assert token is None or isinstance(token, str)
    coverage_fields = {k: v for k, v in body.items() if "incomplete" in k.lower() or "coverage" in k.lower()}
    assert not coverage_fields, "Review a new coverage field before use"
    public = {
        "page": r["page"],
        "started_at_utc": r["started_at_utc"],
        "finished_at_utc": r["finished_at_utc"],
        "aliases": [inverse[x["id"]] for x in items],
        "connector_exposed_item_count": len(items),
        "request_token_sha256": token_hash(r["request"].get(token_name)),
        "next_token_sha256": token_hash(token),
        "next_token_representation": "absent" if "next_page_token" not in body else "null" if token is None else "empty_string" if token == "" else "value",
        "coverage_status": "unknown",
        "coverage_fields": coverage_fields,
        "private_record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "response_sha256": digest(r["response"]),
    }
    return r, public


def main():
    cfg = json.loads((PRIVATE / "query_freeze.json").read_text())
    public_freeze = json.loads((HERE / "query_freeze.json").read_text())
    assert public_freeze["private_query_freeze_sha256"] == hashlib.sha256((PRIVATE / "query_freeze.json").read_bytes()).hexdigest()
    traces = {"schema": 1, "frozen_at_utc": cfg["frozen_at_utc"], "setup": cfg["setup"], "providers": {}}
    for provider in ["drive", "calendar"]:
        pages = []
        prior = None
        paths = sorted(PRIVATE.glob(provider + "-page-*.json"))
        assert 1 <= len(paths) <= 8
        for i, path in enumerate(paths, 1):
            prior, public = read_record(path, cfg, provider, "chain", prior)
            assert public["page"] == i
            pages.append(public)
        _, control = read_record(PRIVATE / (provider + "-empty-control.json"), cfg, provider, "empty_control")
        traces["providers"][provider] = {
            "tool": cfg["tools"][provider],
            "requested_maximum": 1,
            "page_budget": 8,
            "targets": list(cfg["target_ids"][provider]),
            "query_scope": "four run-owned direct child folders; nontrashed filter" if provider == "drive" else "primary calendar; frozen marker; 2026-10-01 to 2026-10-03; explicit Toronto offsets",
            "base_query_sha256": digest(cfg["queries"][provider]),
            "pages": pages,
            "empty_control": control,
        }
    text = json.dumps(traces, indent=2, sort_keys=True) + "\n"
    for ids in cfg["target_ids"].values():
        assert all(i not in text for i in ids.values())
    assert "@" not in text and "http" not in text
    (HERE / "live_trace.json").write_text(text)
    print(json.dumps({"providers": len(traces["providers"]), "pages": sum(len(v["pages"]) for v in traces["providers"].values()), "empty_controls": 2, "private_request_and_identity_checks": "pass"}))


if __name__ == "__main__":
    main()
