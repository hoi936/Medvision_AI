"""Explicit host-supplied privacy readiness status."""

from .security_readiness import validate_external_status


def validate_privacy_readiness(record):
    return validate_external_status(record, "privacy")
