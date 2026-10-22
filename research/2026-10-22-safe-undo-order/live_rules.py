"""Pure local rules for the planned Calendar and Drive tests.

This module makes no account call and does not run a live experiment. Its
outputs are controller decisions and predicted paths, not saved website state.
The runner must verify the actual state and identity before the next action.

Rule names are fixed and have no aliases:
  gates: boolean, nonnegative_count, active_ids, lifecycle_registry
  order: fixed, greedy, complete
Gate actions are C (close) and R (release). Operation IDs are nonempty strings.
"""

from copy import deepcopy
from itertools import permutations
import json


GATE_RULES = ("boolean", "nonnegative_count", "active_ids", "lifecycle_registry")
ORDER_RULES = ("fixed", "greedy", "complete")
ALL_STATES = tuple(format(n, "03b") for n in range(8))
WITNESS_STATES = ("000", "010", "011", "101", "111")


def initial_gate_state():
    """Return a fresh JSON-friendly state with no retained operation IDs."""
    return {"flag": False, "count": 0, "active": [], "lifecycle": {}}


def _check_rule(rule):
    if rule not in GATE_RULES:
        raise ValueError(f"unknown gate rule: {rule!r}")


def _check_state(state):
    if not isinstance(state, dict) or set(state) != {
        "flag", "count", "active", "lifecycle"
    }:
        raise ValueError("gate state must contain flag, count, active, lifecycle")
    if type(state["flag"]) is not bool:
        raise ValueError("flag must be a Boolean")
    if type(state["count"]) is not int or state["count"] < 0:
        raise ValueError("count must be a nonnegative integer")
    active = state["active"]
    if not isinstance(active, list) or any(
        not isinstance(op, str) or not op for op in active
    ):
        raise ValueError("active must be a list of nonempty operation IDs")
    if len(active) != len(set(active)):
        raise ValueError("active cannot contain duplicate IDs")
    lifecycle = state["lifecycle"]
    if not isinstance(lifecycle, dict) or any(
        not isinstance(op, str) or not op or value not in ("active", "completed")
        for op, value in lifecycle.items()
    ):
        raise ValueError("lifecycle must map IDs to active or completed")


def update_gate(rule, state, action, op):
    """Return a new state after one local request; do not mutate the input.

    Only the selected rule's state component changes. The function does not
    know whether a request is repeated or whether website work is complete.
    In particular, release must follow the runner's saved-state verification.
    """
    _check_rule(rule)
    _check_state(state)
    if action not in ("C", "R"):
        raise ValueError("action must be C or R")
    if not isinstance(op, str) or not op:
        raise ValueError("op must be a nonempty string")
    new = deepcopy(state)
    if rule == "boolean":
        new["flag"] = action == "C"
    elif rule == "nonnegative_count":
        new["count"] = (
            new["count"] + 1 if action == "C" else max(0, new["count"] - 1)
        )
    elif rule == "active_ids":
        active = set(new["active"])
        if action == "C":
            active.add(op)
        else:
            active.discard(op)
        new["active"] = sorted(active)
    else:
        lifecycle = new["lifecycle"]
        if action == "C" and op not in lifecycle:
            lifecycle[op] = "active"
        elif action == "R" and lifecycle.get(op) == "active":
            lifecycle[op] = "completed"
        new["lifecycle"] = dict(sorted(lifecycle.items()))
    return new


def gate_closed(rule, state):
    """Return only the local gate decision, not a website completion claim."""
    _check_rule(rule)
    _check_state(state)
    if rule == "boolean":
        return state["flag"]
    if rule == "nonnegative_count":
        return state["count"] > 0
    if rule == "active_ids":
        return bool(state["active"])
    return "active" in state["lifecycle"].values()


def gate_probe(rule, state):
    """Return dispatch permission; no browser read is performed here."""
    closed = gate_closed(rule, state)
    return {
        "gate_closed": closed,
        "dispatch_guarded_read": not closed,
        "decision": "refuse_read" if closed else "permit_read",
        "read_executed": False,
        "live_state_verified": False,
    }


def _clear(state, field):
    index = "abc".index(field)
    if state[index] != "1":
        raise ValueError("a planned action can only clear a field that is one")
    return state[:index] + "0" + state[index + 1:]


def _path_for_order(fields):
    states = ["111"]
    for field in fields:
        states.append(_clear(states[-1], field))
    return states


def order_path(rule, valid_states, priority="bac"):
    """Return predicted states, including 111, for a fixed three-bit rule.

    Fixed ignores validity. Greedy commits the first valid remaining clear.
    Complete tests all field permutations in priority order before action.
    If complete finds no full valid path, it returns only ["111"].

    These are planned states. The runner must compare each expected state
    with a fresh, full saved-field audit before it executes the next change.
    """
    if rule not in ORDER_RULES:
        raise ValueError(f"unknown order rule: {rule!r}")
    if not isinstance(priority, str) or len(priority) != 3 or set(priority) != set("abc"):
        raise ValueError("priority must be a permutation of abc")
    if isinstance(valid_states, (str, bytes)):
        raise ValueError("valid_states must be a collection of three-bit strings")
    values = list(valid_states)
    if any(not isinstance(state, str) or state not in ALL_STATES for state in values):
        raise ValueError("each valid state must be a three-bit string")
    valid = set(values)
    if not {"111", "000"} <= valid:
        raise ValueError("valid_states must include start 111 and goal 000")
    if rule == "fixed":
        return _path_for_order(priority)
    if rule == "complete":
        for fields in permutations(priority):
            path = _path_for_order(fields)
            if all(state in valid for state in path):
                return path
        return ["111"]
    path = ["111"]
    while path[-1] != "000":
        for field in priority:
            if path[-1]["abc".index(field)] == "1":
                candidate = _clear(path[-1], field)
                if candidate in valid:
                    path.append(candidate)
                    break
        else:
            return path
    return path


def self_check():
    """Check hand-specified predictions only; this is not a live trial."""
    comparisons = 0

    def equal(actual, expected):
        nonlocal comparisons
        if actual != expected:
            raise AssertionError({"actual": actual, "expected": expected})
        comparisons += 1

    predictions = {
        "witness": {
            "fixed": ["111", "101", "001", "000"],
            "greedy": ["111", "101"],
            "complete": ["111", "011", "010", "000"],
        },
        "all_valid": {rule: ["111", "101", "001", "000"] for rule in ORDER_RULES},
    }
    for name, valid in (("witness", WITNESS_STATES), ("all_valid", ALL_STATES)):
        for rule in ORDER_RULES:
            equal(order_path(rule, valid), predictions[name][rule])
    equal(order_path("greedy", ("111", "000")), ["111"])
    equal(order_path("complete", ("111", "000")), ["111"])
    equal(order_path("fixed", ("111", "000")), ["111", "101", "001", "000"])

    schedules = {
        "G1": (("C", "A"), ("C", "B"), ("R", "A"), ("R", "A"), ("R", "B")),
        "G2": (("C", "A"), ("R", "A"), ("C", "A"), ("C", "B"), ("R", "B")),
    }
    predicted_closed = {
        "G1": {
            "boolean": [True, True, False, False, False],
            "nonnegative_count": [True, True, True, False, False],
            "active_ids": [True, True, True, True, False],
            "lifecycle_registry": [True, True, True, True, False],
        },
        "G2": {
            "boolean": [True, False, True, True, False],
            "nonnegative_count": [True, False, True, True, True],
            "active_ids": [True, False, True, True, True],
            "lifecycle_registry": [True, False, False, True, False],
        },
    }
    for name, requests in schedules.items():
        for rule in GATE_RULES:
            state = initial_gate_state()
            closed = []
            for action, op in requests:
                before = deepcopy(state)
                new = update_gate(rule, state, action, name + ":" + rule + ":" + op)
                equal(state, before)
                state = new
                closed.append(gate_closed(rule, state))
                equal(gate_probe(rule, state)["read_executed"], False)
                equal(gate_probe(rule, state)["dispatch_guarded_read"], not closed[-1])
                equal(json.loads(json.dumps(state)), state)
            equal(closed, predicted_closed[name][rule])

    # Retained completion must survive both late request types. Unknown
    # release does not create a completed entry in the declared registry.
    state = update_gate("lifecycle_registry", initial_gate_state(), "R", "absent")
    equal(state["lifecycle"], {})
    state = update_gate("lifecycle_registry", state, "C", "retained")
    state = update_gate("lifecycle_registry", state, "R", "retained")
    done = deepcopy(state)
    equal(update_gate("lifecycle_registry", state, "C", "retained"), done)
    equal(update_gate("lifecycle_registry", state, "R", "retained"), done)
    equal(update_gate("nonnegative_count", initial_gate_state(), "R", "absent")["count"], 0)
    return {
        "kind": "local_logic_self_check",
        "live_experiment": False,
        "account_calls": 0,
        "passed": True,
        "comparisons": comparisons,
        "predicted_order_paths": predictions,
        "predicted_gate_closed": predicted_closed,
    }


if __name__ == "__main__":
    print(json.dumps(self_check(), indent=2, sort_keys=True))
