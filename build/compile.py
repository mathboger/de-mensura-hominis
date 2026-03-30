#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════
# build/compile.py
# ────────────────────────────────────────────────────────────────────────────
# Generated with the assistance of AI (Claude, Anthropic).
#
# Master build script for De Mensura Hominis.
# Orchestrates Quarto rendering to HTML (output/html/) and PDF (output/pdf/).
#
# Each chapter uses its own Jupyter kernel backed by chapters/<name>/.venv.
# The global .venv only needs jupyter/ipykernel — not chapter science packages.
# Run `make bootstrap` after cloning to initialise all chapter venvs.
#
# Usage
# -----
#   python build/compile.py              # build HTML + PDF
#   python build/compile.py --html       # HTML only
#   python build/compile.py --pdf        # PDF only
#   python build/compile.py --freeze     # skip re-executing notebooks
#   python build/compile.py --chapter hodgkin-huxley   # one chapter only
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent.parent    # repository root
OUTPUT = ROOT / "output"                           # parent of html/ and pdf/

# ── Terminal colours ──────────────────────────────────────────────────────────
GRN = "\033[32m"; YEL = "\033[33m"; RED = "\033[31m"; RST = "\033[0m"
def ok(m):   print(f"{GRN}✓{RST}  {m}")
def info(m): print(f"{YEL}→{RST}  {m}")
def err(m):  print(f"{RED}✗{RST}  {m}", file=sys.stderr)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a shell command, stream its output to the terminal, and raise on failure."""
    info(" ".join(str(c) for c in cmd))
    result = subprocess.run(cmd, cwd=ROOT, **kwargs)
    if result.returncode != 0:
        err(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    return result


def check_quarto():
    """Verify that Quarto is installed and print its version."""
    try:
        v = subprocess.check_output(["quarto", "--version"], text=True).strip()
        ok(f"Quarto {v} found")
    except FileNotFoundError:
        err("quarto not found. Install from https://quarto.org/docs/get-started/")
        sys.exit(1)


def check_kernels():
    """Scan every chapter's index.qmd for a `jupyter:` declaration and warn
    if that kernel is not registered on this machine. A missing kernel causes
    a silent build failure that is hard to diagnose without this check.
    """
    try:
        # Ask Jupyter for the list of registered kernels as JSON
        registered = subprocess.check_output(
            ["jupyter", "kernelspec", "list", "--json"], text=True
        )
        kernel_names = set(json.loads(registered).get("kernelspecs", {}).keys())
    except Exception:
        info("Could not list kernels — skipping kernel check")
        return

    # Check every chapter's front matter for a jupyter: key
    for qmd in sorted(ROOT.glob("chapters/**/index.qmd")):
        for line in qmd.read_text().splitlines():
            if line.strip().startswith("jupyter:"):
                kernel = line.split(":", 1)[1].strip()    # extract kernel name
                if kernel not in kernel_names:
                    err(
                        f"Kernel '{kernel}' not registered "
                        f"(declared in {qmd.relative_to(ROOT)}). "
                        f"Run: make bootstrap-chapter CHAPTER={qmd.parent.name}"
                    )


def build_html(freeze: bool = False, chapter: str = None):
    """Render the book (or a single chapter) to HTML.
    Output lands in output/html/ to avoid overwriting the PDF build.
    """
    info("Building HTML book…")
    t = time.time()

    # Create output directory if it doesn't exist
    output_dir = ROOT / "output" / "html"
    output_dir.mkdir(parents=True, exist_ok=True)

    if chapter:
        # Render only the specified chapter folder
        cmd = ["quarto", "render", f"chapters/{chapter}/index.qmd",
               "--to", "html", "--output-dir", str(output_dir)]
    else:
        # Render the entire book
        cmd = ["quarto", "render", ".", "--to", "html",
               "--output-dir", str(output_dir)]

    if freeze:
        cmd += ["--freeze"]    # skip code execution, use cached outputs

    run(cmd)
    ok(f"HTML built in {time.time()-t:.1f}s  →  output/html/")


def build_pdf(freeze: bool = False, chapter: str = None):
    """Render the book (or a single chapter) to PDF.
    Output lands in output/pdf/ to avoid overwriting the HTML build.
    """
    info("Building PDF book…")
    t = time.time()

    # Create output directory if it doesn't exist
    output_dir = ROOT / "output" / "pdf"
    output_dir.mkdir(parents=True, exist_ok=True)

    if chapter:
        cmd = ["quarto", "render", f"chapters/{chapter}/index.qmd",
               "--to", "pdf", "--output-dir", str(output_dir)]
    else:
        cmd = ["quarto", "render", ".", "--to", "pdf",
               "--output-dir", str(output_dir)]

    if freeze:
        cmd += ["--freeze"]

    run(cmd)

    # Report the PDF filename so the user knows where to find it
    pdfs = list(output_dir.glob("*.pdf"))
    if pdfs:
        ok(f"PDF built in {time.time()-t:.1f}s  →  output/pdf/{pdfs[0].name}")
    else:
        err("PDF not found in output/pdf/ — check Quarto logs above")


def screenshot_apps():
    """Capture screenshots of any chapter app.py files using Playwright.
    Screenshots are saved as screenshot.png next to each app.py and can be
    embedded in the PDF version of the chapter.
    Skipped silently if Playwright is not installed.
    """
    try:
        from playwright.sync_api import sync_playwright    # noqa: F401
    except ImportError:
        info("playwright not installed — skipping app screenshots")
        return

    import socket
    from playwright.sync_api import sync_playwright

    for app_path in sorted(ROOT.glob("chapters/*/app.py")):
        chapter_dir = app_path.parent
        # Use the chapter's own venv Python if available, else fall back
        venv_python  = chapter_dir / ".venv" / "bin" / "python"
        python_bin   = str(venv_python) if venv_python.exists() else sys.executable
        screenshot   = chapter_dir / "screenshot.png"

        info(f"Screenshotting {app_path.relative_to(ROOT)} …")

        # Start Streamlit server in background
        proc = subprocess.Popen(
            [python_bin, "-m", "streamlit", "run", "app.py",
             "--server.headless", "true", "--server.port", "8765"],
            cwd=chapter_dir,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

        # Poll until the server is accepting connections (up to 10 seconds)
        for _ in range(20):
            time.sleep(0.5)
            try:
                with socket.create_connection(("localhost", 8765), timeout=1):
                    break
            except OSError:
                pass

        # Take the screenshot and shut down the server
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1100, "height": 700})
            page.goto("http://localhost:8765")
            page.wait_for_timeout(2000)    # wait for page to fully render
            page.screenshot(path=str(screenshot), full_page=False)
            browser.close()

        proc.terminate()
        ok(f"Screenshot → {screenshot.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser(
        description="Build the De Mensura Hominis book (HTML and/or PDF)."
    )
    parser.add_argument("--html",   action="store_true", help="Build HTML only")
    parser.add_argument("--pdf",    action="store_true", help="Build PDF only")
    parser.add_argument("--freeze", action="store_true",
                        help="Skip re-running code (use frozen outputs)")
    parser.add_argument("--screenshots", action="store_true",
                        help="Capture app screenshots before building")
    parser.add_argument("--chapter", default=None,
                        help="Render one chapter only, e.g. --chapter hodgkin-huxley")
    args = parser.parse_args()

    # Default: build both formats if neither --html nor --pdf is specified
    build_both = not args.html and not args.pdf

    print("\n── Book compiler ──────────────────────────────────────────────\n")
    check_quarto()       # abort early if Quarto is missing
    check_kernels()      # warn about any unregistered chapter kernels
    OUTPUT.mkdir(parents=True, exist_ok=True)

    if args.screenshots:
        screenshot_apps()

    if args.html or build_both:
        build_html(freeze=args.freeze, chapter=args.chapter)

    if args.pdf or build_both:
        build_pdf(freeze=args.freeze, chapter=args.chapter)

    print("\n── Done ───────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
