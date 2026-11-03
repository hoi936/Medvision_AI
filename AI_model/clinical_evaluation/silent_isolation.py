"""Hard isolation contract for SILENT_SHADOW evaluation."""

from __future__ import annotations


ISOLATION_FLAGS = (
    "clinical_visibility", "alerts_enabled", "ehr_write_enabled",
    "doctor_message_enabled", "clinical_finalization_enabled",
)


class SilentIsolationBreach(ValueError):
    code = "SILENT_ISOLATION_BREACH"

    def __init__(self, enabled_flags):
        self.enabled_flags = list(enabled_flags)
        super().__init__(f"SILENT_ISOLATION_BREACH: enabled={','.join(self.enabled_flags)}")


def validate_silent_isolation(isolation):
    if not isinstance(isolation, dict):
        raise SilentIsolationBreach(["isolation_contract_missing"])
    missing = [flag for flag in ISOLATION_FLAGS if flag not in isolation]
    enabled = [flag for flag in ISOLATION_FLAGS if isolation.get(flag) is not False]
    violations = missing + [flag for flag in enabled if flag not in missing]
    if violations:
        raise SilentIsolationBreach(violations)
    return {"valid": True, "mode": "SILENT_SHADOW", "flags": {flag: False for flag in ISOLATION_FLAGS}}
