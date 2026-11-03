"""Reader-study case isolation and reference-leakage checks."""

from __future__ import annotations

from evaluation.dataset_schema import validate_case


INTERNAL_CASE_PREFIXES = ("E2E", "PB")


class CaseIsolationError(ValueError):
    def __init__(self, violations):
        self.violations = list(violations)
        super().__init__("; ".join(item["code"] for item in violations))


def validate_reader_case(case):
    validated = validate_case(case)
    metadata = validated.get("metadata", {})
    if not metadata.get("case_stratum") or not metadata.get("randomization_id"):
        raise CaseIsolationError([{
            "code": "READER_CASE_BINDING_INCOMPLETE",
            "case_id": validated.get("case_id"),
        }])
    return validated


def _case_sets(cases):
    return {
        "case": {case["case_id"] for case in cases},
        "patient": {case["patient_group_id"] for case in cases},
        "study": {study["study_id"] for case in cases for study in case["studies"]},
        "hash": {
            study[key]
            for case in cases for study in case["studies"]
            for key in ("content_hash", "image_hash", "report_hash") if study.get(key)
        },
    }


def validate_case_isolation(training_cases, evaluation_cases):
    training = [validate_case(case) for case in training_cases]
    evaluation = [validate_reader_case(case) for case in evaluation_cases]
    train_sets, eval_sets = _case_sets(training), _case_sets(evaluation)
    violations = []
    code_map = {
        "case": "TRAINING_CASE_OVERLAP", "patient": "TRAINING_PATIENT_OVERLAP",
        "study": "TRAINING_STUDY_OVERLAP", "hash": "TRAINING_CONTENT_OVERLAP",
    }
    for kind, code in code_map.items():
        for value in sorted(train_sets[kind] & eval_sets[kind]):
            violations.append({"code": code, "value": value})
    for case in evaluation:
        non_evaluation = case.get("metadata", {}).get("study_role") == "non_evaluation"
        origin = case.get("metadata", {}).get("origin")
        if not non_evaluation and (
            case["case_id"].startswith(INTERNAL_CASE_PREFIXES)
            or origin in {"golden_case", "e2e_fixture", "provider_backed_fixture"}
        ):
            violations.append({"code": "GOLDEN_CASE_AS_EVALUATION", "case_id": case["case_id"]})
        visible = set(case.get("metadata", {}).get("reader_visible_fields", []))
        if visible & {"reference_standard", "reference_standards", "adjudication", "ground_truth"}:
            violations.append({"code": "REFERENCE_STANDARD_LEAKAGE", "case_id": case["case_id"]})
    if violations:
        raise CaseIsolationError(violations)
    return {"valid": True, "training_case_count": len(training), "evaluation_case_count": len(evaluation)}
