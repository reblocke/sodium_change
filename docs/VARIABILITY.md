# Variability Defaults

## Summary

Default variability parameters are LoA half-widths for paired measurements, expressed in mmol/L.
They are committed in `data/variability_defaults.json` and copied to
`docs/variability_defaults.json` for the static browser app.

These defaults are intentionally editable starting values. They are not a substitute for local
laboratory validation, analyzer-specific quality data, or institution-specific specimen-handling
performance data.

## Defaults table

| Context | Method | LoA half-width (mmol/L) | Implied per-measurement σ (mmol/L) | Provenance status |
| --- | --- | ---: | ---: | --- |
| Analytic repeatability | Central lab (indirect ISE) | 2.8 | 1.01 | Project v1 default from owner evidence review |
| Analytic repeatability | i-STAT (direct ISE) | 2.2 | 0.79 | Project v1 default from owner evidence review |
| Sequential draws | Central lab (indirect ISE) | 5.8 | 2.09 | Project v1 default from owner evidence review |
| Sequential draws | i-STAT (direct ISE) | 5.8 | 2.09 | Project v1 default from owner evidence review |

## Conversion

LoA half-widths are interpreted as 95% limits of agreement for paired independent measurements.
For equal per-measurement standard deviations within a row:

```text
SD_diff = LoA half-width / 1.96
σ = SD_diff / sqrt(2)
σ = LoA half-width / (1.96 × sqrt(2))
```

## Interpretation by context

- Analytic repeatability values represent same-specimen repeat measurement variability.
- Sequential-draw values represent total per-draw variability for two separate specimens, folding in
  collection, handling, and analytic components.
- Optional app-level constant-CV scaling multiplies σ by `observed Na / reference Na`, with default
  reference Na = 140 mmol/L.

## Provenance limits

The repository does not currently include a machine-readable bibliography or primary-source
extraction table for these values. Treat the values as documented project defaults rather than
published constants. If local or literature-derived values are substituted, update this file and
`data/variability_defaults.json` in the same change, and record the source, retrieval date, and any
conversion steps used.
