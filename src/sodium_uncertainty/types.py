from dataclasses import dataclass


@dataclass(frozen=True)
class NormalSummary:
    mean: float
    sd: float
    ci_low: float
    ci_high: float


@dataclass(frozen=True)
class ScenarioResult:
    na1: NormalSummary
    na2: NormalSummary
    delta_true: NormalSummary
    observed_delta: float
    delta_observed: NormalSummary | None = None
