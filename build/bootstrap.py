#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════
# build/bootstrap.py
# ────────────────────────────────────────────────────────────────────────────
# Generated with the assistance of AI (Claude, Anthropic).
#
# Initialises the Python virtual environment for every chapter in the
# repository. Run this once after cloning the repo on a new machine.
#
# For each folder directly inside chapters/ it:
#   1. Creates a .venv inside the chapter folder
#   2. Installs base packages (numpy, matplotlib, pandas, ipykernel)
#   3. Installs anything listed in requirements.txt
#   4. Registers the folder name as a named Jupyter kernel
#
# This is the Python equivalent of `renv::restore()` — it reconstructs all
# chapter environments from the committed requirements.txt files without
# storing the venvs in git.
#
# Usage
# -----
#   python build/bootstrap.py                          # all chapters
#   python build/bootstrap.py --chapter my-chapter    # single chapter
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import subprocess
import sys
import venv
from pathlib import Path

# ── Project root ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

# ── Terminal colours ──────────────────────────────────────────────────────────
GRN = "\033[32m"; YEL = "\033[33m"; RED = "\033[31m"; RST = "\033[0m"
def ok(m):   print(f"{GRN}✓{RST}  {m}")
def info(m): print(f"{YEL}→{RST}  {m}")
def err(m):  print(f"{RED}✗{RST}  {m}", file=sys.stderr)

# ── Packages installed in every chapter venv regardless of topic ──────────────
BASE_PACKAGES = [
    "numpy>=1.26",
    "matplotlib>=3.8",
    "pandas>=2.1",
    "ipykernel>=6.0",    # required to register the Jupyter kernel
]


def bootstrap_chapter(chapter_dir: Path):
    """Create a venv, install packages, and register a Jupyter kernel
    for one chapter folder.
    """
    name     = chapter_dir.name          # folder name = kernel name
    venv_dir = chapter_dir / ".venv"     # venv lives inside the chapter folder
    req_path = chapter_dir / "requirements.txt"

    print(f"\n── {name} {'─' * (52 - len(name))}")

    # Create a fresh virtual environment with pip
    info("  Creating venv …")
    venv.create(str(venv_dir), with_pip=True, clear=True)

    pip = venv_dir / "bin" / "pip"

    # Upgrade pip silently to avoid version mismatch warnings
    subprocess.run(
        [str(pip), "install", "--quiet", "--upgrade", "pip"],
        check=True
    )

    # Install base packages common to all chapters
    info("  Installing base packages …")
    subprocess.run(
        [str(pip), "install", "--quiet"] + BASE_PACKAGES,
        check=True
    )

    # Install chapter-specific packages from requirements.txt if present
    if req_path.exists():
        # Filter out blank lines and comment lines
        lines = [
            l.strip() for l in req_path.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        if lines:
            info(f"  Installing {len(lines)} chapter-specific package(s) …")
            subprocess.run(
                [str(pip), "install", "--quiet", "-r", str(req_path)],
                check=True
            )
        else:
            info("  requirements.txt has no packages — skipping")

    # Register the venv as a named Jupyter kernel so Quarto can find it
    python = venv_dir / "bin" / "python"
    info(f"  Registering kernel '{name}' …")
    subprocess.run(
        [
            str(python), "-m", "ipykernel", "install",
            "--user",
            "--name", name,                       # identifier used in .qmd front matter
            "--display-name", f"Book – {name}",   # label shown in Jupyter UI
        ],
        check=True
    )

    ok(f"  {name} ready")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap chapter venvs and Jupyter kernels after cloning."
    )
    parser.add_argument(
        "--chapter", default=None,
        help="Bootstrap only one chapter folder, e.g. --chapter hodgkin-huxley"
    )
    args = parser.parse_args()

    if args.chapter:
        # Single-chapter mode: target one specific folder
        targets = [ROOT / "chapters" / args.chapter]
        if not targets[0].exists():
            err(f"Chapter folder not found: {targets[0]}")
            sys.exit(1)
    else:
        # All-chapters mode: every direct subdirectory of chapters/
        targets = sorted([
            d for d in (ROOT / "chapters").iterdir()
            if d.is_dir() and not d.name.startswith(".")    # skip hidden folders
        ])

    if not targets:
        info("No chapter folders found in chapters/ — nothing to do.")
        sys.exit(0)

    print(f"\n── Bootstrap — {len(targets)} chapter(s) {'─' * 30}\n")

    failed = []
    for chapter_dir in targets:
        try:
            bootstrap_chapter(chapter_dir)
        except subprocess.CalledProcessError as e:
            err(f"  Failed: {chapter_dir.name} — {e}")
            failed.append(chapter_dir.name)

    # Summary report
    print(f"\n── Summary {'─' * 50}")
    ok(f"  {len(targets) - len(failed)} chapter(s) bootstrapped successfully")
    if failed:
        for name in failed:
            err(f"  Failed: {name}")
        sys.exit(1)
    else:
        print(f"\n{GRN}All chapters ready.{RST} You can now run:\n")
        print("  make preview")
        print("  make all\n")


if __name__ == "__main__":
    main()
