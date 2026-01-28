# Decisions

## Analytic repeatability interpretation
The analytic repeatability scenario assumes a single true sodium for both measurements, so
true ΔNa is identically 0. The UI also reports the expected observed difference distribution
from measurement noise. The ticket test case referencing ΔNa = 3 mmol/L was interpreted as
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
