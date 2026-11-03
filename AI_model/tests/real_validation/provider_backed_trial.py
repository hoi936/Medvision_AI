"""Trial policy for the provider-backed E2E harness."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrialPolicy:
    mode: str = "REAL_GATE"
    transient_retries: int = 1

    def __post_init__(self):
        if self.mode not in {"REAL_GATE", "REAL_ROBUSTNESS"}:
            raise ValueError(f"unsupported trial mode: {self.mode}")
        if self.transient_retries < 0:
            raise ValueError("transient_retries must be non-negative")

    @property
    def trials_per_case(self):
        return 1 if self.mode == "REAL_GATE" else None

    def may_retry(self, failure_class, attempts_completed):
        """Only bounded transient infrastructure failures may be retried."""
        return (
            failure_class == "INFRASTRUCTURE_TRANSIENT"
            and attempts_completed <= self.transient_retries
        )
