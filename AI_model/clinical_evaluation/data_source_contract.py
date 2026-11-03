"""Explicit data-source field allowlists; there is no generic ingest-everything path."""

from __future__ import annotations


UNKNOWN_FIELD_POLICIES = {"REJECT", "QUARANTINE"}
TIME_FIELDS = {
    "acquisition_time", "sample_time", "result_time", "report_final_time",
    "ingestion_time", "hermes_run_time",
}


class DataSourceContractError(ValueError):
    pass


def validate_data_source_contract(contract):
    if not isinstance(contract, dict):
        raise DataSourceContractError("data-source contract must be an object")
    required = {
        "source_id", "source_type", "system_name", "owner", "ingestion_mode",
        "fields_allowed", "fields_excluded", "timestamp_semantics",
        "update_frequency", "validation_rules", "unknown_field_policy",
    }
    missing = sorted(required - set(contract))
    if missing:
        raise DataSourceContractError(f"data-source contract missing fields: {', '.join(missing)}")
    if not all(contract.get(field) for field in ("source_id", "source_type", "system_name", "owner", "ingestion_mode")):
        raise DataSourceContractError("data-source identity/owner fields are required")
    allowed = contract["fields_allowed"]
    excluded = contract["fields_excluded"]
    if not isinstance(allowed, list) or not allowed or not isinstance(excluded, list):
        raise DataSourceContractError("allowed/excluded fields must be explicit lists")
    if set(allowed) & set(excluded):
        raise DataSourceContractError("a field cannot be both allowed and excluded")
    if contract["unknown_field_policy"] not in UNKNOWN_FIELD_POLICIES:
        raise DataSourceContractError("unknown_field_policy must be REJECT or QUARANTINE")
    semantics = contract["timestamp_semantics"]
    if not isinstance(semantics, dict) or not TIME_FIELDS <= set(semantics):
        raise DataSourceContractError("timestamp semantics must define every clinical and processing time")
    if not isinstance(contract["validation_rules"], list) or not contract["validation_rules"]:
        raise DataSourceContractError("validation rules must be pre-specified")
    return contract


def classify_payload_fields(contract, payload):
    validate_data_source_contract(contract)
    if not isinstance(payload, dict):
        raise DataSourceContractError("payload must be an object")
    allowed = set(contract["fields_allowed"])
    excluded = set(contract["fields_excluded"])
    present = set(payload)
    excluded_present = sorted(present & excluded)
    unknown = sorted(present - allowed - excluded)
    if excluded_present:
        return {"status": "REJECTED", "reason": "excluded fields present", "fields": excluded_present}
    if unknown:
        status = "REJECTED" if contract["unknown_field_policy"] == "REJECT" else "QUARANTINED"
        return {"status": status, "reason": "unknown fields present", "fields": unknown}
    return {"status": "ACCEPTED", "reason": None, "fields": []}
