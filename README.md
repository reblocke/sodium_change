# Sodium ΔNa Uncertainty Calculator

A static, browser-run educational tool for reasoning about measurement uncertainty in the
change between two sodium results. The app models each measured sodium as a noisy observation,
uses user-selected variability parameters, and reports distributions for plausible true Na1,
true Na2, and true change in sodium (ΔNa).

- Hosted app: <https://reblocke.github.io/sodium_change/>
- Repository: <https://github.com/reblocke/sodium_change>
- Package name: `sodium-uncertainty`
- Python package: `sodium_uncertainty`

## What it does

- Accepts two sodium values in mmol/L.
- Lets users choose the method for each result:
  - Central lab, indirect ion-selective electrode (ISE)
  - i-STAT/direct ISE
- Supports two uncertainty contexts:
  - Analytic repeatability: same specimen measured twice; true ΔNa is fixed at 0, and the app
    reports how often the observed difference could occur from measurement noise alone.
  - Sequential draws: two separate specimens; the app estimates a plausible true ΔNa distribution
    with SD `sqrt(σ1² + σ2²)`.
- Reports observed ΔNa, a no-change chance probability, qualitative interpretation label,
  confidence intervals, and parameter details.
- Draws distributions for Na1, Na2, and ΔNa in the browser.
- Allows advanced LoA half-width edits, per-measurement σ overrides, JSON import/export of
  parameters, and optional σ scaling with sodium concentration.

## What it does not do

- It does not diagnose, treat, recommend therapy, or replace clinical judgment.
- It does not estimate physiologic priors or expected clinical direction of sodium change.
- It does not implement biologic-variation reference change value (RCV) calculations.
- It does not correct for systematic method bias, specimen artifacts, contamination, dilution,
  or local analyzer calibration unless the user explicitly changes the variability parameters.
- It does not intentionally store, transmit, or persist patient-entered sodium values.

## Hosted use

Open the GitHub Pages deployment:

```text
https://reblocke.github.io/sodium_change/
```

The hosted page is served from the repository `docs/` folder. Calculations run client-side in the
browser through Pyodide. Pyodide itself is loaded from the jsDelivr CDN, so first load requires
network access to that CDN.

## Local use

Recommended local browser workflow:

```bash
make serve
```

Then open:

```text
http://127.0.0.1:8000
```

The `make serve` target stages the Python package into `docs/sodium_uncertainty/` before starting a
local static server. Avoid relying on direct `file://` opening because browser fetch behavior can
break Pyodide asset loading.

## Development setup

Requirements:

- Python 3.11
- `make`
- Internet access for first-time installation of Python packages and pre-commit hooks

Conda/mamba setup:

```bash
mamba env create -f environment.yml   # or: conda env create -f environment.yml
mamba activate proj-env               # or: conda activate proj-env
```

Virtual environment setup:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . "pytest>=8" "ruff>=0.6" "pre-commit>=3"
```

Useful commands:

```bash
make stage-docs   # copy src/sodium_uncertainty into docs/ for Pyodide
make test         # run pytest
make lint         # run Ruff linting
make fmt          # format Python files with Ruff
make fmt-check    # check formatting without rewriting files
make verify       # stage docs, check formatting, lint, and test
make serve        # stage docs and serve docs/ locally on port 8000
```

Install local Git hooks:

```bash
PRE_COMMIT_HOME=.cache/pre-commit pre-commit install
PRE_COMMIT_HOME=.cache/pre-commit pre-commit install --hook-type pre-push
```

The commit hook runs formatting/lint hygiene through pre-commit. The pre-push hook runs `make test`
so pushes are gated without slowing every commit.

## Repository layout

```text
├── src/sodium_uncertainty/       # Source-of-truth Python package
├── docs/                         # GitHub Pages app and staged Pyodide package copy
├── data/variability_defaults.json # Default LoA half-width parameters
├── scripts/stage_docs_python.py  # Stages package/defaults into docs/
├── tests/                        # Unit, contract, and static-staging tests
├── .github/workflows/            # pre-commit and pytest CI workflows
├── docs/SPEC.md                  # Measurement model and browser contract
├── docs/VARIABILITY.md           # Default variability values and provenance limits
├── docs/VALIDATION.md            # Current verification gates and validation limits
├── docs/CLINICAL_SCOPE.md        # Intended educational use and non-goals
├── docs/PRIVACY.md               # Client-side/no-persistence posture
└── docs/DECISIONS.md             # Durable implementation and interpretation decisions
```

## Default variability values

Defaults live in `data/variability_defaults.json` and are staged to
`docs/variability_defaults.json` for the browser. They are LoA half-widths for paired measurements
in mmol/L.

| Context | Method | LoA half-width | Implied per-measurement σ |
| --- | --- | ---: | ---: |
| Analytic repeatability | Central lab indirect ISE | 2.8 | 1.01 |
| Analytic repeatability | i-STAT/direct ISE | 2.2 | 0.79 |
| Sequential draws | Central lab indirect ISE | 5.8 | 2.09 |
| Sequential draws | i-STAT/direct ISE | 5.8 | 2.09 |

The conversion is:

```text
σ = LoA half-width / (1.96 × sqrt(2))
```

These values are project defaults for demonstration and sensitivity analysis. They are not local
laboratory validation data and should be replaced or overridden when institution-specific
performance data are available.

## Measurement model summary

The core model assumes independent, normally distributed measurement errors. For sequential draws,
ΔNa is modeled as:

```text
Δtrue ~ Normal(Na2 - Na1, sqrt(σ1² + σ2²))
```

For analytic repeatability, the two measurements are treated as repeated measurements of the same
specimen. The true ΔNa is therefore 0, and the reported no-change probability is the two-sided tail
probability of observing a difference at least as large as the observed ΔNa under measurement noise.

Optional constant-CV scaling multiplies each σ by:

```text
observed Na / reference Na
```

with default reference Na = 140 mmol/L.

## Background / Justification

**Why sodium results can “change” even when physiology does not.** Lab results are usually
displayed as a single number. That presentation encourages the false idea that the measurement is
exact. In reality, every clinical measurement has unavoidable uncertainty, and small changes can
reflect noise rather than physiology.

**Where uncertainty comes from.** Variation can come from specimen collection and handling
(preanalytical factors), instrument imprecision (analytical factors), and true within-person
fluctuation (biological variation).

**What reference change value means.** A standard way to interpret serial tests is to ask how large
a difference must be before it is unlikely to be chance. This is often framed as a reference change
value based on analytical and within-subject biological variation.

**What this tool does instead.** This tool treats each sodium value as a range of plausible true
values consistent with the chosen limits of agreement, then derives a distribution for plausible
true ΔNa under independent random errors. It also reports how often a difference this large could
occur by chance under a no-true-change model.

**Caveats.** The tool does not correct for systematic bias between methods or preanalytical
artifacts unless those are explicitly incorporated into the parameters. Point-of-care and central
laboratory instruments can differ, and local performance may differ from these defaults.

## Validation and CI

Current automated checks verify Python math invariants, calculator JSON contract behavior, default
file loading, staged browser package consistency, Ruff formatting, and Ruff linting. CI runs these
checks on push and pull request through `.github/workflows/pre-commit.yml` and
`.github/workflows/tests.yml`.

Passing these checks does not establish clinical validation, regulatory clearance, or local
laboratory calibration.

## Citation

Citation metadata are in `CITATION.cff`. GitHub should render this through the repository “Cite
this repository” control. No DOI is currently assigned.

## License

MIT license. See `LICENSE` for terms.
