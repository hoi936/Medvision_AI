"""Explicit host-supplied security readiness status."""

from __future__ import annotations


EXTERNAL_STATUSES = {"NOT_ASSESSED", "IN_PROGRESS", "RESOLVED", "BLOCKING_ISSUE"}


def validate_external_status(record, domain):
    if not isinstance(record, dict):
        raise ValueError(f"{domain} readiness must be an object")
    if record.get("status") not in EXTERNAL_STATUSES:
        raise ValueError(f"invalid {domain} readiness status")
    if not isinstance(record.get("reference"), str):
        raise ValueError(f"{domain} reference must be explicit")
    if record["status"] == "RESOLVED" and not record["reference"].strip():
        raise ValueError(f"resolved {domain} readiness requires an external reference")
    if not isinstance(record.get("limitations"), list):
        raise ValueError(f"{domain} limitations must be a list")
    return record


def validate_security_readiness(record):
    return validate_external_status(record, "security")
