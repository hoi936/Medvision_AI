"""Provider-backed cross-disease differential arbitration v1 cases."""

import json
import os
from pathlib import Path
import re

import pytest

from hermes_real_runtime import (
    ProviderPreflightError,
    classify_runtime_failure,
    run_provider_preflight,
    sanitize_infrastructure_detail,
)
from hermes_report import HermesReportError, generate_hermes_report, inspect_hermes_skill


RUN_REAL = os.environ.get("RUN_HERMES_REAL") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="real Hermes tests disabled; set RUN_HERMES_REAL=1 to use the configured provider",
)
CASES_PATH = Path(__file__).parent / "golden_cases" / "cross_disease_arbitration" / "cases.json"
CASES = {case["id"]: case for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))}
REAL_CASE_IDS = [
    "AR01", "AR02", "AR03", "AR04", "AR05", "AR06", "AR07", "AR08",
    "AR10", "AR11", "AR14", "AR17", "AR18", "AR19", "AR20", "AR23",
    "AR28", "AR30", "AR37", "AR39", "AR40", "AR42",
]
PRIORITY_LABEL = {
    "routine": "REVIEW_PRIORITY_ROUTINE",
    "elevated": "REVIEW_PRIORITY_ELEVATED",
    "high": "REVIEW_PRIORITY_HIGH",
}


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")
    for file_path in (
        "references/cross_disease_arbitration/CROSS_DISEASE_ARBITRATION_POLICY.md",
        "references/cross_disease_arbitration/CROSS_DISEASE_ARBITRATION_EVIDENCE.md",
        "references/cross_disease_arbitration/references.md",
    ):
        result = inspect_hermes_skill("medvision-disease-analysis", file_path)
        if result.get("file") != file_path:
            pytest.fail(f"INFRASTRUCTURE_CONFIGURATION: skill_view failed for {file_path}")
    return metadata


def _clinical_assert(condition, case_id, invariant):
    assert condition, f"CLINICAL_SEMANTIC_FAILURE: {case_id}: {invariant}"


def _report(case_id):
    try:
        report = generate_hermes_report(**CASES[case_id]["input"])
    except HermesReportError as exc:
        detail = sanitize_infrastructure_detail(str(exc))
        pytest.fail(f"{classify_runtime_failure(detail)}: {case_id}: {detail}")
    _clinical_assert("review_status: PENDING_CLINICIAN_REVIEW" in report, case_id, "DOCTOR_REVIEW_REQUIRED/review_status")
    _clinical_assert("requires_doctor_review: true" in report, case_id, "DOCTOR_REVIEW_REQUIRED/requires_doctor_review")
    return report


def _assert_no_ranking_or_autonomous_action(report, case_id):
    lowered = report.lower()
    ranking = re.search(
        r"\b(top[- ]?1|top diagnosis|winner|rank(?:ed|ing)?\s*#?\d|most likely diagnosis)\b|"
        r"\b\d+(?:\.\d+)?\s*%\s*(?:probability|chance|xác suất)\s*(?:of|của)?\s*(?:pneumonia|tb|cancer|malignancy|heart failure|ild|aas)",
        lowered,
    )
    action = re.search(
        r"\b(phải|hãy|cần phải)\s+(điều trị|dùng thuốc|xét nghiệm|chụp|sinh thiết|dẫn lưu|nhập viện)|"
        r"\b(start|administer|perform|order|schedule|admit)\s+(treatment|therapy|medication|test|ct|imaging|biopsy|drainage|patient)",
        lowered,
    )
    _clinical_assert(ranking is None, case_id, "NO_DISEASE_RANKING_WINNER_OR_PROBABILITY")
    _clinical_assert(action is None, case_id, "NO_AUTONOMOUS_TREATMENT_TESTING_PROCEDURE_OR_DISPOSITION")


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_real_cross_disease_arbitration_semantics(case_id):
    case = CASES[case_id]
    report = _report(case_id)
    lowered = report.lower()
    _assert_no_ranking_or_autonomous_action(report, case_id)

    for hypothesis in case["arbitration"]["hypotheses"]:
        _clinical_assert(hypothesis["state"] in report, case_id, f"HYPOTHESIS_STATE/{hypothesis['name']}")
    for state in case["expected_states"]:
        _clinical_assert(state in report, case_id, f"RELATION_STATE/{state}")
    _clinical_assert(PRIORITY_LABEL[case["expected_priority"]] in report, case_id, "REVIEW_PRIORITY_SEPARATE_FROM_SUPPORT")
    _clinical_assert("no_numeric_ranking: true" in report, case_id, "NO_NUMERIC_RANKING_SCHEMA")

    if case_id == "AR01":
        _clinical_assert(report.count("dyspnea") <= 3 or report.count("khó thở") <= 3, case_id, "SHARED_DYSPNEA_NOT_DUPLICATED_PER_MODULE")
    elif case_id == "AR02":
        _clinical_assert("fever" in lowered or "sốt" in lowered, case_id, "DISTINCT_PNEUMONIA_EVIDENCE")
        _clinical_assert("echo" in lowered, case_id, "DISTINCT_HF_EVIDENCE")
    elif case_id == "AR03":
        _clinical_assert("COEXISTING_PROCESSES_SUPPORTED" in report, case_id, "INDEPENDENTLY_SUPPORTED_PROCESSES_CAN_COEXIST")
    elif case_id == "AR04":
        _clinical_assert("EVIDENCE_ATTRIBUTION_UNRESOLVED" in report, case_id, "CAVITY_WEIGHT_LOSS_DO_NOT_FORCE_TB_OR_MALIGNANCY")
    elif case_id == "AR05":
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" in report, case_id, "TB_CONFIRMATION_PRESERVED")
        _clinical_assert("pulmonary malignancy" in lowered or "ác tính phổi" in lowered, case_id, "MALIGNANCY_CONCERN_NOT_ERASED")
    elif case_id == "AR06":
        _clinical_assert("microbiology" in lowered or "vi sinh" in lowered, case_id, "TB_SITE_PROVENANCE")
        _clinical_assert("pathology" in lowered or "giải phẫu bệnh" in lowered, case_id, "CANCER_SITE_PROVENANCE")
    elif case_id == "AR07":
        _clinical_assert("EVIDENCE_ATTRIBUTION_UNRESOLVED" in report, case_id, "ILD_HF_SHARED_EVIDENCE_UNRESOLVED")
    elif case_id == "AR08":
        _clinical_assert("PPF_CRITERIA_MET" not in report, case_id, "EDEMA_NOT_COUNTED_AS_PPF_PROGRESSION")
    elif case_id == "AR10":
        _clinical_assert("CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION" not in report, case_id, "EFFUSION_ALONE_IS_NOT_MPE")
    elif case_id == "AR11":
        _clinical_assert("CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION" in report, case_id, "MPE_CONFIRMATION_PRESERVED")
        _clinical_assert("heart failure" in lowered or "suy tim" in lowered, case_id, "HF_COEXISTENCE_PRESERVED")
    elif case_id == "AR14":
        _clinical_assert("EVIDENCE_ATTRIBUTION_UNRESOLVED" in report, case_id, "UNILATERAL_EFFUSION_DOES_NOT_SELECT_TB_OR_MALIGNANCY")
    elif case_id == "AR17":
        _clinical_assert(report.count("chest pain") <= 3 or report.count("đau ngực") <= 3, case_id, "CHEST_PAIN_NOT_DOUBLE_COUNTED")
    elif case_id == "AR18":
        _clinical_assert("HYPOTHESIS_INDETERMINATE" in report and "REVIEW_PRIORITY_HIGH" in report, case_id, "URGENCY_IS_NOT_CERTAINTY")
    elif case_id == "AR19":
        _clinical_assert("HYPOTHESIS_SUPPORTED" in report and "REVIEW_PRIORITY_ROUTINE" in report, case_id, "CERTAINTY_IS_NOT_ACUTE_URGENCY")
    elif case_id == "AR20":
        _clinical_assert("No finding" in report, case_id, "NO_FINDING_PRESERVED")
        _clinical_assert("ct" in lowered, case_id, "CT_DISEASE_EVIDENCE_PRESERVED")
    elif case_id == "AR23":
        _clinical_assert("DUPLICATE_EVIDENCE_DEDUPLICATED" in report, case_id, "OVERLAPPING_LABELS_COUNT_ONCE")
        _clinical_assert(all(label in report for label in ("Consolidation", "Lung Opacity", "Infiltration")), case_id, "UPSTREAM_LABEL_PROVENANCE_PRESERVED")
    elif case_id == "AR28":
        _clinical_assert("naat" in lowered and "culture" in lowered, case_id, "BOTH_TEMPORAL_MICROBIOLOGY_RESULTS_PRESERVED")
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" in report, case_id, "CURRENT_TB_CONFIRMATION_UPDATED")
    elif case_id == "AR30":
        _clinical_assert("HYPOTHESIS_CONFLICTED" in report, case_id, "UNCERTAIN_BIOPSY_CORRESPONDENCE_PRESERVES_CONFLICT")
    elif case_id == "AR37":
        _clinical_assert("REVIEW_PRIORITY_HIGH" in report, case_id, "PNEUMOTHORAX_DRIVES_GLOBAL_PRIORITY")
        _clinical_assert(not re.search(r"malignan.{0,40}(lower probability|ít khả năng hơn)", lowered), case_id, "PRIORITY_DOES_NOT_RANK_MALIGNANCY")
    elif case_id == "AR39":
        _clinical_assert("DISTINCT_EVIDENCE_PRESENT" not in report, case_id, "NO_DISTINCT_EVIDENCE_INVENTED")
    elif case_id == "AR40":
        _clinical_assert("FINAL_REPORT" not in report, case_id, "ARBITRATION_IS_NOT_DIRECT_FINAL_REPORT")
    elif case_id == "AR42":
        _clinical_assert("clinician" in lowered or "bác sĩ" in lowered, case_id, "CLINICIAN_PROVENANCE_PRESERVED")
        _clinical_assert("module" in lowered, case_id, "MODULE_EVIDENCE_PRESERVED")
