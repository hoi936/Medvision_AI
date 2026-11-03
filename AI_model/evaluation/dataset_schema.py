"""Fail-closed manifest and case schemas for independent dataset evaluation."""

from __future__ import annotations

from copy import deepcopy


SCHEMA_VERSION = "clinical-dataset-evaluation-v1"
MISSINGNESS_STATES = {"MISSING", "EXPLICIT_NEGATIVE", "POSITIVE", "UNKNOWN"}
DIRECT_IDENTIFIER_KEYS = {
    "name", "patient_name", "mrn", "medical_record_number", "dob",
    "date_of_birth", "email", "phone", "address", "national_id", "patient_id",
}
REQUIRED_MANIFEST_FIELDS = {
    "dataset_id", "dataset_version", "source", "institution", "date_range",
    "deidentified", "counts", "splits",
}
REQUIRED_CASE_FIELDS = {
    "case_id", "patient_group_id", "split", "studies", "imaging", "clinical",
    "labs", "physiology", "microbiology", "pathology", "longitudinal",
    "reference_standards", "adjudication", "metadata", "missingness",
}


class DatasetSchemaError(ValueError):
    pass


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise DatasetSchemaError(f"{label} must be an object")


def _walk_identifier_keys(value, path="case"):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in DIRECT_IDENTIFIER_KEYS:
                raise DatasetSchemaError(f"direct patient identifier is forbidden at {path}.{key}")
            _walk_identifier_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_identifier_keys(child, f"{path}[{index}]")


def validate_manifest(manifest):
    _require_mapping(manifest, "dataset manifest")
    missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    if missing:
        raise DatasetSchemaError(f"dataset manifest missing fields: {', '.join(missing)}")
    if not manifest["dataset_id"] or not manifest["dataset_version"]:
        raise DatasetSchemaError("dataset_id and dataset_version must be non-empty")
    if manifest["deidentified"] is not True:
        raise DatasetSchemaError("dataset must be explicitly marked deidentified=true")
    _require_mapping(manifest["counts"], "dataset counts")
    _require_mapping(manifest["splits"], "dataset splits")
    for name, case_ids in manifest["splits"].items():
        if not name or not isinstance(case_ids, list) or not all(isinstance(item, str) and item for item in case_ids):
            raise DatasetSchemaError("each split must be a named list of case IDs")
    return deepcopy(manifest)


def validate_case(case):
    _require_mapping(case, "dataset case")
    missing = sorted(REQUIRED_CASE_FIELDS - set(case))
    if missing:
        raise DatasetSchemaError(f"dataset case missing fields: {', '.join(missing)}")
    for field in ("case_id", "patient_group_id", "split"):
        if not isinstance(case[field], str) or not case[field].strip():
            raise DatasetSchemaError(f"{field} must be a non-empty pseudonymous value")
    if not isinstance(case["studies"], list) or not case["studies"]:
        raise DatasetSchemaError("studies must be a non-empty list")
    study_ids = []
    for study in case["studies"]:
        _require_mapping(study, "study")
        if not study.get("study_id") or not study.get("modality"):
            raise DatasetSchemaError("each study requires study_id and modality")
        study_ids.append(study["study_id"])
    if len(study_ids) != len(set(study_ids)):
        raise DatasetSchemaError("study IDs must be unique within a case")
    _require_mapping(case["imaging"], "imaging")
    _require_mapping(case["clinical"], "clinical")
    _require_mapping(case["longitudinal"], "longitudinal")
    _require_mapping(case["adjudication"], "adjudication")
    _require_mapping(case["metadata"], "metadata")
    _require_mapping(case["missingness"], "missingness")
    for field in ("labs", "physiology", "microbiology", "pathology", "reference_standards"):
        if not isinstance(case[field], list):
            raise DatasetSchemaError(f"{field} must be a list")
    bad_missingness = sorted(
        {str(value) for value in case["missingness"].values()} - MISSINGNESS_STATES
    )
    if bad_missingness:
        raise DatasetSchemaError(f"invalid missingness states: {', '.join(bad_missingness)}")
    _walk_identifier_keys(case)
    return deepcopy(case)
