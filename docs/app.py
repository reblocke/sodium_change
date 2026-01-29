import json
from typing import Any

from sodium_uncertainty.defaults import resolve_sigma
from sodium_uncertainty.model import (
    chance_probability_under_null,
    make_curve,
    normal_cdf,
    normal_ci,
    posterior_same_sample,
    posterior_sequential_draws,
    qualitative_bucket,
    same_sample_p_value,
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


def _intervals(mean: float, sd: float) -> list[dict[str, float]]:
    levels = (0.5, 0.95, 0.99)
    intervals = []
    for level in levels:
        low, high = normal_ci(mean, sd, level)
        intervals.append({"level": level, "low": low, "high": high})
    return intervals


def _detail_entry(
    entry: dict[str, Any],
    sigma_used: float,
    value: float,
    scale_with_na: bool,
    na_ref: float,
) -> dict[str, Any]:
    loa_half = entry.get("loa_half_pair")
    sigma_override = entry.get("sigma")
    override_used = sigma_override not in (None, "")
    scale_factor = value / na_ref if scale_with_na else 1.0
    sigma_raw = sigma_used / scale_factor if scale_factor != 0 else sigma_used
    detail: dict[str, Any] = {
        "loa_half_pair": loa_half,
        "sigma_override": sigma_override,
        "override_used": override_used,
        "sigma_used": sigma_used,
        "sigma_raw": sigma_raw,
        "scale_factor": scale_factor,
    }
    if loa_half not in (None, ""):
        sd_diff = float(loa_half) / 1.96
        detail["sd_diff"] = sd_diff
        detail["sigma_from_loa"] = sd_diff / (2**0.5)
    return detail


def compute_from_json(payload_json: str) -> str:
    payload = json.loads(payload_json)
    errors: list[str] = []
    warnings: list[str] = []

    y1 = _parse_float(payload.get("y1"), "Na1", errors)
    y2 = _parse_float(payload.get("y2"), "Na2", errors)
    ci_level = _parse_float(payload.get("ci_level"), "CI level", errors)
    threshold = _parse_float(payload.get("threshold"), "Threshold", errors)
    scale_with_na = payload.get("scale_with_na", False)
    na_ref = _parse_float(payload.get("na_ref", 140), "Reference Na", errors)

    if y1 is not None and (y1 < 100 or y1 > 170):
        warnings.append("Na1 is outside typical physiologic ranges.")
    if y2 is not None and (y2 < 100 or y2 > 170):
        warnings.append("Na2 is outside typical physiologic ranges.")
    if ci_level is not None and not 0 < ci_level < 1:
        errors.append("CI level must be between 0 and 1.")
    if threshold is not None and threshold < 0:
        errors.append("Threshold must be non-negative.")
    if na_ref is not None and na_ref <= 0:
        errors.append("Reference Na must be positive.")

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

    if scale_with_na:
        sigma1 *= y1 / na_ref
        sigma2 *= y2 / na_ref

    sigma_delta = (sigma1**2 + sigma2**2) ** 0.5

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

    p_chance = chance_probability_under_null(y2 - y1, sigma_delta)
    bucket_key, bucket_label = qualitative_bucket(p_chance)
    probabilities = {
        "delta_gt_zero": _probability_gt_zero(result.delta_true.mean, result.delta_true.sd),
        "delta_abs_gt_threshold": _probability_abs_gt_threshold(
            result.delta_true.mean,
            result.delta_true.sd,
            threshold,
        ),
        "same_sample_p": same_sample_p_value(y1, y2, sigma1, sigma2)
        if context == "analytic_repeatability"
        else None,
        "chance_under_null": p_chance,
        "chance_bucket_key": bucket_key,
        "chance_bucket_label": bucket_label,
    }

    curves = {
        "na1": make_curve(result.na1.mean, result.na1.sd),
        "na2": make_curve(result.na2.mean, result.na2.sd),
        "delta_true": make_curve(result.delta_true.mean, result.delta_true.sd),
        "delta_observed": make_curve(delta_observed.mean, delta_observed.sd),
        "delta_null": make_curve(0.0, sigma_delta),
        "na1_obs": make_curve(y1, sigma1),
        "na2_obs": make_curve(y2, sigma2),
    }
    intervals = {
        "na1": _intervals(result.na1.mean, result.na1.sd),
        "na2": _intervals(result.na2.mean, result.na2.sd),
        "delta_true": _intervals(result.delta_true.mean, result.delta_true.sd),
        "delta_observed": _intervals(delta_observed.mean, delta_observed.sd),
        "delta_null": _intervals(0.0, sigma_delta),
        "na1_obs": _intervals(y1, sigma1),
        "na2_obs": _intervals(y2, sigma2),
    }
    details = {
        "context": context,
        "method1": method1,
        "method2": method2,
        "sigma1": sigma1,
        "sigma2": sigma2,
        "sigma_delta": sigma_delta,
        "scale_with_na": scale_with_na,
        "na_ref": na_ref,
        "entry1": _detail_entry(
            params["defaults"][context][method1], sigma1, y1, scale_with_na, na_ref
        ),
        "entry2": _detail_entry(
            params["defaults"][context][method2], sigma2, y2, scale_with_na, na_ref
        ),
    }

    return json.dumps(
        {
            "errors": [],
            "warnings": warnings,
            "inputs": {"y1": y1, "y2": y2, "sigma1": sigma1, "sigma2": sigma2},
            "context": context,
            "ci_level": ci_level,
            "threshold": threshold,
            "observed_delta": result.observed_delta,
            "na1": result.na1.__dict__,
            "na2": result.na2.__dict__,
            "delta_true": result.delta_true.__dict__,
            "delta_observed": delta_observed.__dict__,
            "probabilities": probabilities,
            "curves": curves,
            "intervals": intervals,
            "details": details,
        }
    )
