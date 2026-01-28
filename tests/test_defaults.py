from pathlib import Path

import json
import pytest

from sodium_uncertainty.defaults import load_defaults, resolve_sigma
from sodium_uncertainty.model import loa_half_pair_to_sigma


def test_load_defaults_structure() -> None:
    data = load_defaults()
    assert data["units"] == "mmol/L"
    assert "analytic_repeatability" in data["defaults"]
    assert "central_lab_indirect_ISE" in data["defaults"]["analytic_repeatability"]


def test_resolve_sigma_prefers_sigma_override(tmp_path: Path) -> None:
    payload = {
        "version": 1,
        "units": "mmol/L",
        "defaults": {
            "analytic_repeatability": {
                "central_lab_indirect_ISE": {"loa_half_pair": 3.0, "sigma": 1.2}
            }
        },
    }
    path = tmp_path / "defaults.json"
    path.write_text(json.dumps(payload))
    data = load_defaults(path)
    assert resolve_sigma(data, "analytic_repeatability", "central_lab_indirect_ISE") == pytest.approx(1.2)


def test_resolve_sigma_from_loa() -> None:
    data = load_defaults()
    sigma = resolve_sigma(data, "analytic_repeatability", "central_lab_indirect_ISE")
    assert sigma == pytest.approx(loa_half_pair_to_sigma(3.0))
