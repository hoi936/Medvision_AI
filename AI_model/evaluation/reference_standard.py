"""Task-specific reference-standard contract."""

from __future__ import annotations


REFERENCE_TASKS = {
    "finding", "disease_state", "temporal_state", "arbitration", "report_fidelity",
}
FINDING_LABELS = {"POSITIVE", "EXPLICIT_NEGATIVE", "UNKNOWN", "INDETERMINATE"}


class ReferenceStandardError(ValueError):
    pass


def validate_reference_standard(reference):
    if not isinstance(reference, dict):
        raise ReferenceStandardError("reference standard must be an object")
    required = {
        "task", "source_type", "source_ids", "reviewer_count", "adjudicated",
        "confidence", "limitations", "label",
    }
    missing = sorted(required - set(reference))
    if missing:
        raise ReferenceStandardError(f"reference standard missing fields: {', '.join(missing)}")
    task = reference["task"]
    if task not in REFERENCE_TASKS:
        raise ReferenceStandardError(f"unsupported reference task: {task}")
    if not reference["source_type"] or not reference["source_ids"]:
        raise ReferenceStandardError("reference source_type and source_ids are required")
    if not isinstance(reference["source_ids"], list) or not all(reference["source_ids"]):
        raise ReferenceStandardError("reference source_ids must be a non-empty list")
    if not isinstance(reference["reviewer_count"], int) or reference["reviewer_count"] < 0:
        raise ReferenceStandardError("reviewer_count must be a non-negative integer")
    if not isinstance(reference["adjudicated"], bool):
        raise ReferenceStandardError("adjudicated must be boolean")
    if not isinstance(reference["limitations"], list):
        raise ReferenceStandardError("reference limitations must be a list")
    label = reference["label"]
    if task == "finding" and label not in FINDING_LABELS:
        raise ReferenceStandardError("finding reference uses an invalid bounded label")
    if task in {"disease_state", "temporal_state"} and (
        not isinstance(label, str) or not label.strip()
    ):
        raise ReferenceStandardError(f"{task} label must retain its named bounded state")
    if task in {"arbitration", "report_fidelity"} and (
        not isinstance(label, dict) or not label
    ):
        raise ReferenceStandardError(f"{task} label must be a structured object")
    return reference


def validate_case_references(case, requested_tasks):
    references = [validate_reference_standard(item) for item in case["reference_standards"]]
    available = {item["task"] for item in references}
    missing = sorted(set(requested_tasks) - available)
    if missing:
        raise ReferenceStandardError(
            f"case {case['case_id']} lacks reference standards for: {', '.join(missing)}"
        )
    return references


def validate_reference_set(cases, requested_tasks):
    return {
        case["case_id"]: validate_case_references(case, requested_tasks)
        for case in cases
    }
