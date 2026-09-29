"""Provider-backed TB/chronic mycobacterial thoracic infection cases."""

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
CASES_PATH = Path(__file__).parent / "golden_cases" / "disease_analysis_tb_chronic_mycobacterial" / "cases.json"
CASES = {case["id"]: case for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))}
REAL_CASE_IDS = [
    "TB01", "TB02", "TB04", "TB06", "TB07", "TB09", "TB10",
    "TB11", "TB13", "TB15", "TB17", "TB19", "TB21", "TB22",
    "TB25", "TB27", "TB28", "TB29", "TB30", "TB33", "TB34",
]


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")
    for file_path in (
        "references/tb_chronic_mycobacterial/TB_CHRONIC_MYCOBACTERIAL_POLICY.md",
        "references/tb_chronic_mycobacterial/TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md",
        "references/tb_chronic_mycobacterial/references.md",
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


def _assert_no_autonomous_action(report, case_id):
    prohibited = re.search(
        r"\b(phải|hãy|cần phải)\s+(xét nghiệm|lấy đờm|cách ly|truy vết|thông báo|điều trị|dùng thuốc|nhập viện|dẫn lưu|sinh thiết)|"
        r"\b(start|administer|perform|order|isolate|admit|notify|trace)\s+(sputum|naat|culture|treatment|therapy|antibiotic|anti-tb|patient|contacts|public health|drainage|biopsy)",
        report.lower(),
    )
    _clinical_assert(prohibited is None, case_id, "NO_AUTONOMOUS_TESTING_ISOLATION_CONTACT_TRACING_PUBLIC_HEALTH_TREATMENT_PROCEDURE_OR_DISPOSITION")


def _assert_not_confirmed(report, case_id):
    _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" not in report, case_id, "CONFIRMATION_REQUIRES_EXPLICIT_MTB_COMPLEX_MOLECULAR_OR_CULTURE_EVIDENCE")


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_real_tb_chronic_mycobacterial_semantics(case_id):
    report = _report(case_id)
    lowered = report.lower()
    _assert_no_autonomous_action(report, case_id)
    if case_id not in {"TB11", "TB13", "TB15", "TB19"}:
        _assert_not_confirmed(report, case_id)

    if case_id == "TB01":
        _clinical_assert("Calcification" in report, case_id, "UPSTREAM_CALCIFICATION_PRESERVED")
        _clinical_assert("PULMONARY_TB_" not in report and "TB_ACTIVITY_" not in report, case_id, "GENERIC_CALCIFICATION_DOES_NOT_ACTIVATE_TB_MODULE")
    elif case_id == "TB02":
        _clinical_assert("Pulmonary fibrosis" in report, case_id, "UPSTREAM_FIBROSIS_PRESERVED")
        _clinical_assert("PULMONARY_TB_" not in report and "TB_ACTIVITY_" not in report, case_id, "GENERIC_FIBROSIS_DOES_NOT_ACTIVATE_TB_MODULE")
    elif case_id == "TB04":
        _clinical_assert("PULMONARY_TB_CONCERN_INDETERMINATE" in report, case_id, "CAVITY_SUPPORTS_BOUNDED_CONCERN")
        _clinical_assert("CHRONIC_INFECTION_ETIOLOGY_UNRESOLVED" in report, case_id, "CAVITY_ETIOLOGY_UNRESOLVED")
    elif case_id == "TB06":
        _clinical_assert("igra" in lowered and "dương" in lowered, case_id, "POSITIVE_IGRA_PRESERVED")
        _clinical_assert("PULMONARY_TB_NOT_ESTABLISHED" in report, case_id, "IGRA_IS_NOT_ACTIVE_TB")
    elif case_id == "TB07":
        _clinical_assert("igra" in lowered and ("âm" in lowered or "negative" in lowered), case_id, "NEGATIVE_IGRA_PRESERVED")
        _clinical_assert("PULMONARY_TB_CONCERN_INDETERMINATE" in report, case_id, "NEGATIVE_IGRA_DOES_NOT_EXCLUDE_ACTIVE_TB")
    elif case_id == "TB09":
        _clinical_assert("AFB_DETECTED_SPECIES_UNRESOLVED" in report, case_id, "AFB_IS_NOT_SPECIES_SPECIFIC")
        _clinical_assert("ntm" in lowered, case_id, "NTM_DIFFERENTIAL_PRESERVED")
    elif case_id == "TB10":
        _clinical_assert("PULMONARY_TB_CONCERN_SUPPORTED" in report, case_id, "HIGH_CONTEXT_TB_CONCERN_PRESERVED")
        _clinical_assert("afb" in lowered and ("âm" in lowered or "negative" in lowered), case_id, "NEGATIVE_SMEAR_PRESERVED_WITHOUT_EXCLUSION")
    elif case_id == "TB11":
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" in report, case_id, "MTB_SPECIFIC_NAAT_CONFIRMATION")
        _clinical_assert("sputum" in lowered or "đờm" in lowered, case_id, "PULMONARY_SPECIMEN_PROVENANCE")
    elif case_id == "TB13":
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" in report, case_id, "MTB_CULTURE_CONFIRMATION")
        _clinical_assert("culture" in lowered and "naat" in lowered, case_id, "DISCORDANT_TEST_TIMING_PRESERVED")
    elif case_id == "TB15":
        _clinical_assert("No finding" in report, case_id, "NO_FINDING_CXR_PRESERVED")
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" in report, case_id, "MICROBIOLOGY_NOT_ERASED_BY_CXR")
        _clinical_assert("NO_FINDING_CONTRADICTION" not in report, case_id, "NO_FALSE_IMAGE_CONTRADICTION")
    elif case_id == "TB17":
        _clinical_assert("PLEURAL_TB_CONCERN_INDETERMINATE" in report, case_id, "ADA_ONLY_IS_BOUNDED_CONCERN")
        _clinical_assert("ada" in lowered, case_id, "ADA_PROVENANCE_PRESERVED")
    elif case_id == "TB19":
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" in report, case_id, "PLEURAL_MTB_NAAT_CONFIRMATION")
        _clinical_assert("pleur" in lowered or "màng phổi" in lowered, case_id, "PLEURAL_SPECIMEN_SITE_PRESERVED")
    elif case_id == "TB21":
        _clinical_assert("PATHOLOGY_SUPPORTED_TB" in report, case_id, "PATHOLOGY_SUPPORT_PRESERVED")
        _clinical_assert("PLEURAL_TB_CONCERN_SUPPORTED" in report, case_id, "NEGATIVE_PLEURAL_NAAT_NOT_UNIVERSAL_EXCLUSION")
    elif case_id == "TB22":
        _clinical_assert("CHRONIC_INFECTION_ETIOLOGY_UNRESOLVED" in report, case_id, "GRANULOMA_ETIOLOGY_UNRESOLVED")
        _clinical_assert("granul" in lowered, case_id, "GRANULOMATOUS_PATHOLOGY_PRESERVED")
    elif case_id == "TB25":
        _clinical_assert("TB_ACTIVITY_UNRESOLVED" in report, case_id, "CURRENT_ACTIVITY_UNRESOLVED")
        _clinical_assert("fibrosis" in lowered or "xơ" in lowered, case_id, "RESIDUAL_FIBROSIS_PRESERVED")
    elif case_id == "TB27":
        _clinical_assert("PNEUMONIA_HYPOTHESIS_SUPPORTED" in report, case_id, "PNEUMONIA_HYPOTHESIS_PRESERVED")
        _clinical_assert("PULMONARY_TB_CONCERN_INDETERMINATE" in report, case_id, "TB_CONCERN_COEXISTS")
    elif case_id == "TB28":
        _clinical_assert("PULMONARY_MALIGNANCY_CONCERN" in report, case_id, "MALIGNANCY_CONCERN_PRESERVED")
        _clinical_assert("PULMONARY_TB_CONCERN_SUPPORTED" in report, case_id, "TB_CONCERN_PRESERVED")
    elif case_id == "TB29":
        _clinical_assert("NTM_PULMONARY_DISEASE_NOT_ESTABLISHED" in report, case_id, "SINGLE_NTM_CULTURE_IS_INSUFFICIENT")
        _clinical_assert("ntm" in lowered, case_id, "NTM_SPECIES_CONTEXT_PRESERVED")
    elif case_id == "TB30":
        _clinical_assert("NTM_PULMONARY_DISEASE_CONCERN_SUPPORTED" in report, case_id, "REPEATED_SAME_SPECIES_WITH_FULL_CRITERIA")
        _clinical_assert("MICROBIOLOGICALLY_CONFIRMED_TB" not in report, case_id, "NTM_NOT_RELABELLED_AS_MTB")
    elif case_id == "TB33":
        _clinical_assert("0.93" in report and "0.89" in report, case_id, "MODEL_SCORES_PRESERVED")
        _clinical_assert(not re.search(r"(93|89)\s*%\s*(probability|chance|xác suất|nguy cơ).{0,20}(tb|lao)", lowered), case_id, "MODEL_SCORE_IS_NOT_TB_PROBABILITY")
    elif case_id == "TB34":
        _clinical_assert("PULMONARY_TB_CONCERN_SUPPORTED" in report, case_id, "ACTIVE_TB_CONCERN_PRESERVED")
        _clinical_assert("HIGH_PRIORITY" in report or "high priority" in lowered or "ưu tiên cao" in lowered, case_id, "SEVERE_RESPIRATORY_EVIDENCE_ESCALATES_REVIEW")
