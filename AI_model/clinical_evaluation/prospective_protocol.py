"""Prospective interventional protocol schema; validation never starts a study."""

from __future__ import annotations

from .protocol_schema import ClinicalProtocolError


def validate_prospective_protocol(protocol):
    if not isinstance(protocol, dict):
        raise ClinicalProtocolError("prospective protocol must be an object")
    required = {
        "protocol_id", "version", "objective", "mode", "intended_use",
        "intended_users", "clinical_pathway_position", "system_snapshot",
        "inputs", "outputs", "intervention", "control", "human_ai_interaction",
        "input_failure_handling", "output_failure_handling", "eligibility",
        "primary_endpoint", "secondary_endpoints", "safety_endpoints",
        "stopping_rules", "pause_rules", "ethics", "consent_strategy", "monitoring",
    }
    missing = sorted(required - set(protocol))
    if missing:
        raise ClinicalProtocolError("prospective protocol missing fields: " + ", ".join(missing))
    if protocol["mode"] != "PROSPECTIVE_INTERVENTIONAL":
        raise ClinicalProtocolError("prospective protocol mode must be PROSPECTIVE_INTERVENTIONAL")
    scalar_fields = {
        "protocol_id", "version", "objective", "intended_use",
        "clinical_pathway_position", "primary_endpoint", "consent_strategy",
    }
    for field in scalar_fields:
        if not isinstance(protocol[field], str) or not protocol[field].strip():
            raise ClinicalProtocolError(f"{field} must be non-empty")
    list_fields = {
        "intended_users", "inputs", "outputs", "secondary_endpoints", "safety_endpoints",
        "stopping_rules", "pause_rules",
    }
    for field in list_fields:
        if not isinstance(protocol[field], list) or not protocol[field]:
            raise ClinicalProtocolError(f"{field} must be a non-empty pre-specified list")
    object_fields = {
        "system_snapshot", "intervention", "control", "human_ai_interaction",
        "input_failure_handling", "output_failure_handling", "eligibility", "ethics", "monitoring",
    }
    for field in object_fields:
        if not isinstance(protocol[field], dict) or not protocol[field]:
            raise ClinicalProtocolError(f"{field} must be a non-empty object")
    if protocol["intervention"].get("autonomous_action") is not False:
        raise ClinicalProtocolError("autonomous intervention is prohibited")
    if protocol["human_ai_interaction"].get("doctor_remains_decision_maker") is not True:
        raise ClinicalProtocolError("doctor decision authority must be explicit")
    if protocol["human_ai_interaction"].get("doctor_review_required") is not True:
        raise ClinicalProtocolError("doctor review must remain required")
    if not all(protocol["ethics"].get(key) for key in ("status", "reference")):
        raise ClinicalProtocolError("ethics status/reference is incomplete")
    snapshot_fields = {
        "repo_commit", "hermes_version", "hermes_commit", "python_version",
        "skill_tree_hash", "config_hash", "provider", "model", "snapshot_hash",
    }
    if any(not protocol["system_snapshot"].get(field) for field in snapshot_fields):
        raise ClinicalProtocolError("prospective system snapshot is incomplete")
    return protocol
