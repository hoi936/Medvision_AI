"""Provider-backed Disease Analysis v2 Heart Failure cases HF01-HF15."""

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
    / "disease_analysis_heart_failure"
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
        "references/heart_failure/HEART_FAILURE_POLICY.md",
        "references/heart_failure/HEART_FAILURE_EVIDENCE.md",
        "references/heart_failure/references.md",
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
        r"\b(phải|hãy)\s+(dùng|khởi trị|điều trị|cho oxy|thở máy|"
        r"chụp ct|siêu âm tim|nhập viện|chuyển icu|dẫn lưu|chọc hút)|"
        r"\b(start|administer|order|perform)\s+(diuretics?|oxygen|ventilation|"
        r"vasopressors?|echo|ct|thoracentesis|drainage|admission)",
        report.lower(),
    )
    _clinical_assert(
        prohibited is None,
        case_id,
        "NO_AUTONOMOUS_TREATMENT_PROCEDURE_IMAGING_OR_DISPOSITION",
    )


def _assert_no_confirmed_hf(report, case_id):
    lowered = report.lower()
    prohibited = (
        "suy tim đã xác nhận",
        "suy tim được xác nhận",
        "chẩn đoán xác định suy tim",
        "confirmed heart failure",
        "heart failure confirmed",
    )
    _clinical_assert(
        not any(term in lowered for term in prohibited),
        case_id,
        "BOUNDED_HF_HYPOTHESIS_IS_NOT_FINAL_DIAGNOSIS",
    )


def test_hf01_cardiomegaly_only_does_not_confirm_hf_or_infer_ef_or_chamber():
    report = _report("HF01")
    lowered = report.lower()
    _clinical_assert(
        "IMAGING_FINDINGS_WITHOUT_SUFFICIENT_HF_CLINICAL_SUPPORT" in report,
        "HF01",
        "IMAGING_ONLY_SUPPORT_IS_INSUFFICIENT",
    )
    _clinical_assert("Cardiomegaly" in report, "HF01", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        not re.search(r"\bef\s*[:=]\s*\d|phân suất tống máu\s*[:=]\s*\d", lowered),
        "HF01",
        "EF_NOT_INFERRED_FROM_CXR",
    )
    _assert_no_confirmed_hf(report, "HF01")


def test_hf02_total_syndrome_supports_hf_and_preserves_echo_provenance():
    report = _report("HF02")
    lowered = report.lower()
    _clinical_assert(
        "HEART_FAILURE_HYPOTHESIS_SUPPORTED" in report,
        "HF02",
        "TOTAL_SYNDROME_AND_OBJECTIVE_EVIDENCE_SUPPORT_HF",
    )
    _clinical_assert("Cardiomegaly" in report, "HF02", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "siêu âm" in lowered or "echo" in lowered,
        "HF02",
        "ECHO_SOURCE_PRESERVED",
    )
    _assert_no_confirmed_hf(report, "HF02")


def test_hf03_effusion_alone_is_not_hf_transudate_or_drainage_need():
    report = _report("HF03")
    lowered = report.lower()
    _clinical_assert("Pleural effusion" in report, "HF03", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "transudate confirmed" not in lowered and "dịch thấm được xác nhận" not in lowered,
        "HF03",
        "EFFUSION_DOES_NOT_ESTABLISH_TRANSUDATE",
    )
    _assert_no_confirmed_hf(report, "HF03")
    _assert_no_autonomous_action(report, "HF03")


def test_hf04_generic_opacity_is_not_forced_to_edema_or_single_disease():
    report = _report("HF04")
    lowered = report.lower()
    _clinical_assert("Lung Opacity" in report, "HF04", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "không đặc hiệu" in lowered or "nonspecific" in lowered,
        "HF04",
        "GENERIC_OPACITY_REMAINS_NONSPECIFIC",
    )
    _clinical_assert(
        "pulmonary edema confirmed" not in lowered and "phù phổi được xác nhận" not in lowered,
        "HF04",
        "GENERIC_OPACITY_IS_NOT_PULMONARY_EDEMA",
    )
    _assert_no_confirmed_hf(report, "HF04")


def test_hf05_explicit_congestion_and_objective_evidence_support_bounded_states():
    report = _report("HF05")
    _clinical_assert(
        "CARDIOGENIC_CONGESTION_HYPOTHESIS_SUPPORTED" in report,
        "HF05",
        "EXPLICIT_CONGESTION_WITH_CARDIAC_SUPPORT",
    )
    _clinical_assert(
        "HEART_FAILURE_HYPOTHESIS_SUPPORTED" in report,
        "HF05",
        "TOTAL_HF_EVIDENCE_SUPPORT",
    )
    _assert_no_confirmed_hf(report, "HF05")
    _assert_no_autonomous_action(report, "HF05")


def test_hf06_elevated_np_alone_is_supportive_nonspecific_not_confirmation():
    report = _report("HF06")
    lowered = report.lower()
    _clinical_assert("nt-probnp" in lowered, "HF06", "NP_PROVENANCE_PRESERVED")
    _clinical_assert(
        "HF_OBJECTIVE_EVIDENCE_INCOMPLETE" in report,
        "HF06",
        "NP_ALONE_IS_INCOMPLETE",
    )
    _assert_no_confirmed_hf(report, "HF06")


def test_hf07_renal_dysfunction_modifies_np_without_discard_or_confirmation():
    report = _report("HF07")
    lowered = report.lower()
    _clinical_assert(
        "thận" in lowered or "renal" in lowered,
        "HF07",
        "RENAL_MODIFIER_PRESERVED",
    )
    _clinical_assert("bnp" in lowered, "HF07", "NP_NOT_DISCARDED")
    _assert_no_confirmed_hf(report, "HF07")


def test_hf08_obesity_and_low_np_do_not_erase_strong_objective_evidence():
    report = _report("HF08")
    lowered = report.lower()
    _clinical_assert(
        "béo phì" in lowered or "obesity" in lowered,
        "HF08",
        "OBESITY_MODIFIER_PRESERVED",
    )
    _clinical_assert(
        "HEART_FAILURE_HYPOTHESIS_SUPPORTED" in report,
        "HF08",
        "LOW_NP_NOT_UNIVERSAL_EXCLUSION",
    )
    _clinical_assert(
        "heart failure excluded" not in lowered and "loại trừ suy tim" not in lowered,
        "HF08",
        "HF_NOT_EXCLUDED_BY_LOW_NP",
    )


def test_hf09_no_finding_does_not_exclude_hf_or_create_image_conflict():
    report = _report("HF09")
    lowered = report.lower()
    _clinical_assert(
        "HEART_FAILURE_POSSIBLE_WITHOUT_RADIOGRAPHIC_CONGESTION" in report
        or "HEART_FAILURE_HYPOTHESIS_SUPPORTED" in report,
        "HF09",
        "HF_CAN_EXIST_WITHOUT_CXR_CONGESTION",
    )
    _clinical_assert(
        "NO_FINDING_CONTRADICTION" not in report,
        "HF09",
        "NO_FINDING_HAS_NO_TARGET_FINDING_CONTRADICTION",
    )
    _clinical_assert(
        "heart failure excluded" not in lowered and "loại trừ suy tim" not in lowered,
        "HF09",
        "NO_FINDING_DOES_NOT_EXCLUDE_HF",
    )


def test_hf10_current_phenotype_uses_echo_not_cxr_and_preserves_source():
    report = _report("HF10")
    lowered = report.lower()
    _clinical_assert(
        "siêu âm" in lowered or "echo" in lowered,
        "HF10",
        "PHENOTYPE_EVIDENCE_SOURCE_PRESERVED",
    )
    _clinical_assert(
        not re.search(r"x-quang[^\n]{0,80}(suy ra|xác định)[^\n]{0,40}(ef|phân suất)", lowered),
        "HF10",
        "EF_NOT_INFERRED_FROM_CXR",
    )
    _assert_no_confirmed_hf(report, "HF10")


def test_hf11_hfpef_requires_more_than_preserved_ef_alone():
    report = _report("HF11")
    lowered = report.lower()
    _clinical_assert(
        "áp lực đổ đầy" in lowered or "filling pressure" in lowered,
        "HF11",
        "OBJECTIVE_FILLING_PRESSURE_EVIDENCE_PRESERVED",
    )
    _clinical_assert(
        "preserved ef alone confirms hfpef" not in lowered
        and "ef bảo tồn đơn độc xác nhận hfpef" not in lowered,
        "HF11",
        "PRESERVED_EF_ALONE_IS_INSUFFICIENT",
    )
    _assert_no_confirmed_hf(report, "HF11")


def test_hf12_generic_opacity_stays_nonspecific_while_explicit_congestion_supports_hypothesis():
    report = _report("HF12")
    lowered = report.lower()
    _clinical_assert(
        "CARDIOGENIC_CONGESTION_HYPOTHESIS_SUPPORTED" in report,
        "HF12",
        "TRUSTED_EXPLICIT_CONGESTION_SUPPORT",
    )
    _clinical_assert("Lung Opacity" in report, "HF12", "UPSTREAM_FINDING_PRESERVED")
    _clinical_assert(
        "không đặc hiệu" in lowered or "nonspecific" in lowered,
        "HF12",
        "GENERIC_OPACITY_REMAINS_NONSPECIFIC",
    )
    _clinical_assert(
        not re.search(r"\b\d+(?:\.\d+)?%\s*(xác suất|khả năng|probability|chance)\s*(suy tim|hf)", lowered),
        "HF12",
        "NO_HIDDEN_DISEASE_SCORE",
    )


def test_hf13_pneumonia_and_hf_remain_separate_without_shared_evidence_double_counting():
    report = _report("HF13")
    lowered = report.lower()
    _clinical_assert(
        "pneumonia" in lowered or "viêm phổi" in lowered,
        "HF13",
        "PNEUMONIA_HYPOTHESIS_PRESERVED",
    )
    _clinical_assert(
        "heart failure" in lowered or "suy tim" in lowered,
        "HF13",
        "HF_HYPOTHESIS_PRESERVED",
    )
    _clinical_assert(
        any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "double count")),
        "HF13",
        "SHARED_EVIDENCE_NOT_DOUBLE_COUNTED",
    )
    _clinical_assert(
        "confirmed winner" not in lowered and "kết luận bên thắng" not in lowered,
        "HF13",
        "NO_FORCED_WINNER",
    )


def test_hf14_trusted_later_evidence_creates_explicit_conflict_with_timing():
    report = _report("HF14")
    lowered = report.lower()
    _clinical_assert(
        "HEART_FAILURE_HYPOTHESIS_CONFLICTED" in report,
        "HF14",
        "TRUSTED_HF_CONFLICT",
    )
    _clinical_assert("EVIDENCE_CONFLICT" in report, "HF14", "CONFLICT_PRESERVED")
    _clinical_assert(
        "sau đó" in lowered or "later" in lowered,
        "HF14",
        "SOURCE_TIMING_PRESERVED",
    )


def test_hf15_high_risk_state_escalates_review_without_autonomous_actions():
    report = _report("HF15")
    _clinical_assert(
        "HIGH_PRIORITY_CLINICAL_REVIEW" in report,
        "HF15",
        "SAFETY_PRIORITY_SIGNAL",
    )
    _assert_no_autonomous_action(report, "HF15")
