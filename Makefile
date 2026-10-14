# LightGBM needs OpenMP (libomp) on macOS: Homebrew (Apple silicon, Intel) or, failing that, an Anaconda installation
PY := cd python && . .venv/bin/activate && DYLD_FALLBACK_LIBRARY_PATH=$${DYLD_FALLBACK_LIBRARY_PATH:-/opt/homebrew/opt/libomp/lib:/usr/local/opt/libomp/lib:/opt/anaconda3/lib}
# PDF exports of the Bulletin officiel and the bulk XML index, outside the repository: make bo-import BO_DIR=<folder>
BO_DIR ?=
BO_FR := $(BO_DIR)/publications.pdf $(foreach i,2 3 4 5 6 7,$(BO_DIR)/publications-$(i).pdf)
BO_DE := $(BO_DIR)/publications-10.pdf $(BO_DIR)/publications-11.pdf

.PHONY: install dev check py-check py-test py-lint py-types backtest world demo web-check db-test bo-import

# Everything a new machine needs, at the exact versions that were tested: Node 22 (apps/web/.nvmrc) and uv (it installs
# Python 3.12.13 itself, python/.python-version); then `make dev` for the app on http://localhost:3000
install:
	cd python && uv sync --frozen --extra dev
	cd apps/web && npm ci

dev:
	cd apps/web && npm run dev

check: py-check web-check db-test

py-check: py-lint py-types py-test

py-lint:
	$(PY) ruff check src tests

py-types:
	$(PY) mypy

py-test:
	$(PY) pytest -q -m "not network"

world:
	$(PY) proxsis world --seed 42

backtest:
	$(PY) proxsis backtest --seed 42

demo:
	$(PY) proxsis export-demo --seed 42

web-check:
	cd apps/web && npm run lint && npm run typecheck && npm test && npm run build

db-test:
	./supabase/tests/run.sh

# Bulletin officiel: FR then DE import (filter + sweep before any write), draws and freeze, assignments, radar note.
# Same seeds: the same files give the same outputs. A clean rebuild writes into EMPTY staging folders (nothing is
# merged with earlier outputs), is audited, then replaces the delivered files: see the audit of the clean rebuild of 2026-10-06 (working notes, not published)
BO_PUBLIC ?= ../data/manuel/import_pdf
BO_PRIVE ?= ../data/manuel/textes/bo_vs_pdf
BO_ANNOT ?= ../data/annotations/bo_vs_v1
BO_PAGES ?= ../data/manuel/textes/bo_vs_v1
BO_RADAR_MD ?= ../docs/radar/projets_bo_vs_2026-08-09.md
bo-import:
	@test -n "$(BO_DIR)" || { echo "BO_DIR manque : make bo-import BO_DIR=<dossier des exports PDF et XML>"; exit 2; }
	$(PY) proxsis import-bo-pdf --pdfs $(BO_FR) --index $(BO_DIR)/publications.xml --public $(BO_PUBLIC) \
		--prive $(BO_PRIVE) --contexte $(BO_FR) $(BO_DE)
	$(PY) proxsis import-bo-pdf --pdfs $(BO_DE) --index $(BO_DIR)/publications.xml --public $(BO_PUBLIC) \
		--prive $(BO_PRIVE) --suffixe _de --contexte $(BO_FR) $(BO_DE)
	$(PY) proxsis tirage-bo --langue fr --n 100 --public $(BO_PUBLIC) --prive $(BO_PRIVE) --annotations $(BO_ANNOT)
	$(PY) proxsis tirage-bo --langue de --n 50 --public $(BO_PUBLIC) --prive $(BO_PRIVE) --annotations $(BO_ANNOT)
	$(PY) proxsis repartir-annotation --items $(BO_PRIVE)/items_fr.jsonl --annotateurs A1,A2 --double 14 \
		--seed 20261006 --public $(BO_ANNOT) --prive $(BO_PAGES) --profil bo_fr
	$(PY) proxsis repartir-annotation --items $(BO_PRIVE)/items_de.jsonl --annotateurs A1,A2 --double 6 \
		--seed 20261006 --public $(BO_ANNOT)/de --prive $(BO_PAGES)/de --profil bo_de_structure
	$(PY) proxsis projets-radar --public $(BO_PUBLIC) --out $(BO_PUBLIC)/projets_radar.json --md $(BO_RADAR_MD)
