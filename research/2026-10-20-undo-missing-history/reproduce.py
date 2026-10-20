"""Run the fixed procedure in a new temporary folder and compare every result."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

root = Path(__file__).resolve().parent
inputs = ("config.json", "analyze.py", "independent_check.py")
frozen = json.loads((root / "plan_freeze.json").read_text())
for name, expected in frozen["files"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name

started = datetime.datetime.now(datetime.timezone.utc).isoformat()
logs = []
comparisons = {}
with tempfile.TemporaryDirectory(prefix="undo-missing-reproduction-") as temp:
    folder = Path(temp)
    for name in inputs:
        shutil.copyfile(root / name, folder / name)
    for script in ("analyze.py", "independent_check.py"):
        before = time.perf_counter()
        result = subprocess.run([sys.executable, script], cwd=folder,
                                capture_output=True, text=True, timeout=600)
        logs.append({"command": f"python3 {script}", "exit_code": result.returncode,
                     "elapsed_seconds": time.perf_counter() - before,
                     "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise RuntimeError(json.dumps(logs[-1]))
    generated = {p.name for p in (folder / "results").iterdir() if p.is_file()}
    expected_names = {p.name for p in (root / "results").iterdir() if p.is_file()}
    assert generated == expected_names, (generated, expected_names)
    for name in sorted(generated):
        got = (folder / "results" / name).read_bytes()
        want = (root / "results" / name).read_bytes()
        assert got == want, name
        comparisons[name] = {"bytes": len(got), "sha256": hashlib.sha256(got).hexdigest(),
                             "exact_match": True}
receipt = {"status": "PASS", "started_at_utc": started,
           "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "frozen_input_hashes_match": True,
           "input_hashes": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in inputs},
           "commands": logs, "comparisons": comparisons}
(root / "reproduction_check.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": receipt["status"], "exact_result_files": len(comparisons)}, sort_keys=True))
