"""Intended-use lock for a version-bound release review."""

from __future__ import annotations


REQUIRED_FIELDS = {
    "intended_users", "setting", "inputs", "outputs", "clinical_role",
    "doctor_control_statement", "prohibited_uses", "known_limitations",
    "workflow_position", "reviewer_role", "finalizer_role", "escalation_owner",
}


class IntendedUseError(ValueError):
    code = "INTENDED_USE_NOT_LOCKED"


def validate_intended_use(intended_use):
    if not isinstance(intended_use, dict):
        raise IntendedUseError("INTENDED_USE_NOT_LOCKED: intended use must be an object")
    missing = sorted(REQUIRED_FIELDS - set(intended_use))
    if missing:
        raise IntendedUseError("INTENDED_USE_NOT_LOCKED: missing " + ", ".join(missing))
    list_fields = {"intended_users", "inputs", "outputs", "prohibited_uses", "known_limitations"}
    for field in list_fields:
        if not isinstance(intended_use[field], list) or not intended_use[field]:
            raise IntendedUseError(f"INTENDED_USE_NOT_LOCKED: {field} must be a non-empty list")
    scalar_fields = REQUIRED_FIELDS - list_fields
    for field in scalar_fields:
        if not isinstance(intended_use[field], str) or not intended_use[field].strip():
            raise IntendedUseError(f"INTENDED_USE_NOT_LOCKED: {field} must be non-empty")
    if "doctor" not in intended_use["doctor_control_statement"].lower():
        raise IntendedUseError("INTENDED_USE_NOT_LOCKED: doctor control must be explicit")
    if not any("autonomous" in item.lower() for item in intended_use["prohibited_uses"]):
        raise IntendedUseError("INTENDED_USE_NOT_LOCKED: autonomous use must be prohibited")
    return intended_use
