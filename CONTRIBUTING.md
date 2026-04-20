# Contributing

## Development setup

Use Python 3.11. Conda/mamba users can create the documented environment:

```bash
mamba env create -f environment.yml   # or: conda env create -f environment.yml
mamba activate proj-env               # or: conda activate proj-env
```

Virtual environment users can install the package and dev tools directly:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . "pytest>=8" "ruff>=0.6" "pre-commit>=3"
```

## Local hooks

Install hooks once per clone:

```bash
PRE_COMMIT_HOME=.cache/pre-commit pre-commit install
PRE_COMMIT_HOME=.cache/pre-commit pre-commit install --hook-type pre-push
```

The commit hook handles fast formatting/lint hygiene. The pre-push hook runs `make test`.

## Checks

Use the Makefile targets rather than ad hoc commands:

```bash
make stage-docs   # mirror src package/defaults into docs/ for Pyodide
make fmt          # format Python files
make fmt-check    # verify Python formatting
make lint         # Ruff lint
make test         # pytest
make verify       # stage docs, format-check, lint, and test
make serve        # serve docs/ locally on http://127.0.0.1:8000
```

Run `make verify` before pushing. For browser-facing changes, also run `make serve` and manually
check that the hosted-page workflow still loads defaults and calculates without console errors.

## Change discipline

- Keep PRs small and focused.
- Keep calculation logic in `src/sodium_uncertainty/`.
- Do not hand-edit generated package files under `docs/sodium_uncertainty/`; run `make stage-docs`.
- Update docs in the same change when behavior, assumptions, defaults, validation, or public copy
  changes.
- Add tests for changed math, changed defaults, browser contract changes, and staging behavior.

## Clinical and privacy boundaries

- Do not commit PHI/PII or real patient examples.
- Use synthetic sodium examples in tests and docs.
- Do not add telemetry, backend storage, URL persistence of entered values, uploads, or external data
  submission without an explicit documented decision.
- Keep public wording educational; do not claim clinical validation, regulatory clearance, diagnosis,
  treatment guidance, or local laboratory calibration.

## Defaults and provenance

Default variability values live in `data/variability_defaults.json`; their human-readable summary
lives in `docs/VARIABILITY.md`. Any default change must update both files and record the evidence,
retrieval date, and conversion assumptions used.
