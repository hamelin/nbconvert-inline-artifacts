import subprocess as sp
import sys
from typing import List


def print_heading(heading_: str) -> None:
    heading = f"=== {heading_} "
    suffix = "=" * (88 - len(heading))
    print()
    print(heading, suffix, sep="")


def run_cmd(cmd: List[str]) -> bool:
    cp = sp.run(cmd)
    return cp.returncode == 0


CHECKS = [
    ("flake8", ["flake8"]),
    ("mypy", ["mypy", "--ignore-missing-imports", "."]),
    ("pytest", ["pytest"])
]

checks_possible = [name for name, _ in CHECKS]
args = sys.argv[1:]
if args:
    for arg in args:
        if arg not in [checks_possible]:
            raise ValueError(
                f"Unknown check: {arg}. Use one of {', '.join(checks_possible)}"
            )
    checks_to_run = args
else:
    checks_to_run = checks_possible


commands = dict(CHECKS)
success = {}
for check in checks_to_run:
    print_heading(f"Running {check} [{' '.join(commands[check])}]")
    success[check] = run_cmd(commands[check])


print_heading("SUMMARY")
for check in checks_to_run:
    print(f"    {check:12s}{'pass' if success[check] else 'FAIL'}")
sys.exit(0 if all(success.values()) else 1)
