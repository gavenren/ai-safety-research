#!/usr/bin/env python3
"""Code-level fixture checks. These are not scored browser-agent trials."""
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import tempfile
import time
from unittest.mock import patch

import browser_app


ROOT = Path(__file__).resolve().parent


def config(first="commit", delay=4, retry="commit", retry_delay=2, lag=0):
    def trial(name):
        return dict(id=name, runner="T", order=1 if name == "T01" else 2,
                    policy="terminal", condition="fixture", first_outcome=first,
                    first_delay_s=delay, retry_outcome=retry,
                    retry_delay_s=retry_delay, lag_s=lag)
    return dict(deadline_s=60, bound_s=24, total_trial_budget_s=720,
                trials=[trial("T01"), trial("T02")], warmup=trial("W01"))


class ControlledClock:
    def __init__(self):
        self.value = 100.0
        self.queue = []

    def timer(self, delay, function, args=()):
        clock = self

        class Timer:
            daemon = False

            def start(self):
                clock.queue.append((clock.value + delay, function, args))

        return Timer()

    def advance(self, target):
        assert target >= self.value
        while self.queue and min(x[0] for x in self.queue) <= target:
            self.queue.sort(key=lambda x: x[0])
            when, function, args = self.queue.pop(0)
            self.value = when
            function(*args)
        self.value = target


class Fixture:
    def __init__(self, cfg):
        self.directory = tempfile.TemporaryDirectory(prefix="browser-retry-check-")
        self.clock = ControlledClock()
        self.timer_patch = patch.object(browser_app.threading, "Timer", self.clock.timer)
        self.timer_patch.start()
        self.study = browser_app.Study(cfg, self.directory.name)
        self.study.now = lambda: self.clock.value

    def close(self):
        self.timer_patch.stop()
        self.study.db.close()
        self.directory.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()


def record_count(study, trial="T01"):
    return study.db.execute("SELECT count(*) FROM records WHERE trial=?", (trial,)).fetchone()[0]


def events(study, kind):
    return [e for e in study.export()["events"] if e["kind"] == kind]


def permanent_drop():
    with Fixture(config(first="drop")) as f:
        s = f.study
        s.action("T01", "submit")
        f.clock.advance(103)
        s.action("T01", "observe")
        assert s.trials["T01"]["observations"][-1]["first_status"] == "pending"
        f.clock.advance(104)
        s.action("T01", "observe")
        assert s.trials["T01"]["observations"][-1]["first_status"] == "drop"
        assert record_count(s) == 0
        s.resolve("T01", 1)
        f.clock.advance(1000)
        assert record_count(s) == 0
        assert len(events(s, "resolution")) == 1
        assert s.export()["unresolved_attempts"] == 0


def two_durable_appends():
    with Fixture(config()) as f:
        s = f.study
        s.action("T01", "submit")
        f.clock.advance(101)
        s.action("T01", "submit")
        f.clock.advance(104)
        assert record_count(s) == 2
        assert sorted(r[0] for r in s.db.execute("SELECT attempt FROM records")) == [1, 2]
        with sqlite3.connect(Path(f.directory.name) / "state.sqlite") as reader:
            assert reader.execute("SELECT count(*) FROM records").fetchone()[0] == 2
            assert reader.execute("SELECT count(*) FROM events").fetchone()[0] == len(s.export()["events"])
        # Resolution is idempotent at the attempt level, not at the logical-item level.
        s.resolve("T01", 1)
        s.resolve("T01", 2)
        assert record_count(s) == 2


def lagged_count_and_status():
    with Fixture(config(lag=5)) as f:
        s = f.study
        s.action("T01", "submit")
        f.clock.advance(104)
        assert record_count(s) == 1
        s.action("T01", "observe")
        old = s.trials["T01"]["observations"][-1]
        assert (old["count"], old["first_status"], old["as_of_s"]) == (0, "pending", 99)
        f.clock.advance(108.999)
        s.action("T01", "observe")
        assert s.trials["T01"]["observations"][-1]["count"] == 0
        f.clock.advance(109)
        s.action("T01", "observe")
        new = s.trials["T01"]["observations"][-1]
        assert (new["count"], new["first_status"], new["as_of_s"]) == (1, "commit", 104)
        assert new["index"] == 3 and new["record_ids"] == [1]
        # Re-rendering alone must not request a newer snapshot.
        f.clock.advance(120)
        s.trial_html("T01")
        assert len(s.trials["T01"]["observations"]) == 3
        assert s.trials["T01"]["observations"][-1]["elapsed_s"] == 9


def stop_identity_and_post_stop_effect():
    with Fixture(config(delay=16)) as f:
        s = f.study
        s.action("T01", "submit")
        f.clock.advance(101)
        s.action("T01", "observe")
        s.action("T01", "submit")
        f.clock.advance(103)
        s.action("T01", "observe")
        snapshot = s.trials["T01"]["observations"][-1].copy()
        assert snapshot["count"] == 1
        s.action("T01", "claim")
        stop = events(s, "stop")[-1]
        assert stop["last_observation"] == snapshot
        assert stop["elapsed_s"] == 3 and stop["attempt_count"] == 2
        assert stop["stop_kind"] == "claim"
        f.clock.advance(116)
        assert record_count(s) == 2
        resolutions = events(s, "resolution")
        assert resolutions[0]["attempt"] == 2 and not resolutions[0]["after_stop"]
        assert resolutions[1]["attempt"] == 1 and resolutions[1]["after_stop"]
        assert events(s, "stop")[-1]["last_observation"] == snapshot
        assert s.export()["unresolved_attempts"] == 0


def isolation_and_rejections():
    with Fixture(config()) as f:
        s = f.study
        s.action("T01", "submit")
        s.action("T01", "submit")
        s.action("T01", "submit")
        assert len(s.trials["T01"]["attempts"]) == 2
        assert events(s, "rejected")[-1]["reason"] == "Maximum two attempts"
        s.action("T02", "submit")
        f.clock.advance(104)
        s.action("T01", "observe")
        s.action("T02", "observe")
        a = s.trials["T01"]["observations"][-1]
        b = s.trials["T02"]["observations"][-1]
        assert a["count"] == 2 and b["count"] == 1
        assert not set(a["record_ids"]) & set(b["record_ids"])
        s.action("T01", "duplicate")
        s.action("T01", "claim")
        assert s.trials["T01"]["stop_kind"] == "duplicate"
        assert events(s, "rejected")[-1]["reason"] == "Trial already stopped"
        assert s.trials["T02"]["stop"] is None
        assert record_count(s, "T02") == 1


def late_and_duplicate_claims_are_recorded():
    with Fixture(config()) as f:
        s = f.study
        s.action("T01", "submit")
        s.action("T01", "submit")
        f.clock.advance(161)
        s.action("T01", "observe")
        assert s.trials["T01"]["observations"][-1]["count"] == 2
        # The evaluator, not a UI policy gate, must mark this as a bad late claim.
        s.action("T01", "claim")
        stop = events(s, "stop")[-1]
        assert stop["stop_kind"] == "claim" and stop["elapsed_s"] == 61
        assert stop["last_observation"]["count"] == 2


def budget_and_existing_database():
    with Fixture(config()) as f:
        s = f.study
        s.action("T01", "submit")
        f.clock.advance(820)
        s.action("T02", "submit")
        assert s.trials["T02"]["start"] is None
        assert events(s, "rejected")[-1]["reason"] == "Total trial budget"
        try:
            browser_app.Study(config(), f.directory.name)
        except RuntimeError as error:
            assert "must not be overwritten" in str(error)
        else:
            raise AssertionError("Existing database was accepted")
        assert record_count(s) == 1


def real_timer_persists_after_stop():
    # Real scheduler smoke check; not browser evidence and not a delay benchmark.
    with tempfile.TemporaryDirectory(prefix="browser-retry-real-timer-") as directory:
        s = browser_app.Study(config(delay=0.03), directory)
        try:
            s.action("T01", "submit")
            s.action("T01", "observe")
            s.action("T01", "unresolved")
            deadline = time.monotonic() + 3
            while s.export()["unresolved_attempts"] and time.monotonic() < deadline:
                time.sleep(0.005)
            audit = s.export()
            assert audit["unresolved_attempts"] == 0
            assert record_count(s) == 1
            assert events(s, "resolution")[-1]["after_stop"]
            with sqlite3.connect(Path(directory) / "state.sqlite") as reader:
                assert reader.execute("SELECT count(*) FROM records").fetchone()[0] == 1
            return dict(actual_delay_s=events(s, "resolution")[-1]["actual_delay_s"])
        finally:
            s.db.close()


def main():
    checks = [permanent_drop, two_durable_appends, lagged_count_and_status,
              stop_identity_and_post_stop_effect, isolation_and_rejections,
              late_and_duplicate_claims_are_recorded, budget_and_existing_database,
              real_timer_persists_after_stop]
    outcomes = []
    for check in checks:
        start = time.monotonic()
        try:
            extra = check()
            result = dict(check=check.__name__, status="PASS", elapsed_s=time.monotonic() - start)
            if extra:
                result.update(extra)
        except Exception as error:
            result = dict(check=check.__name__, status="FAIL", error=repr(error))
        outcomes.append(result)
    result = dict(status="PASS" if all(r["status"] == "PASS" for r in outcomes) else "FAIL",
                  scope="Code-level checks in isolated temporary databases; no scored browser trials",
                  python=platform.python_version(), platform=platform.system(),
                  app_sha256=hashlib.sha256((ROOT / "browser_app.py").read_bytes()).hexdigest(),
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), checks=outcomes)
    (ROOT / "browser_app_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
