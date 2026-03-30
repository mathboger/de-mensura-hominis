# ══════════════════════════════════════════════════════════════════════════════
# Makefile
# ────────────────────────────────────────────────────────────────────────────
# Generated with the assistance of AI (Claude, Anthropic).
#
# Convenience commands for building and managing De Mensura Hominis.
# All targets activate the global .venv before running Python scripts.
# ══════════════════════════════════════════════════════════════════════════════

SHELL := /bin/bash    # use bash so `source` works in all targets

.PHONY: all html pdf clean preview screenshots chapter chapter-app test bootstrap bootstrap-chapter

# ── Build targets ─────────────────────────────────────────────────────────────

all: html pdf    # build both HTML and PDF

html:            # HTML only — output lands in output/html/
	source .venv/bin/activate && python build/compile.py --html

pdf:             # PDF only — output lands in output/pdf/
	source .venv/bin/activate && python build/compile.py --pdf

screenshots:     # capture Streamlit app screenshots before building
	source .venv/bin/activate && python build/compile.py --screenshots

# ── Development ───────────────────────────────────────────────────────────────

preview:         # live-reloading HTML preview in browser
	source .venv/bin/activate && quarto preview . --to html

fast:            # build both formats without re-running code (uses frozen outputs)
	source .venv/bin/activate && python build/compile.py --freeze

# ── Chapter scaffolding ───────────────────────────────────────────────────────
# Usage:  make chapter TITLE="My Chapter Title"
# Usage:  make chapter-app TITLE="My Chapter Title"
# No book/part prefix is needed — folder names are free-form.
# After scaffolding, move the chapter entry in _quarto.yml to the correct
# part and position for your intended book structure.

chapter:
	source .venv/bin/activate && python build/new_chapter.py "$(TITLE)"

chapter-app:     # scaffold chapter + Streamlit demo app
	source .venv/bin/activate && python build/new_chapter.py "$(TITLE)" --app

# ── Environment management ────────────────────────────────────────────────────

bootstrap:       # initialise all chapter venvs and kernels after a fresh clone
	source .venv/bin/activate && python build/bootstrap.py

bootstrap-chapter:   # initialise a single chapter:  make bootstrap-chapter CHAPTER=hodgkin-huxley
	source .venv/bin/activate && python build/bootstrap.py --chapter $(CHAPTER)

# ── Testing ───────────────────────────────────────────────────────────────────

test:            # run all notebooks as tests (requires nbmake)
	source .venv/bin/activate && python build/test_notebooks.py

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean:           # remove generated outputs (keeps frozen execution cache)
	rm -rf output/html/ output/pdf/
	find . -name "_freeze" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".quarto" -type d -exec rm -rf {} + 2>/dev/null || true

clean-all: clean    # nuclear clean — also clears the execution cache
	find . -name "*.cached" -delete
