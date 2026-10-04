"""Schema contract for an offline paired Human-AI reader study."""

from __future__ import annotations


CONDITIONS = {"UNAIDED", "HERMES_ASSISTED"}
ASSISTANCE_MODES = {"DRAFT_REPORT_ASSIST", "CONCURRENT_DECISION_SUPPORT"}
DESIGNS = {"paired_mrmc", "other"}
ETHICS_RESOLVED_STATUSES = {
    "APPROVED", "EXEMPT_BY_INSTITUTION", "NOT_HUMAN_SUBJECTS_BY_INSTITUTION",
    "NOT_REQUIRED_BY_INSTITUTION",
}
DIRECT_READER_IDENTIFIERS = {
    "name", "full_name", "email", "phone", "address", "license_number",
    "employee_id", "date_of_birth",
}


class StudySchemaError(ValueError):
    pass


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise StudySchemaError(f"{label} must be an object")


def validate_study_protocol(protocol):
    _require_mapping(protocol, "study protocol")
    required = {
        "study_id", "version", "objective", "design", "conditions",
        "assistance_mode", "primary_endpoint", "secondary_endpoints",
        "dataset_id", "reference_standard_version", "reader_plan", "sessions",
        "randomization", "training", "system_snapshot", "ui_version",
        "ui_snapshot_hash", "data_storage", "ethics",
    }
    missing = sorted(required - set(protocol))
    if missing:
        raise StudySchemaError(f"study protocol missing fields: {', '.join(missing)}")
    for field in ("study_id", "version", "objective", "primary_endpoint", "dataset_id", "reference_standard_version", "ui_version", "ui_snapshot_hash"):
        if not isinstance(protocol[field], str) or not protocol[field].strip():
            raise StudySchemaError(f"{field} must be non-empty")
    if protocol["design"] not in DESIGNS:
        raise StudySchemaError("unsupported study design")
    if set(protocol["conditions"]) != CONDITIONS:
        raise StudySchemaError("conditions must contain UNAIDED and HERMES_ASSISTED")
    if protocol["assistance_mode"] not in ASSISTANCE_MODES:
        raise StudySchemaError("assistance_mode must select one supported workflow")
    if not isinstance(protocol["secondary_endpoints"], list):
        raise StudySchemaError("secondary_endpoints must be a list")
    for field in ("reader_plan", "sessions", "randomization", "training", "system_snapshot", "data_storage", "ethics"):
        _require_mapping(protocol[field], field)
    reader_plan = protocol["reader_plan"]
    if not reader_plan.get("target_roles") or not reader_plan.get("planned_count"):
        raise StudySchemaError("reader plan requires target_roles and planned_count")
    sessions = protocol["sessions"]
    if sessions.get("count") != 2:
        raise StudySchemaError("paired AB/BA v1 requires exactly two sessions")
    if sessions.get("counterbalanced") is not True:
        raise StudySchemaError("paired study sessions must be counterbalanced")
    washout = sessions.get("washout")
    _require_mapping(washout, "washout")
    if not all(washout.get(field) for field in ("duration", "rationale", "memory_mitigation")):
        raise StudySchemaError("washout duration, rationale, and memory mitigation must be pre-specified")
    randomization = protocol["randomization"]
    if randomization.get("method") not in {"AB_BA_COUNTERBALANCED"}:
        raise StudySchemaError("randomization method must be AB_BA_COUNTERBALANCED")
    if not isinstance(randomization.get("seed"), int):
        raise StudySchemaError("randomization seed must be an integer")
    training = protocol["training"]
    if training.get("required") is not True or not training.get("training_case_set_id"):
        raise StudySchemaError("training set must be explicitly configured")
    snapshot = protocol["system_snapshot"]
    required_snapshot = {
        "repo_commit", "hermes_version", "hermes_commit", "skill_tree_hash", "snapshot_hash",
    }
    if any(not snapshot.get(field) for field in required_snapshot):
        raise StudySchemaError("system snapshot must be frozen and complete")
    storage = protocol["data_storage"]
    if storage.get("status") != "APPROVED" or not storage.get("approval_reference"):
        raise StudySchemaError("study data storage path/handling is not approved")
    ethics = protocol["ethics"]
    for field in ("status", "determination_reference", "privacy_status", "data_use_status", "reader_participation_status"):
        if field not in ethics:
            raise StudySchemaError(f"ethics field missing: {field}")
    return protocol


def validate_reader(reader):
    _require_mapping(reader, "reader")
    if DIRECT_READER_IDENTIFIERS & {str(key).lower() for key in reader}:
        raise StudySchemaError("direct reader identifiers are forbidden")
    required = {
        "reader_id", "role", "specialty", "experience_band", "training_level",
        "prior_ai_experience", "site", "assigned_sequence",
    }
    missing = sorted(required - set(reader))
    if missing:
        raise StudySchemaError(f"reader missing fields: {', '.join(missing)}")
    if reader["assigned_sequence"] not in {"AB", "BA", "PENDING"}:
        raise StudySchemaError("reader sequence must be AB, BA, or PENDING before randomization")
    if not all(isinstance(reader[field], str) and reader[field].strip() for field in required):
        raise StudySchemaError("reader fields must be non-empty categorical values")
    return reader
