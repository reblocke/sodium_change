import json
from typing import Any

from sodium_uncertainty.defaults import resolve_sigma
from sodium_uncertainty.model import (
    make_curve,
    normal_cdf,
    posterior_same_sample,
    posterior_sequential_draws,
)


def _parse_float(value: Any, label: str, errors: list[str]) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{label} must be a number.")
        return None


def _probability_gt_zero(mean: float, sd: float) -> float:
    if sd == 0:
        return 1.0 if mean > 0 else 0.0
    return 1 - normal_cdf(0.0, mean, sd)


def _probability_abs_gt_threshold(mean: float, sd: float, threshold: float) -> float:
    if sd == 0:
        return 1.0 if abs(mean) > threshold else 0.0
    upper = 1 - normal_cdf(threshold, mean, sd)
    lower = normal_cdf(-threshold, mean, sd)
    return upper + lower


def compute_from_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    errors: list[str] = []
    warnings: list[str] = []

    y1 = _parse_float(payload.get("y1"), "Na1", errors)
    y2 = _parse_float(payload.get("y2"), "Na2", errors)
    ci_level = _parse_float(payload.get("ci_level"), "CI level", errors)
    threshold = _parse_float(payload.get("threshold"), "Threshold", errors)

    if y1 is not None and (y1 < 100 or y1 > 170):
        warnings.append("Na1 is outside typical physiologic ranges.")
    if y2 is not None and (y2 < 100 or y2 > 170):
        warnings.append("Na2 is outside typical physiologic ranges.")
    if ci_level is not None and not 0 < ci_level < 1:
        errors.append("CI level must be between 0 and 1.")
    if threshold is not None and threshold < 0:
        errors.append("Threshold must be non-negative.")

    if errors:
        return json.dumps({"errors": errors, "warnings": warnings})

    context = payload.get("context")
    method1 = payload.get("method1")
    method2 = payload.get("method2")
    params = payload.get("params")

    try:
        sigma1 = resolve_sigma(params, context, method1)
        sigma2 = resolve_sigma(params, context, method2)
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"errors": [str(exc)], "warnings": warnings})

    try:
        if context == "analytic_repeatability":
            result = posterior_same_sample(y1, y2, sigma1, sigma2, ci_level)
        elif context == "sequential_draws":
            result = posterior_sequential_draws(y1, y2, sigma1, sigma2, ci_level)
        else:
            return json.dumps({"errors": ["Invalid context selection."], "warnings": warnings})
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"errors": [str(exc)], "warnings": warnings})

    delta_observed = result.delta_observed or result.delta_true

    probabilities = {
        "delta_gt_zero": _probability_gt_zero(result.delta_true.mean, result.delta_true.sd),
        "delta_abs_gt_threshold": _probability_abs_gt_threshold(
            result.delta_true.mean,
            result.delta_true.sd,
            threshold,
        ),
    }

    curves = {
        "na1": make_curve(result.na1.mean, result.na1.sd),
        "na2": make_curve(result.na2.mean, result.na2.sd),
        "delta_true": make_curve(result.delta_true.mean, result.delta_true.sd),
        "delta_observed": make_curve(delta_observed.mean, delta_observed.sd),
    }

    return json.dumps(
        {
            "errors": [],
            "warnings": warnings,
            "context": context,
            "ci_level": ci_level,
            "observed_delta": result.observed_delta,
            "na1": result.na1.__dict__,
            "na2": result.na2.__dict__,
            "delta_true": result.delta_true.__dict__,
            "delta_observed": delta_observed.__dict__,
            "probabilities": probabilities,
            "curves": curves,
        }
    )
