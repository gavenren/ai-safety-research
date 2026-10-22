"""Pure local rules for the proposed browser trials.

This module has no account, browser, file, clock, or network calls. Import does
not run a trial or a self-check. Call self_checks() explicitly for local checks.
No result from this module proves that a provider saved a field. The caller
must supply the saved-state evidence required by the frozen study plan.

Canonical JSON here means Python JSON with sorted string keys, compact
separators, UTF-8, no NaN or infinity, and no Unicode or whitespace changes.
It is not an implementation of RFC 8785. Numbers 1 and 1.0 remain distinct.
"""

import hashlib
import json
import math
from typing import Any, Dict


IMMUTABLE_FIELDS = (
    "service",
    "account_alias",
    "operation_id",
    "target",
    "action",
    "payload",
)
RULES = ("key_only", "bound")


def _check_json(value: Any) -> None:
    """Reject values that cannot keep an exact JSON representation."""
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _check_json(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("JSON object keys must be strings")
            _check_json(item)
        return
    raise TypeError("Use plain JSON values and finite numbers only")


def canonical_json(value: Any) -> str:
    """Return deterministic JSON without changing string content."""
    _check_json(value)
    text = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    )
    text.encode("utf-8")  # Reject unpaired surrogate characters.
    return text


def envelope_hash(envelope: Dict[str, Any]) -> str:
    """Hash the complete envelope, including any evidence or metadata fields.

    This hash checks content integrity. It does not check account truth,
    authenticity, freshness, or the correctness of an evidence field.
    Do not put this digest inside the envelope before hashing that envelope.
    """
    if type(envelope) is not dict:
        raise TypeError("The envelope must be a plain JSON object")
    return hashlib.sha256(canonical_json(envelope).encode("utf-8")).hexdigest()


def check_generation(command_generation: Any, current_generation: Any,
                     active: Any) -> bool:
    """Allow only an active, equal, nonnegative integer generation.

    A caller must read current_generation and active from the same current
    local ledger state. True is not accepted as integer generation 1.
    This is a local decision, not an atomic check at a provider's commit.
    """
    return (
        type(command_generation) is int
        and type(current_generation) is int
        and command_generation >= 0
        and current_generation >= 0
        and active is True
        and command_generation == current_generation
    )


def _envelope_is_valid(envelope: Any) -> bool:
    if type(envelope) is not dict:
        return False
    if any(field not in envelope for field in IMMUTABLE_FIELDS):
        return False
    # Native target IDs and all other identity fields are opaque strings.
    # Do not trim them. Payload can contain any strict JSON value.
    if any(type(envelope[field]) is not str or not envelope[field]
           for field in IMMUTABLE_FIELDS[:-1]):
        return False
    try:
        canonical_json(envelope)
    except (TypeError, ValueError, RecursionError, UnicodeError):
        return False
    return True


def _result(status: str, reason: str, mismatched_fields=()) -> Dict[str, Any]:
    """Every receipt decision has the same JSON-compatible result fields."""
    return {
        "status": status,
        "reason": reason,
        "replay": status == "success",
        "dispatch": False,
        "mismatched_fields": list(mismatched_fields),
    }


def receipt_decision(rule: str, stored_envelope: Any, new_envelope: Any,
                     evidence_complete: bool = True) -> Dict[str, Any]:
    """Decide whether one stored local receipt can answer this request.

    Rules:
      key_only: compare only operation_id after common validity/evidence gates.
                This deliberately weak rule can return an incorrect success.
      bound: require equality of the six IMMUTABLE_FIELDS. Extra metadata does
             not change the intended operation and is not used for binding.

    Outcomes:
      success: replay this local receipt; do not send a second mutation.
      conflict: same operation ID but a different immutable field under bound.
      unknown: invalid input, incomplete evidence, or another operation ID.

    All outcomes set dispatch=False. A new operation needs its own admission
    path, which this receipt-reuse helper does not implement. Mismatch fields
    describe the binding failure, not a comparison with a live website.

    evidence_complete=True is a caller assertion, not a check done here. The
    caller must explicitly supply it from the frozen evidence checks. If it
    is False, neither policy can claim success. The default is part of the
    requested function interface; production trial calls should not omit it.
    """
    if rule not in RULES:
        return _result("unknown", "unsupported_rule")
    if not _envelope_is_valid(stored_envelope):
        return _result("unknown", "invalid_stored_envelope")
    if not _envelope_is_valid(new_envelope):
        return _result("unknown", "invalid_new_envelope")
    if evidence_complete is not True:
        return _result("unknown", "incomplete_evidence")
    if stored_envelope["operation_id"] != new_envelope["operation_id"]:
        return _result("unknown", "receipt_for_other_operation", ("operation_id",))
    if rule == "key_only":
        return _result("success", "key_only_replay")
    mismatches = [
        field for field in IMMUTABLE_FIELDS
        if canonical_json(stored_envelope[field])
        != canonical_json(new_envelope[field])
    ]
    if mismatches:
        return _result("conflict", "immutable_fields_changed", mismatches)
    return _result("success", "bound_replay")


def self_checks() -> Dict[str, Any]:
    """Run small, pure local checks when the caller explicitly requests them.

    These checks use synthetic values only. They make no live trial claims.
    The function raises AssertionError on failure, even under python -O.
    """
    count = 0

    def require(condition: bool, name: str) -> None:
        nonlocal count
        count += 1
        if not condition:
            raise AssertionError(name)

    require(check_generation(0, 0, True), "valid old generation")
    require(not check_generation(0, 1, True), "retired generation")
    require(not check_generation(0, 0, False), "inactive generation")
    require(check_generation(1, 1, True), "valid new generation")
    require(not check_generation(True, 1, True), "Boolean is not generation")
    require(not check_generation(-1, -1, True), "negative generation")
    require(not check_generation(0, 0, 1), "integer is not active Boolean")

    base = {
        "service": "test-service",
        "account_alias": "account-A",
        "operation_id": "operation-A",
        "target": "record-A",
        "action": "set-fields",
        "payload": {"description": "PAYLOAD-A"},
        "evidence": {"source": "synthetic-only"},
    }
    original = canonical_json(base)
    changed_payload = dict(base, payload={"description": "PAYLOAD-B"})
    changed_target = dict(base, target="record-B")
    require(receipt_decision("bound", base, base, True)
            == _result("success", "bound_replay"), "exact bound repeat")
    for field, modified in (("payload", changed_payload), ("target", changed_target)):
        require(receipt_decision("key_only", base, modified, True)
                == _result("success", "key_only_replay"), "weak replay " + field)
        require(receipt_decision("bound", base, modified, True)
                == _result("conflict", "immutable_fields_changed", (field,)),
                "bound conflict " + field)
    for field in ("service", "account_alias", "action"):
        modified = dict(base, **{field: "changed"})
        require(receipt_decision("bound", base, modified, True)
                == _result("conflict", "immutable_fields_changed", (field,)),
                "bound identity field " + field)
    for rule in RULES:
        require(receipt_decision(rule, base, base, False)["status"] == "unknown",
                "missing evidence " + rule)
        require(receipt_decision(rule, base, dict(base, operation_id="new"), True)
                == _result("unknown", "receipt_for_other_operation", ("operation_id",)),
                "different operation " + rule)
    require(receipt_decision("bound", base, {}, True)["status"] == "unknown",
            "missing envelope fields")
    require(receipt_decision("bound", None, base, True)["status"] == "unknown",
            "absent stored receipt")
    require(receipt_decision("unsupported", base, base, True)["status"] == "unknown",
            "unknown rule")
    require(receipt_decision("bound", dict(base, payload={"x": 1}),
                             dict(base, payload={"x": True}), True)["status"] == "conflict",
            "typed payload comparison")
    require(receipt_decision("bound", base, dict(base, payload=float("nan")), True)
            ["status"] == "unknown", "non-finite payload")
    extra_evidence = dict(base, evidence={"source": "another-synthetic-read"})
    require(receipt_decision("bound", base, extra_evidence, True)["status"] == "success",
            "mutable evidence is not intent")
    require(envelope_hash(base) == envelope_hash(dict(reversed(list(base.items())))),
            "canonical key order")
    require(envelope_hash(base) != envelope_hash(extra_evidence), "full envelope hash")
    require(canonical_json(base) == original, "inputs not mutated")
    return {"status": "pass", "checks": count, "scope": "pure local synthetic checks"}
