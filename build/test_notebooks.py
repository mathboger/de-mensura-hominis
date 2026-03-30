#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════
# build/test_notebooks.py
# ────────────────────────────────────────────────────────────────────────────
# Generated with the assistance of AI (Claude, Anthropic).
#
# Runs every .ipynb file in chapters/ through nbmake (a pytest plugin) to
# verify they execute without errors. Each notebook runs against its own
# chapter kernel, which maps to the chapter's .venv.
#
# Run `make bootstrap` before running tests on a fresh clone.
#
# Usage
# -----
#   python build/test_notebooks.py
#   python build/test_notebooks.py --chapter hodgkin-huxley
#   python build/test_notebooks.py --timeout 120
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent    # repository root

GRN = "\033[32m"; YEL = "\033[33m"; RED = "\033[31m"; RST = "\033[0m"
def info(m): print(f"{YEL}→{RST}  {m}")
def err(m):  print(f"{RED}✗{RST}  {m}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Run all chapter notebooks as tests using nbmake."
    )
    parser.add_argument("--chapter", default=None,
                        help="Test only one chapter, e.g. --chapter hodgkin-huxley")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Per-notebook timeout in seconds (default 300)")
    args = parser.parse_args()

    # Collect notebooks — either one chapter or all
    if args.chapter:
        notebooks = list(ROOT.glob(f"chapters/{args.chapter}/**/*.ipynb"))
    else:
        notebooks = sorted(ROOT.glob("chapters/**/*.ipynb"))

    # Exclude Jupyter checkpoint files which are not real notebooks
    notebooks = [n for n in notebooks if ".ipynb_checkpoints" not in str(n)]

    if not notebooks:
        info("No .ipynb files found — nothing to test.")
        return

    info(f"Testing {len(notebooks)} notebook(s) with nbmake…\n")

    # nbmake respects the kernel declared inside each notebook,
    # which corresponds to the chapter's registered .venv kernel
    cmd = [
        sys.executable, "-m", "pytest",
        "--nbmake",                              # use nbmake plugin
        f"--nbmake-timeout={args.timeout}",      # per-notebook timeout
        "-v",                                    # verbose output
    ] + [str(n) for n in notebooks]

    result = subprocess.run(cmd, cwd=ROOT)
    sys.exit(result.returncode)    # propagate pytest exit code to make


if __name__ == "__main__":
    main()
