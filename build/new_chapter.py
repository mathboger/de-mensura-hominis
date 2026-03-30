#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════
# build/new_chapter.py
# ────────────────────────────────────────────────────────────────────────────
# Generated with the assistance of AI (Claude, Anthropic).
#
# Scaffolds a new chapter folder inside chapters/, creates and registers its
# own Python virtual environment, and adds its entry to _quarto.yml.
#
# Chapters can have any folder name — no prefix convention is enforced.
# The order and grouping of chapters is controlled entirely by _quarto.yml.
#
# Usage
# -----
#   python build/new_chapter.py "My Chapter Title"
#   python build/new_chapter.py "My Chapter Title" --lang python
#   python build/new_chapter.py "My Chapter Title" --lang r
#   python build/new_chapter.py "My Chapter Title" --lang both   (default)
#   python build/new_chapter.py "My Chapter Title" --app         (add Streamlit demo)
#   python build/new_chapter.py "My Chapter Title" --no-venv     (skip venv creation)
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import re
import subprocess
import sys
import venv
from pathlib import Path

# ── Project root (two levels up from this script) ────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

# ── Terminal colour codes for readable output ─────────────────────────────────
GRN = "\033[32m"; YEL = "\033[33m"; RED = "\033[31m"; RST = "\033[0m"
def ok(m):   print(f"{GRN}✓{RST}  {m}")    # success message
def info(m): print(f"{YEL}→{RST}  {m}")    # informational message
def err(m):  print(f"{RED}✗{RST}  {m}", file=sys.stderr); sys.exit(1)  # fatal error


def slugify(title: str) -> str:
    """Convert a human-readable title to a filesystem-safe folder name.

    Lowercases, strips special characters, and replaces spaces/hyphens with
    a single hyphen. Example: 'The Hodgkin–Huxley Model!' → 'the-hodgkin-huxley-model'
    """
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)    # remove non-word, non-space, non-hyphen chars
    s = re.sub(r"[\s_-]+", "-", s)    # collapse whitespace/underscores/hyphens to one hyphen
    return s


def create_chapter_venv(chapter_dir: Path, kernel_name: str, requirements: Path):
    """Create a Python virtual environment inside the chapter folder,
    install base scientific packages plus any chapter-specific requirements,
    and register the environment as a named Jupyter kernel so Quarto can find it.
    """
    venv_dir = chapter_dir / ".venv"
    info(f"  Creating venv at {venv_dir.relative_to(ROOT)} …")

    # Create a fresh venv with pip available
    venv.create(str(venv_dir), with_pip=True, clear=True)

    pip = venv_dir / "bin" / "pip"

    # Upgrade pip silently to avoid version warnings
    subprocess.run([str(pip), "install", "--quiet", "--upgrade", "pip"], check=True)

    # Install the packages every chapter needs regardless of topic
    info("  Installing base packages (numpy, matplotlib, pandas, ipykernel) …")
    subprocess.run([
        str(pip), "install", "--quiet",
        "numpy>=1.26", "matplotlib>=3.8", "pandas>=2.1", "ipykernel>=6.0"
    ], check=True)

    # Install chapter-specific packages if requirements.txt has non-comment content
    if requirements.exists():
        lines = [
            l.strip() for l in requirements.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        if lines:
            info(f"  Installing {len(lines)} chapter-specific package(s) …")
            subprocess.run(
                [str(pip), "install", "--quiet", "-r", str(requirements)],
                check=True
            )

    # Register as a Jupyter kernel so Quarto can activate it by name
    python = venv_dir / "bin" / "python"
    info(f"  Registering Jupyter kernel '{kernel_name}' …")
    subprocess.run([
        str(python), "-m", "ipykernel", "install",
        "--user",
        "--name", kernel_name,                          # internal kernel identifier
        "--display-name", f"Book – {kernel_name}",     # human-readable name in UI
    ], check=True)

    ok(f"  Kernel '{kernel_name}' registered")


def write_qmd(path: Path, title: str, lang: str, kernel_name: str):
    """Write a starter index.qmd for the chapter with seed initialisation,
    section stubs, a callout example, and figure placeholders.
    """
    sec_id = f"sec-{slugify(title)}"    # cross-reference anchor, e.g. #sec-my-chapter

    # Jupyter kernel declaration — only needed for Python chapters;
    # R chapters use knitr automatically
    kernel_line = f"jupyter: {kernel_name}" if lang in ("python", "both") else ""

    # Python seed block — ensures all randomness is reproducible
    py_seed = """\
```{python}
#| include: false
import random, numpy as np
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
```
""" if lang in ("python", "both") else ""

    # R seed block
    r_seed = """\
```{r}
#| include: false
SEED <- 42L
set.seed(SEED)
```
""" if lang in ("r", "both") else ""

    # Python figure example
    py_fig = """\
## A Python example

```{python}
#| label: fig-demo-py
#| fig-cap: "Caption here."
import matplotlib.pyplot as plt
import numpy as np

rng = np.random.default_rng(SEED)
x = np.linspace(0, 2 * np.pi, 300)
y = np.sin(x) + rng.normal(0, 0.1, 300)

fig, ax = plt.subplots(figsize=(6, 3.5))
ax.plot(x, y)
ax.set_xlabel("x"); ax.set_ylabel("y")
plt.tight_layout(); plt.show()
```

""" if lang in ("python", "both") else ""

    # R figure example
    r_fig = """\
## An R example

```{r}
#| label: fig-demo-r
#| fig-cap: "Caption here."
curve(sin(x), 0, 2*pi, col = "#4E79A7", lwd = 2,
      xlab = "x", ylab = "y")
```

""" if lang in ("r", "both") else ""

    content = f"""---
title: "{title}"
{kernel_line}
---

# {title} {{#{sec_id}}}

{r_seed}{py_seed}
Chapter introduction — replace this text.

## Background

Write background here.

::: {{.callout-note}}
## What you will learn

- Point one
- Point two
- Point three
:::

{py_fig}{r_fig}## Summary

Key takeaways.
"""
    path.write_text(content)


def write_requirements(path: Path):
    """Write a commented requirements.txt template for the chapter.
    Base packages (numpy, matplotlib, pandas) are pre-installed by bootstrap
    and do not need to be listed here.
    """
    path.write_text(
        "# Chapter-specific packages — add what this chapter needs.\n"
        "# Base packages (numpy, matplotlib, pandas) are pre-installed.\n"
        "# Examples:\n"
        "# scipy>=1.12\n"
        "# statsmodels>=0.14\n"
        "# networkx>=3.2\n"
    )


def write_app(chapter_dir: Path, title: str):
    """Write a minimal Streamlit demo app for the chapter.
    The app shows a histogram of random data with a sample size slider.
    Replace with chapter-specific content when writing real chapters.
    """
    app = f'''\
# ══════════════════════════════════════════════════════════════════════════════
# app.py — Interactive demo for: {title}
# Generated with the assistance of AI (Claude, Anthropic).
#
# Run with:  source .venv/bin/activate && streamlit run app.py
# ══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

SEED = 42
rng = np.random.default_rng(SEED)    # seeded RNG for reproducibility

st.set_page_config(page_title="{title}", layout="centered")
st.title("{title}")

# Interactive control — reader adjusts sample size
n = st.slider("Sample size", 10, 2000, 200, 10)

# Generate data and plot
data = rng.standard_normal(n)
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(data, bins=30, color="#4E79A7", edgecolor="white")
ax.set_xlabel("value"); ax.set_ylabel("count")
st.pyplot(fig)
'''
    (chapter_dir / "app.py").write_text(app)


def inject_into_quarto_yml(chapter_path: str):
    """Append the new chapter's path to the end of the chapters list in
    _quarto.yml, inside the last part block if one exists, or at the root
    chapters level otherwise.

    The user is expected to manually move the entry to the correct part and
    position in _quarto.yml after scaffolding. This function just ensures
    the chapter is registered so the build doesn't fail.
    """
    yml_path = ROOT / "_quarto.yml"
    text = yml_path.read_text()
    entry = f"        - {chapter_path}\n"    # indented to match part > chapters level

    # Find the last chapter entry and insert after it
    lines = text.splitlines(keepends=True)
    insert_at = None
    for i, line in enumerate(lines):
        if line.strip().startswith("- chapters/"):    # any existing chapter entry
            insert_at = i

    if insert_at is not None:
        # Insert immediately after the last found chapter entry
        lines.insert(insert_at + 1, entry)
        text = "".join(lines)
    else:
        # No existing chapter entries found — append at end
        text = text.rstrip() + "\n" + entry + "\n"

    yml_path.write_text(text)


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new chapter with its own venv and Jupyter kernel."
    )
    parser.add_argument("title",
                        help="Chapter title in quotes, e.g. 'The Hodgkin-Huxley Model'")
    parser.add_argument("--lang", choices=["python", "r", "both"], default="both",
                        help="Programming language(s) for code cells (default: both)")
    parser.add_argument("--app", action="store_true",
                        help="Add a Streamlit interactive demo app")
    parser.add_argument("--no-venv", action="store_true",
                        help="Skip venv creation (register kernel manually later)")
    args = parser.parse_args()

    # Derive folder name from title — no numeric prefix enforced
    slug        = slugify(args.title)          # e.g. "the-hodgkin-huxley-model"
    kernel_name = slug                         # kernel name matches folder name
    cdir        = ROOT / "chapters" / slug     # full path to chapter folder
    cdir.mkdir(parents=True, exist_ok=True)    # create folder (and parents) if needed

    print(f"\n── Scaffolding: {args.title} {'─' * 40}\n")
    info(f"  Folder  : chapters/{slug}/")
    info(f"  Kernel  : {kernel_name}")
    info(f"  Language: {args.lang}")
    print()

    # Always write requirements.txt first — venv creation reads it
    req_path = cdir / "requirements.txt"
    write_requirements(req_path)
    ok("  requirements.txt written (edit before adding packages)")

    # Create venv and register kernel (Python chapters only)
    if not args.no_venv and args.lang in ("python", "both"):
        create_chapter_venv(cdir, kernel_name, req_path)
    elif args.lang in ("python", "both"):
        info("  Skipping venv (--no-venv). Register kernel manually when ready.")

    # Write the starter .qmd file
    write_qmd(cdir / "index.qmd", args.title, args.lang, kernel_name)
    ok("  index.qmd written")

    # Optionally add a Streamlit demo app
    if args.app:
        write_app(cdir, args.title)
        ok("  app.py written")
        info("  Add 'streamlit' to requirements.txt, then:")
        info(f"  cd chapters/{slug} && source .venv/bin/activate && pip install -r requirements.txt")
        info(f"  streamlit run app.py")

    # Register chapter in _quarto.yml (appended after last existing chapter)
    inject_into_quarto_yml(f"chapters/{slug}/index.qmd")
    ok("  _quarto.yml updated")

    print(f"\n✓  Chapter ready.\n")
    print(f"  Edit content  : chapters/{slug}/index.qmd")
    print(f"  Add packages  : chapters/{slug}/requirements.txt")
    if args.lang in ("python", "both") and not args.no_venv:
        print(f"  Activate env  : source chapters/{slug}/.venv/bin/activate")
    print(f"\n  ⚠  Remember to move the chapter entry in _quarto.yml")
    print(f"     to the correct part and position for your intended book structure.\n")


if __name__ == "__main__":
    main()
