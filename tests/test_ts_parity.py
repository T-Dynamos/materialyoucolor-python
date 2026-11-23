import os
import shutil
import subprocess
import pytest


def test_deno_typescript_parity():
    """Verify bit-for-bit parity against upstream TypeScript using Deno if installed."""
    if not os.path.exists("tests/compare_ts_py_all.py") or not shutil.which("deno"):
        pytest.skip("deno or compare_ts_py_all.py not available, skipping TypeScript parity test")

    res = subprocess.run(
        ["python3", "tests/compare_ts_py_all.py", "--contrasts", "0.0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert res.returncode == 0, f"Parity comparison failed:\n{res.stdout}\n{res.stderr}"
    assert "All comparisons matched." in res.stdout
