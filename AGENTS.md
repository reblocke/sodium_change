# Codex AGENTS

## Purpose
- This repository contains the Sodium delta-Na uncertainty calculator and static GitHub Pages app.
- The Python package is `sodium_uncertainty`; the static browser app is served from `docs/` and imports a staged package copy through Pyodide.
- The project explains measurement uncertainty for education and clinical reasoning support only.

## Repo Map
- `src/sodium_uncertainty/` - pure Python source of truth for the uncertainty model.
- `docs/` - GitHub Pages app, browser entrypoint, styles, and staged Python package.
- `scripts/stage_docs_python.py` - mirrors package code and defaults into `docs/` for Pyodide.
- `data/variability_defaults.json` - source default variability parameters.
- `tests/` - unit and smoke tests for the Python core and static assets.
- `.agents/skills/` - focused local workflows for recurring agent tasks.

## Commands
- Stage browser Python: `make stage-docs`
- Format: `make fmt`
- Format check: `make fmt-check`
- Lint: `make lint`
- Tests: `make test`
- Full verification: `make verify`
- Local web app: `make serve`

## Authority
1. `docs/SPEC.md`.
2. `docs/VARIABILITY.md` and `data/variability_defaults.json`.
3. `docs/DECISIONS.md`, clinical/privacy/public-copy docs, and this file.
4. Existing code and tests.

If implementation and documentation disagree, preserve documented math semantics unless the task explicitly changes them, then record the decision in `docs/DECISIONS.md` or a new ADR under `docs/adr/`.

## Working Rules
- Before non-trivial edits, state assumptions, ambiguities, tradeoffs, a brief plan, risks, and verification commands.
- Keep changes small and directly tied to the request; do not make drive-by refactors.
- Keep `src/sodium_uncertainty/` as the calculation source of truth; run staging rather than hand-editing duplicated Python under `docs/sodium_uncertainty/`.
- Preserve the distinction between analytic repeatability and sequential draws.
- Do not impose a physiologic prior on sodium change.
- Keep computation client-side; do not add a backend, telemetry, PHI storage, or URL persistence of patient values.
- Any default variability value must remain traceable in `docs/VARIABILITY.md`.

## Skill Triggers
- Planning a non-trivial change: `.agents/skills/implementation-strategy/SKILL.md`.
- Verifying a code change: `.agents/skills/code-change-verification/SKILL.md`.
- Updating docs after behavior/workflow changes: `.agents/skills/docs-sync/SKILL.md`.
- Preparing PR text: `.agents/skills/pr-draft-summary/SKILL.md`.
- Reviewing numerical/statistical behavior: `.agents/skills/scientific-validation/SKILL.md`.
- Changing the static browser app or Pyodide staging: `.agents/skills/static-browser-pyodide-verification/SKILL.md`.
- Editing clinical, privacy, public-copy, or provenance surfaces: use the matching focused skill in `.agents/skills/`.

## Done Criteria
- `make verify` passes locally.
- Browser-facing package changes are staged and verified.
- Defaults, clinical scope, privacy posture, and public copy remain documented when they change.
- The final report names changed files, verification commands, and any remaining risks.
