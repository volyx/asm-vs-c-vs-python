#!/usr/bin/env python3
"""Comprehensive test suite for Combination Python program."""

import subprocess
import sys

TEST_CASES = [
    # (k, n, expected)
    (3, 5, 10),
    (0, 5, 1),
    (5, 5, 1),
    (1, 5, 5),
    (4, 5, 5),
    (0, 0, 1),
    (2, 4, 6),
    (10, 20, 184756),
    (25, 50, 126410606437752),
    (50, 100, 100891344545564193334812497256),
    # Edge cases
    (6, 5, 0),    # k > n
    (-1, 5, 0),   # negative k
    (2, -5, 0),   # negative n
    (-2, -5, 0),  # both negative
]


def run_stdin(k: int, n: int, sep: str = " ", prog: str = "main.py") -> str:
    proc = subprocess.run(
        [sys.executable, prog],
        input=f"{k}{sep}{n}\n",
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"run_stdin failed: {proc.stderr}")
    return proc.stdout.strip()


def run_args(k: int, n: int, prog: str = "main.py") -> str:
    proc = subprocess.run(
        [sys.executable, prog, str(k), str(n)],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"run_args failed: {proc.stderr}")
    return proc.stdout.strip()


def run_wrapper(k: int, n: int) -> str:
    proc = subprocess.run(
        ["./combination", str(k), str(n)],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"run_wrapper failed: {proc.stderr}")
    return proc.stdout.strip()


def main():
    print("Running tests for Python combination...")
    passed = 0

    for k, n, expected in TEST_CASES:
        for script in ["main.py", "combination.py"]:
            # 1. Test stdin with space
            out1 = run_stdin(k, n, " ", prog=script)
            assert int(out1) == expected, f"stdin space failed for {script} k={k}, n={n}: expected {expected}, got {out1}"

            # 2. Test stdin with newline
            out2 = run_stdin(k, n, "\n", prog=script)
            assert int(out2) == expected, f"stdin newline failed for {script} k={k}, n={n}: expected {expected}, got {out2}"

            # 3. Test args
            out3 = run_args(k, n, prog=script)
            assert int(out3) == expected, f"args failed for {script} k={k}, n={n}: expected {expected}, got {out3}"

        out4 = run_wrapper(k, n)
        assert int(out4) == expected, f"wrapper failed for k={k}, n={n}: expected {expected}, got {out4}"

        passed += 1
        print(f"  [PASS] k={k}, n={n} -> {expected}")

    print(f"\nAll {passed} test scenarios passed successfully!")


if __name__ == "__main__":
    main()
