import math
from statistics import NormalDist

import pytest

from sodium_uncertainty.model import (
    chance_probability_under_null,
    loa_half_pair_to_sigma,
    posterior_same_sample,
    posterior_sequential_draws,
    qualitative_bucket,
    same_sample_p_value,
    sigma_to_loa_half_pair,
)


def test_loa_half_pair_round_trip() -> None:
    loa_half = 3.0
    sigma = loa_half_pair_to_sigma(loa_half)
    assert sigma_to_loa_half_pair(sigma) == pytest.approx(loa_half, rel=1e-6)


def test_sequential_same_method_delta_ci_matches_loa() -> None:
    loa_half = 3.0
    sigma = loa_half_pair_to_sigma(loa_half)
    result = posterior_sequential_draws(130.0, 133.0, sigma, sigma, 0.95)
    assert result.delta_true.mean == pytest.approx(3.0)
    half_width = (result.delta_true.ci_high - result.delta_true.ci_low) / 2
    assert half_width == pytest.approx(loa_half, abs=0.05)


def test_sequential_mixed_methods_ci_between_inputs() -> None:
    sigma_a = loa_half_pair_to_sigma(3.0)
    sigma_b = loa_half_pair_to_sigma(2.0)
    result = posterior_sequential_draws(130.0, 133.0, sigma_a, sigma_b, 0.95)
    half_width = (result.delta_true.ci_high - result.delta_true.ci_low) / 2
    assert 2.0 < half_width < 3.0


def test_sequential_draws_wider_uncertainty() -> None:
    sigma = loa_half_pair_to_sigma(6.0)
    result = posterior_sequential_draws(130.0, 133.0, sigma, sigma, 0.95)
    half_width = (result.delta_true.ci_high - result.delta_true.ci_low) / 2
    assert half_width == pytest.approx(6.0, abs=0.1)


def test_analytic_repeatability_delta_true_zero() -> None:
    sigma = loa_half_pair_to_sigma(3.0)
    result = posterior_same_sample(130.0, 133.0, sigma, sigma, 0.95)
    assert result.delta_true.mean == pytest.approx(0.0)
    assert result.delta_true.sd == pytest.approx(0.0)
    assert result.delta_observed is not None
    assert result.delta_observed.sd == pytest.approx(math.sqrt(2) * sigma)


def test_same_sample_p_value() -> None:
    sigma = 1.0
    p_value_zero = same_sample_p_value(130.0, 130.0, sigma, sigma)
    assert p_value_zero == pytest.approx(1.0)
    delta = 2.0
    sd = math.sqrt(2) * sigma
    expected = 2 * (1 - NormalDist().cdf(abs(delta) / sd))
    p_value = same_sample_p_value(130.0, 132.0, sigma, sigma)
    assert p_value == pytest.approx(expected)


def test_chance_probability_under_null() -> None:
    sigma = 2.0
    p_value_zero = chance_probability_under_null(0.0, sigma)
    assert p_value_zero == pytest.approx(1.0)
    delta = 3.0
    expected = 2 * (1 - NormalDist().cdf(abs(delta) / sigma))
    p_value = chance_probability_under_null(delta, sigma)
    assert p_value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("p_value", "key"),
    [
        (0.2, "common"),
        (0.199, "plausible"),
        (0.05, "plausible"),
        (0.049, "uncommon"),
        (0.01, "uncommon"),
        (0.009, "very_unlikely"),
    ],
)
def test_qualitative_bucket(p_value: float, key: str) -> None:
    bucket_key, _label = qualitative_bucket(p_value)
    assert bucket_key == key


def test_invalid_loa_raises() -> None:
    with pytest.raises(ValueError):
        loa_half_pair_to_sigma(0.0)
