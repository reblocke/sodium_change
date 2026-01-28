import math
from statistics import NormalDist
from typing import Iterable

from .types import NormalSummary, ScenarioResult

Z_95 = 1.96


def loa_half_pair_to_sigma(loa_half: float) -> float:
    if loa_half <= 0:
        raise ValueError("LoA half-width must be positive.")
    return loa_half / (Z_95 * math.sqrt(2))


def sigma_to_loa_half_pair(sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("Sigma must be positive.")
    return Z_95 * math.sqrt(2) * sigma


def normal_ci(mean: float, sd: float, level: float) -> tuple[float, float]:
    if sd < 0:
        raise ValueError("Standard deviation must be non-negative.")
    if not 0 < level < 1:
        raise ValueError("CI level must be between 0 and 1.")
    if sd == 0:
        return mean, mean
    z = NormalDist().inv_cdf(1 - (1 - level) / 2)
    return mean - z * sd, mean + z * sd


def summarize_normal(mean: float, sd: float, level: float) -> NormalSummary:
    ci_low, ci_high = normal_ci(mean, sd, level)
    return NormalSummary(mean=mean, sd=sd, ci_low=ci_low, ci_high=ci_high)


def posterior_same_sample(
    y1: float,
    y2: float,
    sigma1: float,
    sigma2: float,
    ci_level: float,
) -> ScenarioResult:
    if sigma1 <= 0 or sigma2 <= 0:
        raise ValueError("Sigma values must be positive.")
    weight1 = 1 / (sigma1**2)
    weight2 = 1 / (sigma2**2)
    combined_mean = (y1 * weight1 + y2 * weight2) / (weight1 + weight2)
    combined_sd = math.sqrt(1 / (weight1 + weight2))
    na_summary = summarize_normal(combined_mean, combined_sd, ci_level)
    delta_true = summarize_normal(0.0, 0.0, ci_level)
    delta_noise_sd = math.sqrt(sigma1**2 + sigma2**2)
    delta_observed = summarize_normal(0.0, delta_noise_sd, ci_level)
    return ScenarioResult(
        na1=na_summary,
        na2=na_summary,
        delta_true=delta_true,
        observed_delta=y2 - y1,
        delta_observed=delta_observed,
    )


def posterior_sequential_draws(
    y1: float,
    y2: float,
    sigma1: float,
    sigma2: float,
    ci_level: float,
) -> ScenarioResult:
    if sigma1 <= 0 or sigma2 <= 0:
        raise ValueError("Sigma values must be positive.")
    na1 = summarize_normal(y1, sigma1, ci_level)
    na2 = summarize_normal(y2, sigma2, ci_level)
    delta_sd = math.sqrt(sigma1**2 + sigma2**2)
    delta_true = summarize_normal(y2 - y1, delta_sd, ci_level)
    return ScenarioResult(
        na1=na1,
        na2=na2,
        delta_true=delta_true,
        observed_delta=y2 - y1,
        delta_observed=None,
    )


def normal_pdf(x: float, mean: float, sd: float) -> float:
    if sd <= 0:
        raise ValueError("Standard deviation must be positive.")
    return NormalDist(mu=mean, sigma=sd).pdf(x)


def make_curve(
    mean: float,
    sd: float,
    n: int = 401,
    span_sd: float = 4,
) -> dict[str, list[float]]:
    if n < 2:
        raise ValueError("n must be at least 2.")
    if sd <= 0:
        return {"x": [mean - 1, mean, mean + 1], "y": [0.0, 1.0, 0.0]}
    start = mean - span_sd * sd
    step = (2 * span_sd * sd) / (n - 1)
    xs = [start + i * step for i in range(n)]
    ys = [normal_pdf(x, mean, sd) for x in xs]
    return {"x": xs, "y": ys}


def normal_cdf(x: float, mean: float, sd: float) -> float:
    if sd <= 0:
        raise ValueError("Standard deviation must be positive.")
    return NormalDist(mu=mean, sigma=sd).cdf(x)


def validate_inputs(*values: float) -> list[str]:
    errors: list[str] = []
    for value in values:
        if value is None or isinstance(value, str):
            errors.append("Inputs must be numeric.")
            break
    return errors


def clamp_curve_bounds(values: Iterable[float]) -> tuple[float, float]:
    values = list(values)
    if not values:
        return 0.0, 0.0
    return min(values), max(values)
