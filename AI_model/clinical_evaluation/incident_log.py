"""Study incident records with an explicit, privacy-minimal schema."""

from __future__ import annotations

from copy import deepcopy


INCIDENT_CATEGORIES = {
    "TECHNICAL_INCIDENT",
    "DATA_INTEGRITY_INCIDENT",
    "SEMANTIC_SAFETY_INCIDENT",
    "HUMAN_FACTORS_INCIDENT",
    "PRIVACY_SECURITY_INCIDENT",
    "SILENT_ISOLATION_BREACH",
}
DIRECT_IDENTIFIER_FIELDS = {
    "patient_name", "name", "mrn", "medical_record_number", "email",
    "phone", "address", "date_of_birth",
}


class IncidentValidationError(ValueError):
    pass


def validate_incident(incident):
    if not isinstance(incident, dict):
        raise IncidentValidationError("incident must be an object")
    required = {
        "incident_id", "case_id", "deployment_version", "category", "severity",
        "detected_at", "description", "affected_stage", "contained", "resolution",
    }
    missing = sorted(required - set(incident))
    if missing:
        raise IncidentValidationError("incident missing fields: " + ", ".join(missing))
    if incident["category"] not in INCIDENT_CATEGORIES:
        raise IncidentValidationError("unsupported incident category")
    if incident["category"] == "PROTOCOL_DEVIATION":
        raise IncidentValidationError("protocol deviations require the separate deviation log")
    if not isinstance(incident["contained"], bool):
        raise IncidentValidationError("contained must be a boolean")
    direct = sorted(DIRECT_IDENTIFIER_FIELDS & set(incident))
    if direct:
        raise IncidentValidationError("direct identifiers are prohibited: " + ", ".join(direct))
    for field in required - {"contained", "resolution"}:
        if not isinstance(incident[field], str) or not incident[field].strip():
            raise IncidentValidationError(f"{field} must be non-empty")
    return incident


class IncidentLog:
    def __init__(self):
        self._records = []

    def add(self, incident):
        validate_incident(incident)
        self._records.append(deepcopy(incident))

    def records(self):
        return deepcopy(self._records)
