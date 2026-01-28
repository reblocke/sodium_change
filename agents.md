# Sodium ΔNa Uncertainty Calculator — GitHub Pages (Codex instructions)

## Continuity Ledger (compaction-safe)
Maintain a single Continuity Ledger for this workspace in `http://CONTINUITY.md`. The ledger is the canonical session briefing designed to survive context compaction; do not rely on earlier chat text unless it’s reflected in the ledger.

### How it works
- At the start of every assistant turn: read `http://CONTINUITY.md`, update it to reflect the latest goal/constraints/decisions/state, then proceed with the work.
- Update `http://CONTINUITY.md` again whenever any of these change: goal, constraints/assumptions, key decisions, progress state (Done/Now/Next), or important tool outcomes.
- Keep it short and stable: facts only, no transcripts. Prefer bullets. Mark uncertainty as `UNCONFIRMED` (never guess).
- If you notice missing recall or a compaction/summary event: refresh/rebuild the ledger from visible context, mark gaps `UNCONFIRMED`, ask up to 1–3 targeted questions, then continue.

### `functions.update_plan` vs the Ledger
- `functions.update_plan` is for short-term execution scaffolding while you work (a small 3–7 step plan with pending/in_progress/completed).
- `http://CONTINUITY.md` is for long-running continuity across compaction (the “what/why/current state”), not a step-by-step task list.
- Keep them consistent: when the plan or state changes, update the ledger at the intent/progress level (not every micro-step).

### In replies
- Begin with a brief “Ledger Snapshot” (Goal + Now/Next + Open Questions). Print the full ledger only when it materially changes or when the user asks.

### `http://CONTINUITY.md` format (keep headings)
- Goal (incl. success criteria):
- Constraints/Assumptions:
- Key decisions:
- State:
- Done:
- Now:
- Next:
- Open questions (UNCONFIRMED if needed):
- Working set (files/ids/commands):


## Goal
Build a static, browser-run web app (hosted on GitHub Pages) that helps users interpret the *uncertainty* in the change between two sodium measurements.

Inputs:
- Two sodium values (mmol/L).
- For each value: measurement source/method:
  - **Central lab BMP/CMP** (indirect ISE; typical hospital core lab).
  - **i‑STAT / blood gas analyzer** sodium (direct ISE; point-of-care).
- A toggle/checkbox indicating whether the two values represent:
  - **Analytic repeatability** (two runs on the *same* sample; no physiologic change assumed), or
  - **Two sequential draws** (separate samples; physiologic change allowed/unknown).

Outputs:
- A distribution for each underlying “true” sodium consistent with each observed reading and the selected measurement uncertainty model.
- A distribution (and 95% interval) for the **true change** ΔNa between timepoints.
- Clear, minimal visualizations (density curves and/or histograms) for:
  - Na₁ true,
  - Na₂ true,
  - ΔNa true.

Customization:
- Users can override default variability parameters (e.g., 95% limits of agreement or SDs) via an “Advanced settings” panel.

Implementation constraints:
- Must run fully client-side (no server, no PHI).
- Computation implemented in Python executed in-browser (Pyodide/PyScript).
- Core math must be testable outside the browser (pure Python module with unit tests).


## Authority hierarchy (resolve conflicts in this order)
1) `docs/SPEC.md` (intended product behavior and mathematical model; create if missing)
2) `docs/VARIABILITY.md` + `data/variability_defaults.json` (default parameters + citations)
3) UI copy in `docs/index.html` (user-facing language)
4) Any ad-hoc notes/issues

When implementation details are ambiguous:
- implement the simplest version consistent with (1),
- document decisions and tradeoffs in `docs/DECISIONS.md`.


## Non-negotiables
### Measurement model semantics
- **No physiologic prior:** Do not impose assumptions about how sodium “should” change. Treat each observed value strictly as information about its corresponding true value under a measurement-error model.
- **Explicit scenario switch:**
  - **Analytic repeatability (same sample):** assume a *single* true sodium `x` measured twice (`y₁`, `y₂`) with independent errors. Report:
    - posterior for `x | y₁, y₂`,
    - expected distribution of the observed difference due to measurement noise,
    - and (optionally) the implied distribution for ΔNa_true, which is identically 0 under the “same sample” assumption.
  - **Sequential draws (two samples):** allow two true values (`x₁`, `x₂`) with independent priors. Report posterior for Δ = x₂ − x₁.

### Converting “limits of agreement” to per-measurement uncertainty
- Default inputs should be **95% limits of agreement (LoA)** for *pairwise differences* unless otherwise specified.
- If LoA are reported as `bias ± 1.96·SD_diff` for (measurement A − measurement B):
  - `SD_diff = (upper − lower) / 3.92`
  - For two independent measurements with per-measurement SDs σ₁ and σ₂:
    - `SD_diff² = σ₁² + σ₂²`
  - If the two measurements are from the same method and assumed equal variance:
    - `σ = SD_diff / √2`
- Support optional non-zero **bias** (mean difference) in the parameter model; default bias should be 0 unless literature indicates otherwise.

### Parametric first, Monte Carlo optional
- Prefer an analytic/parametric solution for posteriors and 95% intervals under Normal error assumptions.
- Monte Carlo simulation (optional) is allowed for visualization and cross-checks, but must agree with the parametric results (within tolerance).

### Execution hygiene
- Every milestone ends with:
  - run unit tests (e.g., `pytest` for the pure-Python core),
  - update small docs/artifacts as needed (e.g., `docs/VARIABILITY.md`, `docs/DECISIONS.md`),
  - commit with a clear message.


## Reproducibility & safety
- No PHI, no analytics trackers, no external API calls.
- Keep dependencies minimal (prefer Python standard library; avoid SciPy in-browser unless there is a strong, documented reason).
- Any default variability values must be traceable to a citation in `docs/VARIABILITY.md`.
- The app must display an educational disclaimer (not medical advice; measurement uncertainty only).


## Repository / app layout
Recommended (GitHub Pages from `docs/`):
- `docs/`
  - `index.html` (UI shell, loads Pyodide/PyScript, wires inputs/outputs)
  - `app.py` (browser-facing Python entrypoint; orchestrates calls to core)
  - `assets/` (icons/css; optional)
- `src/`
  - `sodium_uncertainty/`
    - `model.py` (core distributions, LoA→σ conversion, CI computation)
    - `defaults.py` (loads defaults from JSON; validation)
    - `types.py` (small dataclasses for parameters/results)
- `data/`
  - `variability_defaults.json` (all defaults; schema-validated)
- `tests/`
  - `test_model.py`
  - `test_defaults.py`
- `docs/VARIABILITY.md` (what each default means, source, date, unit)
- `docs/DECISIONS.md` (non-obvious choices + rationale)


## Definition of done (per milestone)
- Pure-Python unit tests pass locally.
- Browser build works offline (open `docs/index.html` and compute results without a backend).
- For each supported scenario (lab/lab, iStat/iStat, lab/iStat), outputs are:
  - numerically stable,
  - unit-consistent (mmol/L),
  - and match sanity checks (e.g., wider σ ⇒ wider Δ interval).
- Defaults are editable in the UI and persist for the session (no storage required unless explicitly added).
- Documentation updated (`docs/SPEC.md`, `docs/VARIABILITY.md`, `docs/DECISIONS.md` as applicable).
