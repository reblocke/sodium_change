import math

import pytest

from sodium_uncertainty.model import (
    loa_half_pair_to_sigma,
    posterior_same_sample,
    posterior_sequential_draws,
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


def test_invalid_loa_raises() -> None:
    with pytest.raises(ValueError):
        loa_half_pair_to_sigma(0.0)
