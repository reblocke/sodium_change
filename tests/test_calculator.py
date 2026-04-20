import json
import math

import pytest

from sodium_uncertainty.calculator import compute_from_json, compute_payload
from sodium_uncertainty.defaults import load_defaults, resolve_sigma
from sodium_uncertainty.model import chance_probability_under_null, loa_half_pair_to_sigma

CENTRAL = "central_lab_indirect_ISE"
ISTAT = "istat_direct_ISE"


def _payload(context: str = "sequential_draws") -> dict:
    return {
        "y1": 130,
        "y2": 133,
        "method1": CENTRAL,
        "method2": CENTRAL,
        "context": context,
        "ci_level": 0.95,
        "threshold": 2,
        "scale_with_na": False,
        "na_ref": 140,
        "params": load_defaults(),
    }


def test_compute_from_json_preserves_browser_contract() -> None:
    result = json.loads(compute_from_json(json.dumps(_payload())))
    assert result["errors"] == []
    assert result["observed_delta"] == pytest.approx(3.0)
    assert "curves" in result
    assert "details" in result
    assert result["probabilities"]["chance_bucket_key"]


def test_analytic_repeatability_true_delta_fixed_at_zero() -> None:
    result = compute_payload(_payload("analytic_repeatability"))
    sigma_delta = result["details"]["sigma_delta"]

    assert result["errors"] == []
    assert result["delta_true"]["mean"] == pytest.approx(0.0)
    assert result["delta_true"]["sd"] == pytest.approx(0.0)
    assert result["delta_observed"]["sd"] == pytest.approx(sigma_delta)
    assert result["probabilities"]["chance_under_null"] == pytest.approx(
        chance_probability_under_null(3.0, sigma_delta)
    )


def test_sequential_draws_delta_sd_uses_independent_error_sum() -> None:
    payload = _payload("sequential_draws")
    payload["method2"] = ISTAT
    result = compute_payload(payload)
    params = payload["params"]
    sigma1 = resolve_sigma(params, "sequential_draws", CENTRAL)
    sigma2 = resolve_sigma(params, "sequential_draws", ISTAT)

    assert result["errors"] == []
    assert result["delta_true"]["mean"] == pytest.approx(3.0)
    assert result["delta_true"]["sd"] == pytest.approx(math.sqrt(sigma1**2 + sigma2**2))


def test_loa_to_sigma_details_match_pairwise_conversion() -> None:
    result = compute_payload(_payload("analytic_repeatability"))
    detail = result["details"]["entry1"]
    loa_half = 2.8

    assert detail["sd_diff"] == pytest.approx(loa_half / 1.96)
    assert detail["sigma_from_loa"] == pytest.approx(loa_half_pair_to_sigma(loa_half))
    assert detail["sigma_used"] == pytest.approx(loa_half_pair_to_sigma(loa_half))


def test_sigma_override_precedence_is_reflected_in_details() -> None:
    payload = _payload("analytic_repeatability")
    payload["params"] = {
        "version": 1,
        "units": "mmol/L",
        "defaults": {
            "analytic_repeatability": {
                CENTRAL: {"loa_half_pair": 2.8, "sigma": 1.2},
            }
        },
    }

    result = compute_payload(payload)

    assert result["errors"] == []
    assert result["inputs"]["sigma1"] == pytest.approx(1.2)
    assert result["details"]["entry1"]["override_used"] is True
    assert result["details"]["entry1"]["sigma_raw"] == pytest.approx(1.2)


def test_cv_scaling_reports_scaled_sigmas_and_factors() -> None:
    payload = _payload("sequential_draws")
    payload.update({"y1": 126, "y2": 140, "scale_with_na": True, "na_ref": 140})
    params = payload["params"]
    raw_sigma1 = resolve_sigma(params, "sequential_draws", CENTRAL)
    raw_sigma2 = resolve_sigma(params, "sequential_draws", CENTRAL)

    result = compute_payload(payload)

    assert result["errors"] == []
    assert result["details"]["entry1"]["scale_factor"] == pytest.approx(126 / 140)
    assert result["details"]["entry2"]["scale_factor"] == pytest.approx(1.0)
    assert result["details"]["sigma1"] == pytest.approx(raw_sigma1 * (126 / 140))
    assert result["details"]["sigma2"] == pytest.approx(raw_sigma2)
    assert result["details"]["entry1"]["sigma_raw"] == pytest.approx(raw_sigma1)
