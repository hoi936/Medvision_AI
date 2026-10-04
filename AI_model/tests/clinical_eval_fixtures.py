"""Synthetic-only fixtures for clinical evaluation infrastructure tests."""

from __future__ import annotations

from copy import deepcopy


SYSTEM_SNAPSHOT = {
    "repo_commit": "synthetic-repo-commit",
    "hermes_version": "0.21.4",
    "hermes_commit": "2552fb543bd12a326d23449f41a9c13c48eb4e9a",
    "python_version": "3.11.15",
    "skill_tree_hash": "synthetic-skill-tree-hash",
    "config_hash": "synthetic-config-hash",
    "provider": "sanitized-provider",
    "model": "sanitized-model",
    "snapshot_hash": "synthetic-deployment-snapshot-hash",
}

ISOLATION = {
    "clinical_visibility": False,
    "alerts_enabled": False,
    "ehr_write_enabled": False,
    "doctor_message_enabled": False,
    "clinical_finalization_enabled": False,
}

DATA_SOURCE_CONTRACT = {
    "source_id": "SYNTHETIC-CXR-SOURCE",
    "source_type": "CXR",
    "system_name": "synthetic-fixture-system",
    "owner": "synthetic-study-owner",
    "ingestion_mode": "OFFLINE_SYNTHETIC_TEST",
    "fields_allowed": [
        "source_case_id", "positive_findings", "site", "modality", "projection",
        "protocol", "time_period", "acquisition_time", "sample_time", "result_time",
        "report_final_time", "ingestion_time", "hermes_run_time",
    ],
    "fields_excluded": ["patient_name", "mrn", "email", "phone"],
    "timestamp_semantics": {
        "acquisition_time": "imaging acquisition clinical event time",
        "sample_time": "specimen collection clinical event time",
        "result_time": "result availability clinical event time",
        "report_final_time": "source report finalization time",
        "ingestion_time": "study intake processing time",
        "hermes_run_time": "Hermes invocation start time",
    },
    "update_frequency": "synthetic fixture only",
    "validation_rules": ["ISO-8601 timestamps", "explicit field allowlist"],
    "unknown_field_policy": "REJECT",
}

SILENT_PROTOCOL = {
    "protocol_id": "SYNTHETIC-SILENT-001",
    "version": "1.0",
    "objective": "Validate infrastructure behavior with synthetic data only.",
    "mode": "SILENT_SHADOW",
    "data_sources": ["SYNTHETIC-CXR-SOURCE"],
    "eligibility": {"criteria": ["synthetic fixture"]},
    "evaluation_window": {"start": "2026-01-01", "end": "2026-01-02"},
    "reference_linkage_rules": {"rules": ["pre-specified synthetic reference"]},
    "system_snapshot": SYSTEM_SNAPSHOT,
    "provider_requirements": {"strategy": "FROZEN_OUTPUTS"},
    "isolation": ISOLATION,
    "ethics": {"status": "APPROVED", "reference": "SYNTHETIC-ETHICS-FIXTURE"},
    "privacy": {"status": "RESOLVED", "reference": "SYNTHETIC-PRIVACY-FIXTURE"},
    "security": {"status": "APPROVED", "reference": "SYNTHETIC-SECURITY-FIXTURE"},
}

PROVIDER_EVIDENCE = {
    "frozen_outputs_ready": True,
    "frozen_outputs_hash": "synthetic-frozen-output-set",
    "snapshot_hash": SYSTEM_SNAPSHOT["snapshot_hash"],
}

SYNTHETIC_PAYLOAD = {
    "source_case_id": "SYN-CASE-001",
    "positive_findings": ["Pleural effusion"],
    "site": "synthetic-site",
    "modality": "CXR",
    "projection": "PA",
    "protocol": "synthetic-protocol",
    "time_period": "synthetic-period",
    "acquisition_time": "2026-01-01T08:00:00+00:00",
    "sample_time": "2026-01-01T08:01:00+00:00",
    "result_time": "2026-01-01T08:02:00+00:00",
    "report_final_time": "2026-01-01T08:03:00+00:00",
    "ingestion_time": "2026-01-01T08:04:00+00:00",
    "hermes_run_time": "2026-01-01T08:05:00+00:00",
}

PROSPECTIVE_PROTOCOL = {
    "protocol_id": "SYNTHETIC-INTERVENTIONAL-001",
    "version": "1.0",
    "objective": "Exercise readiness validation with synthetic objects only.",
    "mode": "PROSPECTIVE_INTERVENTIONAL",
    "intended_use": "Synthetic workflow evaluation",
    "intended_users": ["credentialed_clinician"],
    "clinical_pathway_position": "before clinician-authored final report",
    "system_snapshot": SYSTEM_SNAPSHOT,
    "inputs": ["approved case data"],
    "outputs": ["advisory draft"],
    "intervention": {"advisory_only": True, "autonomous_action": False},
    "control": {"description": "pre-specified standard workflow"},
    "human_ai_interaction": {
        "doctor_remains_decision_maker": True,
        "doctor_review_required": True,
        "provenance_visible": True,
    },
    "input_failure_handling": {"action": "withhold output and log"},
    "output_failure_handling": {"action": "withhold output and log"},
    "eligibility": {"criteria": ["synthetic fixture"]},
    "primary_endpoint": "pre-specified synthetic endpoint",
    "secondary_endpoints": ["pre-specified synthetic secondary endpoint"],
    "safety_endpoints": ["doctor-review bypass count"],
    "stopping_rules": ["unexpected harmful recommendation"],
    "pause_rules": ["major data-integrity incident"],
    "ethics": {"status": "APPROVED", "reference": "SYNTHETIC-ETHICS-FIXTURE"},
    "consent_strategy": "institution-supplied determination required",
    "monitoring": {"incidents": True, "protocol_deviations": True},
}

GOVERNANCE_APPROVAL = {
    "status": "APPROVED",
    "reference": "SYNTHETIC-GOVERNANCE-FIXTURE",
    "approved_by_roles": ["study_governance", "clinical_safety"],
    "protocol_version": "1.0",
    "snapshot_hash": SYSTEM_SNAPSHOT["snapshot_hash"],
}


def clone(value):
    return deepcopy(value)


def authorized_event(mode):
    return {
        "event_type": f"AUTHORIZED_{mode}_START",
        "actor_role": "synthetic-study-governance",
        "authorization_reference": "SYNTHETIC-AUTHORIZATION-FIXTURE",
        "authorized_at": "2026-01-01T09:00:00+00:00",
        "protocol_version": "1.0",
        "snapshot_hash": SYSTEM_SNAPSHOT["snapshot_hash"],
    }
