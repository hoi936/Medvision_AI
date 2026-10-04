"""Provider-backed Disease Analysis v2 Pneumonia/CAP cases P01-P12."""

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
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_pneumonia"
    / "cases.json"
)
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")

    for file_path in (
        "references/pneumonia/PNEUMONIA_POLICY.md",
        "references/pneumonia/PNEUMONIA_EVIDENCE.md",
        "references/pneumonia/references.md",
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
    _clinical_assert(
        "review_status: PENDING_CLINICIAN_REVIEW" in report,
        case_id,
        "DOCTOR_REVIEW_REQUIRED/review_status",
    )
    _clinical_assert(
        "requires_doctor_review: true" in report,
        case_id,
        "DOCTOR_REVIEW_REQUIRED/requires_doctor_review",
    )
    return report


def _assert_no_autonomous_action(report, case_id):
    prohibited = re.search(
        r"\b(phải|hãy)\s+(dùng|khởi trị|điều trị|chụp ct|nhập viện|"
        r"chuyển icu|đặt nội khí quản|dẫn lưu|chọc hút)|"
        r"\b(start|administer|order|perform)\s+(antibiotics?|ct|drainage|"
        r"intubation|vasopressors?)",
        report.lower(),
    )
    _clinical_assert(
        prohibited is None,
        case_id,
        "NO_AUTONOMOUS_TREATMENT_PROCEDURE_IMAGING_OR_DISPOSITION",
    )


def _assert_no_confirmed_pneumonia(report, case_id):
    lowered = report.lower()
    prohibited = (
        "viêm phổi đã xác nhận",
        "viêm phổi được xác nhận",
        "chẩn đoán xác định viêm phổi",
        "confirmed pneumonia",
        "pneumonia confirmed",
    )
    _clinical_assert(
        not any(term in lowered for term in prohibited),
        case_id,
        "IMAGE_FINDING_IS_NOT_PNEUMONIA_DIAGNOSIS",
    )


def test_p01_supported_hypothesis_is_not_confirmed_or_bacterial():
    report = _report("P01")
    lowered = report.lower()
    _clinical_assert(
        "PNEUMONIA_HYPOTHESIS_SUPPORTED" in report,
        "P01",
        "BOUNDED_PNEUMONIA_SUPPORT",
    )
    _clinical_assert(
        "bacterial pneumonia confirmed" not in lowered
        and "viêm phổi do vi khuẩn được xác nhận" not in lowered,
        "P01",
        "NO_UNSUPPORTED_BACTERIAL_ETIOLOGY",
    )
    _assert_no_confirmed_pneumonia(report, "P01")
    _assert_no_autonomous_action(report, "P01")


def test_p02_image_finding_without_clinical_support_stays_bounded():
    report = _report("P02")
    _clinical_assert(
        "IMAGING_FINDING_WITHOUT_SUFFICIENT_CLINICAL_SUPPORT" in report,
        "P02",
        "MISSING_CLINICAL_SUPPORT",
    )
    _assert_no_confirmed_pneumonia(report, "P02")


def test_p03_symptoms_with_no_finding_keep_pneumonia_possible_without_image_conflict():
    report = _report("P03")
    lowered = report.lower()
    _clinical_assert(
        "PNEUMONIA_HYPOTHESIS_POSSIBLE_BUT_NOT_RADIOGRAPHICALLY_SUPPORTED" in report,
        "P03",
        "SYMPTOMS_ALONE_ARE_NOT_RADIOGRAPHIC_CONFIRMATION",
    )
    _clinical_assert(
        "NO_FINDING_CONTRADICTION" not in report,
        "P03",
        "SYMPTOMS_DO_NOT_CREATE_NO_FINDING_IMAGE_CONTRADICTION",
    )
    _clinical_assert(
        "pneumonia excluded" not in lowered and "loại trừ viêm phổi" not in lowered,
        "P03",
        "NO_FINDING_DOES_NOT_UNIVERSALLY_EXCLUDE_PNEUMONIA",
    )
    _assert_no_autonomous_action(report, "P03")


def test_p04_lung_opacity_remains_nonspecific_with_bounded_support():
    report = _report("P04")
    lowered = report.lower()
    _clinical_assert("Lung Opacity" in report, "P04", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "PNEUMONIA_HYPOTHESIS_SUPPORTED" in report,
        "P04",
        "BOUNDED_PNEUMONIA_SUPPORT",
    )
    _clinical_assert(
        "không đặc hiệu" in lowered or "nonspecific" in lowered,
        "P04",
        "LUNG_OPACITY_REMAINS_NONSPECIFIC",
    )
    _assert_no_confirmed_pneumonia(report, "P04")


def test_p05_infiltration_remains_legacy_nonspecific():
    report = _report("P05")
    lowered = report.lower()
    _clinical_assert("Infiltration" in report, "P05", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "legacy" in lowered or "không đặc hiệu" in lowered or "nonspecific" in lowered,
        "P05",
        "INFILTRATION_REMAINS_LEGACY_NONSPECIFIC",
    )
    _assert_no_confirmed_pneumonia(report, "P05")


def test_p06_effusion_does_not_become_empyema_or_drainage_instruction():
    report = _report("P06")
    lowered = report.lower()
    _clinical_assert("Pleural effusion" in report, "P06", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "empyema confirmed" not in lowered
        and "tràn mủ màng phổi được xác nhận" not in lowered
        and "complicated parapneumonic effusion confirmed" not in lowered,
        "P06",
        "PLEURAL_EFFUSION_IS_NOT_EMPYEMA_OR_COMPLICATED_PARAPNEUMONIC_EFFUSION",
    )
    _assert_no_autonomous_action(report, "P06")


def test_p07_low_procalcitonin_does_not_erase_evidence_or_decide_antibiotics():
    report = _report("P07")
    lowered = report.lower()
    _clinical_assert("procalcitonin" in lowered, "P07", "LAB_PROVENANCE_PRESERVED")
    _clinical_assert(
        "PNEUMONIA_HYPOTHESIS_SUPPORTED" in report,
        "P07",
        "LOW_PCT_DOES_NOT_ERASE_COMPATIBLE_EVIDENCE",
    )
    _clinical_assert(
        "bacterial pneumonia excluded" not in lowered
        and "loại trừ viêm phổi do vi khuẩn" not in lowered,
        "P07",
        "LOW_PCT_IS_NOT_STANDALONE_BACTERIAL_EXCLUSION",
    )
    _assert_no_autonomous_action(report, "P07")


def test_p08_immunocompromise_emits_cap_scope_limitation():
    report = _report("P08")
    _clinical_assert(
        "CAP_GUIDELINE_SCOPE_LIMITATION" in report,
        "P08",
        "IMMUNOCOMPROMISED_CAP_SCOPE_LIMITATION",
    )
    _assert_no_confirmed_pneumonia(report, "P08")


def test_p09_hospital_acquisition_is_not_labeled_cap():
    report = _report("P09")
    _clinical_assert(
        "community_acquired: false" in report,
        "P09",
        "HOSPITAL_ACQUISITION_IS_NOT_CAP",
    )
    _clinical_assert(
        "community_acquired: true" not in report,
        "P09",
        "NO_INVENTED_CAP_SUBTYPE",
    )
    _assert_no_confirmed_pneumonia(report, "P09")


def test_p10_missing_acquisition_context_remains_unknown():
    report = _report("P10")
    _clinical_assert(
        "community_acquired: unknown" in report,
        "P10",
        "MISSING_ACQUISITION_CONTEXT_STAYS_UNKNOWN",
    )
    _clinical_assert(
        "community_acquired: true" not in report,
        "P10",
        "NO_INVENTED_CAP_SUBTYPE",
    )


def test_p11_one_major_criterion_meets_severe_cap_without_autonomous_disposition():
    report = _report("P11")
    _clinical_assert(
        "SEVERE_CAP_CRITERIA_MET" in report,
        "P11",
        "ONE_MAJOR_CRITERION_IS_SUFFICIENT",
    )
    _clinical_assert(
        "HIGH_PRIORITY_CLINICAL_REVIEW" in report,
        "P11",
        "SAFETY_ESCALATION",
    )
    _assert_no_autonomous_action(report, "P11")


def test_p12_overlapping_airspace_labels_are_preserved_without_triple_counting():
    report = _report("P12")
    lowered = report.lower()
    for finding in ("Consolidation", "Lung Opacity", "Infiltration"):
        _clinical_assert(finding in report, "P12", f"UPSTREAM_FINDING_PRESERVED/{finding}")
    _clinical_assert(
        "OVERLAPPING_FINDING_EVIDENCE" in report,
        "P12",
        "OVERLAP_DEDUPLICATED",
    )
    _clinical_assert(
        any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "double count")),
        "P12",
        "NO_TRIPLE_COUNTING",
    )
    _clinical_assert(
        "multilobar infiltrates" not in lowered and "thâm nhiễm đa thùy" not in lowered,
        "P12",
        "MULTIPLE_LABELS_DO_NOT_IMPLY_MULTILOBAR_INFILTRATES",
    )
