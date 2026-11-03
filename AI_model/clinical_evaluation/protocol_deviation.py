"""Protocol deviations remain separate from technical and safety incidents."""

from __future__ import annotations

from copy import deepcopy

from .incident_log import DIRECT_IDENTIFIER_FIELDS


DEVIATION_CATEGORIES = {
    "WRONG_ELIGIBILITY", "WRONG_SYSTEM_VERSION", "WRONG_INPUT",
    "OUTPUT_EXPOSURE", "WRONG_DATA_SOURCE", "MISSING_REQUIRED_REFERENCE",
    "MANUAL_OVERRIDE_OUTSIDE_PROTOCOL",
}


class ProtocolDeviationError(ValueError):
    pass


def validate_protocol_deviation(deviation):
    if not isinstance(deviation, dict):
        raise ProtocolDeviationError("protocol deviation must be an object")
    required = {
        "deviation_id", "case_id", "protocol_id", "protocol_version", "category",
        "detected_at", "description", "disposition", "reported_by_role",
    }
    missing = sorted(required - set(deviation))
    if missing:
        raise ProtocolDeviationError("protocol deviation missing fields: " + ", ".join(missing))
    if deviation["category"] not in DEVIATION_CATEGORIES:
        raise ProtocolDeviationError("unsupported protocol deviation category")
    direct = sorted(DIRECT_IDENTIFIER_FIELDS & set(deviation))
    if direct:
        raise ProtocolDeviationError("direct identifiers are prohibited: " + ", ".join(direct))
    for field in required:
        if not isinstance(deviation[field], str) or not deviation[field].strip():
            raise ProtocolDeviationError(f"{field} must be non-empty")
    return deviation


class ProtocolDeviationLog:
    def __init__(self):
        self._records = []

    def add(self, deviation):
        validate_protocol_deviation(deviation)
        self._records.append(deepcopy(deviation))

    def records(self):
        return deepcopy(self._records)
