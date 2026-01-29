# Sodium ΔNa Uncertainty Calculator

A static, browser-run web app that helps interpret uncertainty in the change between two sodium
measurements. It models measurement error for common lab methods and shows distributions for
Na1, Na2, and the true delta (ΔNa). The app runs fully client-side (Pyodide/PyScript) with no
backend and no PHI.

## What it does

- Accepts two sodium values (mmol/L).
- Lets you choose the measurement method for each value:
  - Central lab BMP/CMP (indirect ISE)
  - i-STAT / blood gas analyzer (direct ISE)
- Supports two scenarios:
  - Analytic repeatability (same sample measured twice)
  - Sequential draws (two different samples)
- Computes distributions and 95% intervals for:
  - Na1 true
  - Na2 true
  - ΔNa true
- Defaults are editable via an Advanced settings panel.

## Local use (web app)

Option A: open the static page directly

- Open `docs/index.html` in your browser.

Option B: run a simple local web server (recommended for Pyodide caching)

```bash
cd docs
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Local dev setup (Python core + tests)

Conda/mamba (recommended by `environment.yml`):

```bash
mamba env create -f environment.yml   # or: conda env create -f environment.yml
mamba activate proj-env               # or: conda activate proj-env
```

Or, use the repo venv (Python 3.11):

```bash
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install \"ruff>=0.6\" \"pytest>=8\" \"pre-commit>=3\" ipykernel jupyter numpy pandas matplotlib pyarrow
```

Run checks/tests:

```bash
ruff check .
pytest -q
```

Install pre-commit hooks:

```bash
PRE_COMMIT_HOME=.cache/pre-commit pre-commit install
```

## Hosted version (GitHub Pages)

The app is published from the `docs/` folder. To enable hosting:

1) In GitHub, go to Settings → Pages.
2) Set Source to the `main` branch and the `/docs` folder.
3) Save.

Your published URL will be:

```text
https://<github-username>.github.io/<repo-name>/
```

## Repository layout

```
├── docs/                     # GitHub Pages site (index.html + app.py)
├── src/sodium_uncertainty/   # Core model (pure Python, testable)
├── data/                     # Default variability values (JSON)
├── tests/                    # Unit tests
├── environment.yml           # Dev environment (conda/mamba)
├── docs/SPEC.md              # Behavior and math model
├── docs/VARIABILITY.md       # Default parameters + citations
└── docs/DECISIONS.md         # Non-obvious choices and rationale
```

## Defaults and variability

- Defaults live in `data/variability_defaults.json`.
- `docs/VARIABILITY.md` explains each default and the source/citation.
- The model converts 95% limits of agreement into per-measurement sigma under
  independence assumptions.

## Background / Justification

**Why sodium results can “change” even when physiology doesn’t.** Lab results are usually
displayed as a single number. That presentation encourages the false idea that the measurement
is exact. In reality, every clinical measurement has unavoidable uncertainty, and small changes
can reflect noise rather than physiology.

**Where the uncertainty comes from.** Variation comes from more than the analyzer. It can come
from specimen collection and handling (preanalytical factors), instrument imprecision
(analytical factors), and true within-person fluctuation (biological variation).

**What “reference change value” means (the BMJ idea).** A standard way to interpret serial
tests is to ask: “How big does the difference need to be before it’s unlikely to be chance?”
This is often framed as a reference change value (RCV) based on analytical and within-subject
biological variation.

**What this tool does instead.** This tool treats each sodium value as a range of plausible
true values consistent with the chosen limits of agreement, then derives a distribution for
the plausible true change (ΔNa), assuming independent random errors. It can also report how
often a difference this large could occur by chance under “no true change.”

**Caveats.** This tool does not correct for systematic bias between methods or preanalytical
artifacts unless you explicitly incorporate them into the parameters. Point-of-care devices
often have larger analytical variation than accredited central laboratory instruments, and
your local lab’s performance may differ from published estimates.

References / further reading: BMJ practice pointers on interpreting serial test results
provide conceptual inspiration, but the math here differs and does not use biologic-variation
RCV calculations.

## Disclaimer

This tool is for education and measurement-uncertainty intuition only. It is not medical advice.

## How to cite

See `CITATION.cff` or the GitHub “Cite this repository” box.

## License

See `LICENSE` for terms.
