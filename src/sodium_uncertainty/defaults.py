import json
from pathlib import Path
from typing import Any

from .model import loa_half_pair_to_sigma


def _default_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "variability_defaults.json"


def load_defaults(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else _default_path()
    data = json.loads(target.read_text())
    validate_defaults(data)
    return data


def validate_defaults(data: dict[str, Any]) -> None:
    if "defaults" not in data:
        raise ValueError("Defaults JSON must include a defaults section.")
    for context, methods in data["defaults"].items():
        if not isinstance(methods, dict):
            raise ValueError(f"Defaults for {context} must be a mapping.")
        for method, params in methods.items():
            if not isinstance(params, dict):
                raise ValueError(f"Defaults for {context}/{method} must be a mapping.")
            loa_half = params.get("loa_half_pair")
            sigma = params.get("sigma")
            if loa_half is None and sigma is None:
                raise ValueError(f"Defaults for {context}/{method} require loa_half_pair or sigma.")
            if loa_half is not None and float(loa_half) <= 0:
                raise ValueError(f"LoA half-width for {context}/{method} must be positive.")
            if sigma is not None and float(sigma) <= 0:
                raise ValueError(f"Sigma for {context}/{method} must be positive.")


def resolve_sigma(params: dict[str, Any], context: str, method: str) -> float:
    entry = params["defaults"][context][method]
    sigma = entry.get("sigma")
    if sigma is not None and sigma != "":
        sigma_value = float(sigma)
        if sigma_value <= 0:
            raise ValueError("Sigma must be positive.")
        return sigma_value
    loa_raw = entry.get("loa_half_pair")
    if loa_raw in (None, ""):
        raise ValueError("LoA half-width must be provided when sigma is empty.")
    loa_half = float(loa_raw)
    return loa_half_pair_to_sigma(loa_half)
