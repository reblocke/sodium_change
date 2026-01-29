# Decisions

## Analytic repeatability interpretation
The analytic repeatability scenario assumes a single true sodium for both measurements, so
true ΔNa is identically 0. The UI reports the expected observed ΔNa distribution from
measurement noise and a two-sided tail probability P(|ΔNa| ≥ observed | same sample) as the
null-hypothesis check. The ticket test case referencing ΔNa = 3 mmol/L was interpreted as
applying to sequential draws to preserve this requirement.

## Plotting approach
Charts are rendered with a lightweight HTML canvas function to avoid external JS plotting
dependencies. This keeps the static site small and compliant with the “no external API
calls” guidance.

## Browser packaging
`src/sodium_uncertainty` is mirrored into `docs/sodium_uncertainty` so Pyodide can import the
same model code when the site is hosted from `docs/`. The docs copy is a direct mirror and
should stay in sync with the core package.

## Pyodide delivery
Pyodide is loaded from the official CDN to keep the repository lightweight. Offline usage
requires the assets to be cached by the browser or bundled separately.

## Na-dependent σ toggle
An optional "scale σ with Na" toggle assumes constant CV by scaling σ linearly with Na
relative to a reference value (default 140 mmol/L). This provides an opt-in heteroscedastic
model without committing to device-specific curves.

## BMJ-style interpretation layer
The app adds a qualitative interpretation label based on the no-change chance probability.
This is a communication layer only and does not alter the quantitative model.
