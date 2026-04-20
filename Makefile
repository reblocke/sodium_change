.DEFAULT_GOAL := help

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
SERVE_PYTHON ?= python3
PORT ?= 8000

.PHONY: help
help:
	@echo "Targets:"
	@echo "  stage-docs  Copy src/sodium_uncertainty into docs/sodium_uncertainty"
	@echo "  fmt         Format code (ruff)"
	@echo "  fmt-check   Check formatting (ruff)"
	@echo "  lint        Lint code (ruff)"
	@echo "  test        Run tests (pytest)"
	@echo "  serve       Stage and serve the static app locally"
	@echo "  verify      Run staging, format check, lint, and tests"
	@echo "  clean       Remove local caches"

.PHONY: stage-docs
stage-docs:
	$(PYTHON) scripts/stage_docs_python.py

.PHONY: fmt
fmt:
	$(PYTHON) -m ruff format .

.PHONY: fmt-check
fmt-check:
	$(PYTHON) -m ruff format --check .

.PHONY: lint
lint:
	$(PYTHON) -m ruff check .

.PHONY: test
test:
	$(PYTHON) -m pytest -q

.PHONY: serve
serve: stage-docs
	$(SERVE_PYTHON) -m http.server --bind 127.0.0.1 --directory docs $(PORT)

.PHONY: verify
verify: stage-docs fmt-check lint test

.PHONY: clean
clean:
	@rm -rf .pytest_cache .ruff_cache htmlcov
	@find src tests scripts docs/sodium_uncertainty -type d -name __pycache__ -prune -exec rm -rf {} +
	@find src tests scripts docs/sodium_uncertainty -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
