"""Exact finite undo study. Uses only the Python standard library."""
import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMANDS = ("add1", "sub1", "set0", "set1", "flip_y")
RULES = ("visible", "replay", "no_loss", "agreement", "oracle")


def run(state, word):
    x, y = state
    for cmd in word:
        if cmd == "add1":
            x += 1
        elif cmd == "sub1":
            x -= 1
        elif cmd == "set0":
            x = 0
        elif cmd == "set1":
            x = 1
        elif cmd == "flip_y":
            y = 1 - y
        else:
            raise ValueError("unknown command")
    return (x, y)


def retained(word, mask):
    return tuple(c for i, c in enumerate(word) if mask & (1 << i))


def build_index(max_length):
    """Index complete words by each distinct subsequence and observed state."""
    index = defaultdict(lambda: defaultdict(list))
    for initial in itertools.product((0, 1), repeat=2):
        agent = (initial[0] + 1, initial[1])
        for length in range(max_length + 1):
            for word in itertools.product(COMMANDS, repeat=length):
                current, target = run(agent, word), run(initial, word)
                subsequences = {retained(word, mask) for mask in range(1 << length)}
                for visible in subsequences:
                    key = (initial, current, visible)
                    index[key][length - len(visible)].append((word, target))
    return index


def candidate_set(index, initial, current, visible, bound):
    if type(bound) is not int or bound < 0:
        raise ValueError("bound must be a nonnegative integer")
    if any(c not in COMMANDS for c in visible):
        raise ValueError("unknown visible command")
    if len(visible) + bound > 5:
        raise ValueError("query exceeds the model's candidate length")
    buckets = index.get((initial, current, visible), {})
    return tuple(item for k in range(bound + 1) for item in buckets.get(k, ()))


def decide(initial, current, visible, bound, targets):
    """No true word, loss count, deletion mask, or evaluator target is an input."""
    proposal = current if any(c in ("set0", "set1") for c in visible) else (current[0] - 1, current[1])
    replay_ok = run((initial[0] + 1, initial[1]), visible) == current
    out = {}
    for name in RULES[:-1]:
        if name == "visible":
            claim, final, reason = True, proposal, "visible_commands"
        elif name == "replay":
            claim = replay_ok
            final, reason = (proposal, "replay_match") if claim else (current, "replay_mismatch")
        elif name == "no_loss":
            claim = bound == 0 and replay_ok
            final = run(initial, visible) if claim else current
            reason = "no_loss_and_match" if claim else "possible_loss_or_mismatch"
        else:
            claim = len(targets) == 1
            final = targets[0] if claim else current
            reason = "one_target" if claim else ("no_candidates" if not targets else "multiple_targets")
        out[name] = {"claim": claim, "final": list(final), "reason": reason}
    return out


def outcome(claim, final, target):
    correct = tuple(final) == tuple(target)
    return ("correct_completion" if correct else "false_completion") if claim else (
        "refusal_correct_state" if correct else "refusal_incorrect_state"
    )


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def line(f, obj):
    f.write(json.dumps(obj, separators=(",", ":"), sort_keys=True) + "\n")


def main(outdir):
    config = json.loads((HERE / "config.json").read_text())
    assert tuple(config["commands"]) == COMMANDS
    assert config["max_actual_length"] == 4 and config["candidate_max_length"] == 5
    assert config["initial_x"] == [0, 1] and config["initial_y"] == [0, 1]
    assert config["bound_settings"] == ["tight", "loose", "false"] and config["seed"] is None
    outdir.mkdir(parents=True, exist_ok=True)
    index = build_index(5)
    queries, observations = {}, []
    summary = defaultdict(Counter)
    obs_by_setting = defaultdict(set)
    witnesses = {}
    checks = Counter()

    def query(initial, current, visible, bound):
        key = (initial, current, visible, bound)
        if key not in queries:
            candidates = candidate_set(index, initial, current, visible, bound)
            targets = tuple(sorted({t for _, t in candidates}))
            record = {"observation_id": len(observations) + 1,
                      "initial": initial, "current": current, "visible": visible,
                      "bound": bound, "candidate_count": len(candidates),
                      "targets": targets, "decisions": decide(initial, current, visible, bound, targets)}
            observations.append(record)
            queries[key] = (record, frozenset(w for w, _ in candidates), candidates)
        return queries[key]

    with (outdir / "cases.jsonl").open("w") as casefile:
        case_id = 0
        for initial in itertools.product((0, 1), repeat=2):
            agent = (initial[0] + 1, initial[1])
            for length in range(5):
                for word in itertools.product(COMMANDS, repeat=length):
                    current, target = run(agent, word), run(initial, word)
                    for mask in range(1 << length):
                        case_id += 1
                        visible = retained(word, mask)
                        missing = length - len(visible)
                        case = dict(case_id=case_id, initial=initial, word=word, mask=mask,
                                    visible=visible, current=current, target=target, missing=missing)
                        line(casefile, case)
                        settings = [("tight", missing), ("loose", missing + 1)]
                        if missing:
                            settings.append(("false", missing - 1))
                        tight_targets = None
                        for setting, bound in settings:
                            rec, members, candidates = query(initial, current, visible, bound)
                            targets = set(rec["targets"])
                            obs_by_setting[setting].add(rec["observation_id"])
                            if setting != "false":
                                assert word in members and target in targets and candidates
                                checks["honest_inclusion"] += 1
                                assert all(t[1] == current[1] for t in targets)
                                checks["candidate_y_preservation"] += 1
                            if setting == "tight":
                                tight_targets = targets
                            if setting == "loose":
                                assert tight_targets <= targets
                                if len(targets) == 1:
                                    assert tight_targets == targets
                                checks["bound_monotonicity"] += 1
                            if bound == 0:
                                assert rec["decisions"]["agreement"]["claim"] == rec["decisions"]["no_loss"]["claim"]
                                assert rec["decisions"]["agreement"]["final"] == rec["decisions"]["no_loss"]["final"]
                                checks["zero_bound_equivalence"] += 1
                            scopes = ["all", f"L{length}", f"missing{missing}"]
                            if length == 4 and missing > 0:
                                scopes.append("L4_missing")
                            decisions = dict(rec["decisions"])
                            decisions["oracle"] = {"claim": True, "final": run(initial, word)}
                            for rule, dec in decisions.items():
                                score = outcome(dec["claim"], dec["final"], target)
                                for scope in scopes:
                                    summary[(setting, scope, rule)][score] += 1
                                if rule == "agreement" and setting != "false" and dec["claim"]:
                                    assert score == "correct_completion"
                                    checks["honest_completion"] += 1
                                tag = None
                                if setting == "tight" and rule == "agreement" and missing and dec["claim"]:
                                    tag = "safe_missing"
                                elif setting == "tight" and rule == "replay" and score == "false_completion":
                                    tag = "replay_false"
                                elif setting == "false" and rule == "agreement" and score == "false_completion":
                                    tag = "false_bound"
                                if tag and tag not in witnesses:
                                    witnesses[tag] = dict(case=case, observation=rec, setting=setting, rule=rule, outcome=score)
                            if setting == "tight" and len(candidates) > 1 and len(targets) == 1:
                                if "multiple_histories_one_target" not in witnesses:
                                    witnesses["multiple_histories_one_target"] = dict(case=case, observation=rec,
                                        candidates=[dict(word=w, target=t) for w, t in candidates[:2]])
                            if setting == "tight" and len(targets) > 1 and "ambiguous" not in witnesses:
                                pair = [next(dict(word=w, target=t) for w, t in candidates if t == wanted)
                                        for wanted in sorted(targets)[:2]]
                                witnesses["ambiguous"] = dict(case=case, observation=rec, candidates=pair)

    assert case_id == 44444
    with (outdir / "decisions.jsonl").open("w") as f:
        for rec in observations:
            line(f, rec)
    scores = ("correct_completion", "false_completion", "refusal_correct_state", "refusal_incorrect_state")
    rows = [dict(setting=k[0], scope=k[1], rule=k[2], cases=sum(v.values()),
                 **{s: v[s] for s in scores}) for k, v in sorted(summary.items())]
    with (outdir / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["setting", "scope", "rule", "cases", *scores])
        writer.writeheader()
        writer.writerows(rows)
    obs_stats = {}
    for setting, ids in sorted(obs_by_setting.items()):
        selected = [observations[i - 1] for i in sorted(ids)]
        obs_stats[setting] = dict(unique_observations=len(selected),
            no_targets=sum(not r["targets"] for r in selected),
            one_target=sum(len(r["targets"]) == 1 for r in selected),
            multiple_targets=sum(len(r["targets"]) > 1 for r in selected),
            multiple_histories_one_target=sum(r["candidate_count"] > 1 and len(r["targets"]) == 1 for r in selected))
    hypotheses = dict(
        H1=all(summary[(s, "all", "agreement")]["false_completion"] == 0 for s in ("tight", "loose")),
        H2="safe_missing" in witnesses,
        H3="replay_false" in witnesses,
        H4=checks["bound_monotonicity"] == case_id,
        H5="false_bound" in witnesses,
        H6="multiple_histories_one_target" in witnesses)
    dump(outdir / "summary.json", {"case_count": case_id, "unique_observations_all_settings": len(observations),
        "observation_counts": obs_stats, "hypotheses": hypotheses, "checks": dict(checks), "rows": rows})
    dump(outdir / "witnesses.json", witnesses)
    controls = []
    for initial, cmd, expect in [((0, 0), "add1", (1, 0)), ((0, 0), "sub1", (-1, 0)),
        ((3, 1), "set0", (0, 1)), ((3, 1), "set1", (1, 1)), ((3, 1), "flip_y", (3, 0))]:
        assert run(initial, (cmd,)) == expect
        controls.append("operation_" + cmd)
    empty = candidate_set(index, (0, 0), (99, 0), (), 0)
    assert not empty and not decide((0, 0), (99, 0), (), 0, ())["agreement"]["claim"]
    controls.append("inconsistent_empty_set_refuses")
    for invalid in (-1, 0.5, True, "1"):
        try:
            candidate_set(index, (0, 0), (1, 0), (), invalid)
        except ValueError:
            controls.append("reject_bound_" + str(invalid))
        else:
            raise AssertionError("invalid bound accepted")
    for args in [((0, 0), (1, 0), ("bad",), 0), ((0, 0), (1, 0), (), 6)]:
        try:
            candidate_set(index, *args)
        except ValueError:
            controls.append("reject_command_or_scope")
        else:
            raise AssertionError("invalid query accepted")
    dump(outdir / "controls.json", {"passed": len(controls), "controls": controls})
    dump(outdir / "output_hashes.json", {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(outdir.iterdir()) if p.name in
        ("cases.jsonl", "decisions.jsonl", "summary.csv", "summary.json", "witnesses.json", "controls.json")})
    print(json.dumps({"cases": case_id, "observations": len(observations),
                      "hypotheses": hypotheses, "controls": len(controls)}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "results")
    main(parser.parse_args().out)
