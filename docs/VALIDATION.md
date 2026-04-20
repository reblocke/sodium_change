# Validation

## Current Gates

- `make stage-docs` mirrors the Python source of truth into the static app.
- `make test` runs the Python unit and smoke tests.
- `make verify` runs staging, formatting check, lint, and tests.
- CI currently runs pre-commit and pytest workflows.

## Validation Expectations

- Changes to uncertainty math require focused unit tests for intervals, probabilities, edge cases,
  and method combinations.
- Changes to default variability values require `docs/VARIABILITY.md` updates and tests that still
  load the defaults.
- Changes to the static app require staging and an offline smoke check of `docs/index.html` or
  `make serve`.
- Any assumption change that affects interpretation must be recorded in `docs/SPEC.md`,
  `docs/DECISIONS.md`, or an ADR.

## Out Of Scope

Passing these gates does not establish clinical validation, local laboratory calibration, or
regulatory clearance.
