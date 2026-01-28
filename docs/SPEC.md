# Sodium ΔNa Uncertainty Calculator — Specification

## Purpose
Provide a static, client-side tool to quantify measurement uncertainty in the change between
two sodium measurements. The app runs on GitHub Pages and uses in-browser Python (Pyodide).

## Inputs
- Na1 and Na2 (mmol/L)
- Method for each measurement: central lab (indirect ISE) or i-STAT (direct ISE)
- Context toggle:
  - Analytic repeatability (same specimen, analytic-only variability)
  - Sequential draws (two samples)
- Confidence interval level (default 95%)
- Optional toggle: scale σ with Na (assume constant CV, Na_ref = 140)
- Advanced settings: LoA half-widths or per-measurement σ overrides

## Measurement model
- Observed sodium values are noisy measurements of latent true values with independent
  normal errors.
- LoA half-widths represent paired differences for two independent measurements.
- Optional CV scaling: when enabled, σ is multiplied by (Na / Na_ref).
- For sequential draws: true ΔNa distribution is Normal with mean (Na2 − Na1) and variance
  σ1² + σ2².
- For analytic repeatability: a single true value is estimated from both measurements;
  true ΔNa is identically 0. The observed difference distribution reflects measurement
  noise, and the UI reports a two-sided tail probability for the observed ΔNa under the
  same-sample null.

## Outputs
- Summary statistics (mean, SD, CI) for true Na1, true Na2, and true ΔNa.
- Observed ΔNa and optional probabilities (ΔNa &gt; 0, |ΔNa| &gt; threshold).
- In analytic repeatability mode: P(|ΔNa| ≥ observed | same sample).
- Plots for Na1, Na2, and ΔNa distributions.

## Implementation notes
- Core math lives in `src/sodium_uncertainty/` and is unit-tested.
- Browser UI loads Pyodide, passes inputs to Python (`docs/app.py`), and renders charts in
  JavaScript.
- Default parameters are sourced from `data/variability_defaults.json` and copied to
  `docs/variability_defaults.json` for the browser.
