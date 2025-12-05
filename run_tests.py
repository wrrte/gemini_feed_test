"""Cross-platform entry point for running the SafeHome tests.

This script uses the current Python interpreter to execute pytest (or
coverage + pytest) so it behaves the same way on Windows, macOS, and
Linux without requiring a POSIX shell.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the SafeHome test suite",
        epilog=(
            "Additional pytest arguments can be provided after a '--' separator, "
            "for example: python run_tests.py -- -k login"
        ),
    )
    parser.add_argument(
        "-t",
        "--tests",
        nargs="+",
        default=["test"],
        metavar="PATH",
        help="Test directories or files to run (default: 'test').",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run the tests under coverage and print a summary report.",
    )
    # argparse.REMAINDER preserves any extra flags for pytest without validation
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded directly to pytest (prefix with '--').",
    )
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    if args.coverage:
        command = [sys.executable, "-m", "coverage", "run", "-m", "pytest"]
    else:
        command = [sys.executable, "-m", "pytest"]

    extra_args = args.pytest_args or []
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]

    return command + args.tests + extra_args


def main() -> int:
    args = parse_args()
    repo_root = pathlib.Path(__file__).resolve().parent
    command = build_command(args)

    print("Executing:", " ".join(command))
    result = subprocess.call(command, cwd=repo_root)

    if args.coverage and result == 0:
        report_cmd = [sys.executable, "-m", "coverage", "report"]
        print("Executing:", " ".join(report_cmd))
        result = subprocess.call(report_cmd, cwd=repo_root)

    return result


if __name__ == "__main__":
    sys.exit(main())
