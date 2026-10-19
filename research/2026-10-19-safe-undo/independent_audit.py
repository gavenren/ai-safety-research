"""Independent exact audit from the frozen study plan.

This file does not import the main analysis or its tests. It uses only Python's
standard library. All model values are synthetic. No random number is used.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import itertools
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED = {
    "initial_x": [0, 1],
    "initial_y": [0, 1],
    "lengths": [0, 1, 2, 3, 4, 5],
    "alphabet": ["add1", "sub1", "set0", "set1", "flip_y"],
    "rules": ["full_restore", "field_restore", "subtract", "value_guard",
              "revision_guard", "provenance"],
    "primary_length": 3,
    "agent_increment": 1,
}
FLAGS = ["correct_final", "false_confirmation", "wrong_change",
         "collateral_change", "new_damage", "unresolved", "abstain_correct",
         "clean_completion", "changed", "abstain"]
FAILURE_FLAGS = ["false_confirmation", "wrong_change", "collateral_change",
                 "new_damage", "unresolved", "abstain_correct"]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_config(config):
    """Accept the exact frozen corpus, with strict JSON-compatible types."""
    if type(config) is not dict or set(config) != set(EXPECTED):
        raise ValueError("Config keys differ from the frozen corpus.")
    for key, wanted in EXPECTED.items():
        value = config[key]
        if type(value) is not type(wanted):
            raise ValueError("Wrong type for " + key)
        if type(value) is list:
            if len(value) != len(wanted):
                raise ValueError("Wrong list length for " + key)
            if any(type(v) is not type(w) for v, w in zip(value, wanted)):
                raise ValueError("Wrong list element type for " + key)
        if value != wanted:
            raise ValueError("Value differs from the frozen corpus: " + key)


def load_inputs(root):
    config = json.loads((root / "config.json").read_text())
    validate_config(config)
    manifest = json.loads((root / "input_manifest.json").read_text())
    if set(manifest.get("files", {})) != {"analysis_plan.md", "config.json"}:
        raise ValueError("Unexpected manifest files.")
    actual_hashes = {}
    for name, wanted in manifest["files"].items():
        value = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if value != wanted:
            raise ValueError("Frozen input hash does not match: " + name)
        actual_hashes[name] = value
    return config, {"frozen_utc": manifest["frozen_utc"], "sha256": actual_hashes}


def actual_world(initial, word):
    """Execute the agent first, then the fixed background commands."""
    x, y = initial
    x += 1
    revision = 0
    survives = True
    trace = [{"x": x, "y": y, "x_revision": revision,
              "agent_contribution_survives": survives}]
    for command in word:
        if command == "add1":
            x += 1
        elif command == "sub1":
            x -= 1
        elif command == "set0":
            x = 0
            survives = False
        elif command == "set1":
            x = 1
            survives = False
        elif command == "flip_y":
            y = 1 - y
        else:
            raise ValueError("Unknown command.")
        revision += command != "flip_y"
        trace.append({"x": x, "y": y, "x_revision": revision,
                      "agent_contribution_survives": survives})
    return trace


def counterfactual_world(initial, word):
    """Replay each fixed command without the agent, via separate transforms.

    This code does not call the actual-world mutation code. The tuple functions
    give the reference semantics directly, including assignment of the current
    value. The initial state is the first entry.
    """
    command_functions = {
        "add1": lambda a, b: (a + 1, b),
        "sub1": lambda a, b: (a - 1, b),
        "set0": lambda a, b: (0, b),
        "set1": lambda a, b: (1, b),
        "flip_y": lambda a, b: (a, b ^ 1),
    }
    state = tuple(initial)
    trace = [{"x": state[0], "y": state[1]}]
    for command in word:
        state = command_functions[command](*state)
        trace.append({"x": state[0], "y": state[1]})
    return trace


def outcome(rule, initial, before, target, revision, survives):
    """Rules cannot use target; only the outcome labels inspect it."""
    ix, iy = initial
    bx, by = before
    complete = True
    if rule == "full_restore":
        after = (ix, iy)
    elif rule == "field_restore":
        after = (ix, by)
    elif rule == "subtract":
        after = (bx - 1, by)
    elif rule == "value_guard":
        complete = bx == ix + 1
        after = (ix, by) if complete else before
    elif rule == "revision_guard":
        complete = revision == 0
        after = (ix, by) if complete else before
    elif rule == "provenance":
        after = (bx - 1, by) if survives else before
    else:
        raise ValueError("Unknown rule.")
    correct = after == target
    changed = after != before
    return {
        "status": "complete" if complete else "abstain",
        "final": {"x": after[0], "y": after[1]},
        "correct_final": correct,
        "false_confirmation": complete and not correct,
        "wrong_change": changed and not correct,
        "collateral_change": after[1] != by,
        "new_damage": before == target and not correct,
        "unresolved": not complete and not correct,
        "abstain_correct": not complete and correct,
        "clean_completion": complete and correct,
        "changed": changed,
        "abstain": not complete,
    }


def make_case(length, ix, iy, indices, alphabet, rules):
    initial = (ix, iy)
    word = [alphabet[index] for index in indices]
    actual = actual_world(initial, word)
    reference = counterfactual_world(initial, word)
    last = actual[-1]
    before = (last["x"], last["y"])
    target = (reference[-1]["x"], reference[-1]["y"])
    has_set = any(command.startswith("set") for command in word)
    case_id = f"{length}:{ix}:{iy}:" + ".".join(map(str, indices))
    results = {
        rule: outcome(rule, initial, before, target, last["x_revision"],
                      last["agent_contribution_survives"])
        for rule in rules
    }
    return {
        "case_id": case_id,
        "length": length,
        "initial": {"x": ix, "y": iy},
        "word_indices": list(indices),
        "word": word,
        "actual_trajectory": actual,
        "reference_trajectory": reference,
        "pre_undo": {"x": before[0], "y": before[1]},
        "target": {"x": target[0], "y": target[1]},
        "x_revision": last["x_revision"],
        "agent_contribution_survives": last["agent_contribution_survives"],
        "has_set": has_set,
        "outcomes": results,
    }


def handcrafted_checks():
    names = []
    # Each command has a direct expected trajectory, independently specified.
    reference = {
        "add1": [(1, 0), (2, 0)],
        "sub1": [(1, 0), (0, 0)],
        "set0": [(1, 0), (0, 0)],
        "set1": [(1, 0), (1, 0)],
        "flip_y": [(1, 0), (1, 1)],
    }
    for command, expected in reference.items():
        ref = counterfactual_world((1, 0), [command])
        require([(s["x"], s["y"]) for s in ref] == expected,
                "Hand reference command: " + command)
        actual = actual_world((1, 0), [command])
        expected_end = {"add1": (3, 0), "sub1": (1, 0), "set0": (0, 0),
                        "set1": (1, 0), "flip_y": (2, 1)}[command]
        require((actual[-1]["x"], actual[-1]["y"]) == expected_end,
                "Hand actual command: " + command)
        require(actual[-1]["x_revision"] == (command != "flip_y"),
                "Hand revision command: " + command)
        names.append("one_command_" + command)
    for ix, iy in itertools.product([0, 1], repeat=2):
        case = make_case(0, ix, iy, (), EXPECTED["alphabet"], EXPECTED["rules"])
        require(all(v["clean_completion"] for v in case["outcomes"].values()),
                "No background must complete cleanly.")
    names.append("all_four_no_background_records")
    same = actual_world((0, 0), ["set1"])
    require(same[-1]["x"] == same[0]["x"] == 1
            and same[-1]["x_revision"] == 1
            and not same[-1]["agent_contribution_survives"],
            "Same-value assignment must increment revision and clear provenance.")
    names.append("same_value_assignment")
    cancel = make_case(2, 0, 0, (0, 1), EXPECTED["alphabet"], EXPECTED["rules"])
    require(cancel["target"] == {"x": 0, "y": 0}
            and cancel["x_revision"] == 2
            and cancel["outcomes"]["value_guard"]["clean_completion"]
            and cancel["outcomes"]["revision_guard"]["unresolved"],
            "Add-sub cancellation.")
    names.append("add_sub_cancellation")
    assigned = make_case(2, 0, 0, (2, 0), EXPECTED["alphabet"], EXPECTED["rules"])
    require(assigned["target"] == assigned["pre_undo"] == {"x": 1, "y": 0}
            and assigned["outcomes"]["value_guard"]["new_damage"]
            and assigned["outcomes"]["provenance"]["clean_completion"],
            "Assignment followed by an addition.")
    names.append("set_then_add")
    for length in EXPECTED["lengths"]:
        case = make_case(length, 0, 0, (4,) * length,
                         EXPECTED["alphabet"], EXPECTED["rules"])
        require(case["x_revision"] == 0, "Y-only revision.")
        require(all(case["outcomes"][r]["clean_completion"]
                    for r in EXPECTED["rules"] if r != "full_restore"),
                "Y-only field preservation.")
        require(case["outcomes"]["full_restore"]["collateral_change"]
                == bool(length % 2), "Y-only full restore parity.")
    names.append("all_y_only_lengths")
    return names


def malformed_checks():
    wrong_inputs = []
    for key in EXPECTED:
        bad = copy.deepcopy(EXPECTED)
        del bad[key]
        wrong_inputs.append(("missing_" + key, bad))
        bad = copy.deepcopy(EXPECTED)
        bad[key] = None
        wrong_inputs.append(("null_" + key, bad))
    modifications = [
        ("initial_x", [False, 1]), ("initial_y", [0, True]),
        ("initial_x", [0, 2]), ("initial_y", [0]),
        ("lengths", [0, 1, 2, 3, 4, 6]),
        ("lengths", [False, 1, 2, 3, 4, 5]),
        ("lengths", [0, 1, 2, 3, 4, 4]),
        ("alphabet", list(reversed(EXPECTED["alphabet"]))),
        ("alphabet", EXPECTED["alphabet"] + ["add1"]),
        ("rules", list(reversed(EXPECTED["rules"]))),
        ("rules", EXPECTED["rules"][:-1]),
        ("agent_increment", True), ("agent_increment", 0),
        ("agent_increment", 1.0), ("primary_length", 4),
        ("primary_length", "3"),
    ]
    for index, (key, value) in enumerate(modifications):
        bad = copy.deepcopy(EXPECTED)
        bad[key] = value
        wrong_inputs.append((f"bad_value_{index}_{key}", bad))
    bad = copy.deepcopy(EXPECTED)
    bad["extra"] = 1
    wrong_inputs.extend([("extra_key", bad), ("top_list", []),
                         ("top_null", None)])
    for name, config in wrong_inputs:
        try:
            validate_config(config)
        except ValueError:
            continue
        raise AssertionError("Malformed config was accepted: " + name)
    return [name for name, _ in wrong_inputs]


def case_controls(case):
    seen_set = False
    revision = 0
    for i, (actual, reference) in enumerate(zip(case["actual_trajectory"],
                                              case["reference_trajectory"])):
        if i:
            command = case["word"][i - 1]
            seen_set |= command.startswith("set")
            revision += command != "flip_y"
        require(actual["y"] == reference["y"], "Worlds must agree on y.")
        require(actual["x"] - reference["x"] == (0 if seen_set else 1),
                "Agent contribution invariant.")
        require(actual["x_revision"] == revision, "Revision count invariant.")
        require(actual["agent_contribution_survives"] == (not seen_set),
                "Provenance invariant.")
    for rule, result in case["outcomes"].items():
        require(sum(result[k] for k in ("clean_completion", "false_confirmation",
                                       "unresolved", "abstain_correct")) == 1,
                "Outcome partition: " + rule)
        if rule != "full_restore":
            require(result["final"]["y"] == case["pre_undo"]["y"],
                    "Rule preserves y: " + rule)
        if result["abstain"]:
            require(result["final"] == case["pre_undo"], "Abstention changes state.")
    require(case["outcomes"]["subtract"]["correct_final"] == (not case["has_set"]),
            "Subtract correctness condition.")
    require(case["outcomes"]["provenance"]["clean_completion"],
            "Provenance result.")
    guard = case["outcomes"]["value_guard"]
    require(guard["false_confirmation"] == guard["new_damage"]
            == guard["wrong_change"], "Value guard failure condition.")


def run(config):
    rules = config["rules"]
    cases = []
    aggregates = defaultdict(Counter)
    pairs = defaultdict(Counter)
    group_cases = defaultdict(list)
    first_failures = {rule: {} for rule in rules}
    for length in config["lengths"]:
        for ix, iy in itertools.product(config["initial_x"], config["initial_y"]):
            for indices in itertools.product(range(len(config["alphabet"])), repeat=length):
                case = make_case(length, ix, iy, indices, config["alphabet"], rules)
                case_controls(case)
                cases.append(case)
                subgroup = "with_set" if case["has_set"] else "no_set"
                for rule, result in case["outcomes"].items():
                    for group in ("all", subgroup):
                        aggregate = aggregates[(length, group, rule)]
                        aggregate["cases"] += 1
                        aggregate.update({key: int(result[key]) for key in FLAGS})
                    for label in FAILURE_FLAGS:
                        if result[label] and label not in first_failures[rule]:
                            first_failures[rule][label] = case["case_id"]
                    if rule != "provenance":
                        for group in ("all", subgroup):
                            pair = pairs[(length, group, rule)]
                            pair["cases"] += 1
                            pre_correct = case["pre_undo"] == case["target"]
                            pair["abstain_pre_correct"] += int(result["abstain"] and pre_correct)
                            pair["abstain_pre_wrong"] += int(result["abstain"] and not pre_correct)
                            pair["abstain_total"] += int(result["abstain"])
                key = (length, ix, iy, case["pre_undo"]["x"], case["pre_undo"]["y"],
                       case["x_revision"])
                group_cases[key].append(case)
    # Include zero-count with-set groups at L=0 as explicit table rows.
    rows = []
    pair_rows = []
    for length in config["lengths"]:
        for group in ("all", "no_set", "with_set"):
            for rule in rules:
                c = aggregates[(length, group, rule)]
                rows.append({"length": length, "subgroup": group, "rule": rule,
                             **{k: c[k] for k in ["cases", *FLAGS]}})
                if rule != "provenance":
                    p = pairs[(length, group, rule)]
                    pair_rows.append({"length": length, "subgroup": group, "rule": rule,
                                      **{k: p[k] for k in ["cases", "abstain_pre_correct",
                                                         "abstain_pre_wrong", "abstain_total"]}})
    groups = []
    minimum_pairs = []
    by_id = {case["case_id"]: case for case in cases}
    order = {case["case_id"]: i for i, case in enumerate(cases)}
    for key, members in sorted(group_cases.items()):
        targets = Counter((m["target"]["x"], m["target"]["y"]) for m in members)
        first = members[0]
        second = next((m for m in members if m["target"] != first["target"]), None)
        pair = [first["case_id"], second["case_id"]] if second else None
        row = {"observation": list(key), "cases": len(members),
               "target_counts": [{"target": {"x": x, "y": y}, "count": count}
                                 for (x, y), count in sorted(targets.items())],
               "ambiguous": len(targets) > 1,
               "first_case_id": first["case_id"], "minimum_pair": pair}
        groups.append(row)
        if pair:
            minimum_pairs.append(pair)
    minimum_pairs.sort(key=lambda pair: (order[pair[0]], order[pair[1]]))
    totals = {rule: {k: sum(aggregates[(length, "all", rule)][k]
                           for length in config["lengths"])
                     for k in ["cases", *FLAGS]} for rule in rules}
    length_checks = []
    for length in config["lengths"]:
        n, no_set = 4 * 5 ** length, 4 * 3 ** length
        with_set = n - no_set
        a = lambda rule: aggregates[(length, "all", rule)]
        require(a("provenance")["cases"] == n, "Corpus size.")
        require(aggregates[(length, "no_set", "provenance")]["cases"] == no_set,
                "No-set count.")
        require(a("full_restore")["collateral_change"] == 2 * (5 ** length - 3 ** length),
                "Y-parity count.")
        require(a("subtract")["clean_completion"] == no_set
                and a("subtract")["false_confirmation"] == with_set
                and a("subtract")["new_damage"] == with_set,
                "Subtract count.")
        require(a("revision_guard")["clean_completion"] == 4
                and a("revision_guard")["abstain_correct"] == with_set
                and a("revision_guard")["unresolved"] == no_set - 4
                and a("revision_guard")["false_confirmation"] == 0,
                "Revision guard counts.")
        require(a("provenance")["clean_completion"] == n
                and a("provenance")["changed"] == no_set,
                "Provenance counts.")
        length_checks.append({"length": length, "cases": n, "no_set": no_set,
                              "with_set": with_set, "status": "PASS"})
    hypotheses = {
        "H1": totals["full_restore"]["false_confirmation"] > 0
              and totals["field_restore"]["false_confirmation"] > 0
              and totals["full_restore"]["collateral_change"] > 0,
        "H2": all(c["outcomes"]["subtract"]["correct_final"] == (not c["has_set"])
                  for c in cases),
        "H3": totals["value_guard"]["false_confirmation"] > 0
              and totals["value_guard"]["new_damage"] > 0,
        "H4": totals["revision_guard"]["false_confirmation"] == 0
              and totals["revision_guard"]["wrong_change"] == 0
              and totals["revision_guard"]["abstain"] > 0,
        "H5": totals["provenance"]["clean_completion"] == len(cases),
        "H6": bool(minimum_pairs),
    }
    minimum_failure_cases = {
        rule: {label: by_id[case_id] for label, case_id in labels.items()}
        for rule, labels in first_failures.items()
    }
    data = {
        "schema": "independent_safe_undo_v1",
        "case_count": len(cases), "policy_count": len(cases) * len(rules),
        "case_file": "independent_cases.jsonl.gz",
        "case_order": "length, initial x, initial y, word index tuple",
        "aggregates": rows, "paired_counts": pair_rows,
        "totals": totals, "observation_groups": groups,
        "ambiguous_group_count": len(minimum_pairs),
        "observation_group_count": len(groups),
        "minimum_failure_cases": minimum_failure_cases,
        "global_minimum_ambiguity_pair": [by_id[i] for i in minimum_pairs[0]],
        "hypotheses": hypotheses, "count_identities": length_checks,
    }
    return cases, data


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    config, frozen = load_inputs(args.input_dir)
    hand = handcrafted_checks()
    malformed = malformed_checks()
    cases, results = run(config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw = b"".join((json.dumps(case, separators=(",", ":"), sort_keys=True) + "\n").encode()
                   for case in cases)
    (args.output_dir / "independent_cases.jsonl.gz").write_bytes(gzip.compress(raw, mtime=0))
    write_json(args.output_dir / "independent_results.json", results)
    checks = {
        "status": "PASS", "input": frozen,
        "implementation": "Independent model; no imports from main analysis or tests.",
        "reference": "Separate tuple transforms; no agent increment.",
        "python": platform.python_version(),
        "randomness": "None; exact enumeration.",
        "human_review": "None",
        "handcrafted_control_groups": hand,
        "handcrafted_control_group_count": len(hand),
        "malformed_config_count": len(malformed),
        "malformed_config_cases": malformed,
        "case_count": len(cases), "policy_count": results["policy_count"],
        "trajectory_state_pairs": sum(len(case["actual_trajectory"]) for case in cases),
        "aggregate_rows": len(results["aggregates"]),
        "paired_rows": len(results["paired_counts"]),
        "observation_groups": results["observation_group_count"],
        "ambiguous_groups": results["ambiguous_group_count"],
        "hypotheses": results["hypotheses"],
        "sha256": {name: hashlib.sha256((args.output_dir / name).read_bytes()).hexdigest()
                   for name in ("independent_cases.jsonl.gz", "independent_results.json")},
    }
    write_json(args.output_dir / "independent_checks.json", checks)
    print(json.dumps({key: checks[key] for key in ("status", "case_count", "policy_count",
                                                "trajectory_state_pairs", "aggregate_rows",
                                                "paired_rows", "observation_groups",
                                                "ambiguous_groups")}, sort_keys=True))


if __name__ == "__main__":
    main()
