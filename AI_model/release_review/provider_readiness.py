"""Provider dependency record; no fallback or provider configuration occurs here."""

from __future__ import annotations

from .security_readiness import validate_external_status


def validate_provider_readiness(record):
    validate_external_status(record, "provider")
    required = {"configured", "provider", "model", "outage_behavior", "drift_strategy", "deprecation_plan", "fallback_policy"}
    missing = sorted(required - set(record))
    if missing:
        raise ValueError("provider readiness missing: " + ", ".join(missing))
    if not isinstance(record["configured"], bool):
        raise ValueError("provider configured flag must be boolean")
    if record["fallback_policy"] != "NO_SILENT_FALLBACK":
        raise ValueError("provider fallback policy violates frozen runtime behavior")
    return record
