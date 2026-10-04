import pytest

from clinical_evaluation.incident_log import IncidentLog, IncidentValidationError
from clinical_evaluation.protocol_deviation import ProtocolDeviationLog, ProtocolDeviationError


def incident(category):
    return {
        "incident_id": "INC-SYN-1", "case_id": "CASE-SYN-1",
        "deployment_version": "DEPLOY-SYN", "category": category,
        "severity": "HIGH", "detected_at": "2026-01-01T10:00:00Z",
        "description": "Synthetic validation incident.", "affected_stage": "semantic_monitoring",
        "contained": True, "resolution": "synthetic fixture closed",
    }


@pytest.mark.parametrize("category", ["SEMANTIC_SAFETY_INCIDENT", "PRIVACY_SECURITY_INCIDENT", "SILENT_ISOLATION_BREACH"])
def test_safety_privacy_and_isolation_incidents_are_explicit(category):
    log = IncidentLog()
    log.add(incident(category))
    assert log.records()[0]["category"] == category


def test_incident_log_rejects_direct_identifiers():
    item = incident("PRIVACY_SECURITY_INCIDENT")
    item["mrn"] = "synthetic-prohibited"
    with pytest.raises(IncidentValidationError, match="direct identifiers"):
        IncidentLog().add(item)


def test_protocol_deviation_uses_separate_schema_and_log():
    deviation = {
        "deviation_id": "DEV-SYN-1", "case_id": "CASE-SYN-1",
        "protocol_id": "SYNTHETIC-SILENT-001", "protocol_version": "1.0",
        "category": "WRONG_SYSTEM_VERSION", "detected_at": "2026-01-01T10:00:00Z",
        "description": "Synthetic mismatch.", "disposition": "excluded from analysis",
        "reported_by_role": "synthetic-study-monitor",
    }
    log = ProtocolDeviationLog()
    log.add(deviation)
    assert log.records() == [deviation]
    with pytest.raises(IncidentValidationError, match="unsupported incident category"):
        IncidentLog().add(incident("PROTOCOL_DEVIATION"))


def test_incident_category_cannot_enter_protocol_deviation_log():
    deviation = {
        "deviation_id": "DEV-SYN-2", "case_id": "CASE-SYN-1",
        "protocol_id": "P", "protocol_version": "1", "category": "TECHNICAL_INCIDENT",
        "detected_at": "2026-01-01T10:00:00Z", "description": "Synthetic.",
        "disposition": "review", "reported_by_role": "monitor",
    }
    with pytest.raises(ProtocolDeviationError, match="unsupported"):
        ProtocolDeviationLog().add(deviation)
