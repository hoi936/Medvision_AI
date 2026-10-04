"""Provider-backed pulmonary malignancy disease-analysis cases PM01-PM18."""

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
    / "disease_analysis_pulmonary_malignancy"
    / "cases.json"
)
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}
REAL_CASE_IDS = [f"PM{number:02d}" for number in range(1, 19)]


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")

    for file_path in (
        "references/pulmonary_malignancy/PULMONARY_MALIGNANCY_POLICY.md",
        "references/pulmonary_malignancy/PULMONARY_MALIGNANCY_EVIDENCE.md",
        "references/pulmonary_malignancy/references.md",
    ):
        result = inspect_hermes_skill("medvision-disease-analysis", file_path)
        if result.get("file") != file_path:
            pytest.fail(
                f"INFRASTRUCTURE_CONFIGURATION: skill_view failed for {file_path}"
            )
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
        r"\b(phải|hãy|chỉ định|tiến hành)\s+(chụp|pet|sinh thiết|nội soi|"
        r"phẫu thuật|điều trị|theo dõi)|"
        r"\b(order|perform|schedule|start|administer|recommend)\s+"
        r"(ct|pet|biopsy|bronchoscopy|surgery|surveillance|oncology|treatment)",
        report.lower(),
    )
    _clinical_assert(
        prohibited is None,
        case_id,
        "NO_AUTONOMOUS_CT_PET_BIOPSY_BRONCHOSCOPY_SURGERY_SURVEILLANCE_OR_TREATMENT",
    )


def _assert_not_confirmed_by_imaging(report, case_id):
    lowered = report.lower()
    prohibited = (
        "ung thư phổi đã xác nhận từ hình ảnh",
        "hình ảnh xác nhận ung thư phổi",
        "cancer confirmed by imaging",
        "imaging confirms lung cancer",
    )
    _clinical_assert(
        "PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY" not in report,
        case_id,
        "PATHOLOGY_STATE_REQUIRES_EXPLICIT_PATHOLOGY",
    )
    _clinical_assert(
        not any(term in lowered for term in prohibited),
        case_id,
        "IMAGING_DOES_NOT_CONFIRM_CANCER",
    )


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_real_pulmonary_malignancy_semantics(case_id):
    report = _report(case_id)
    lowered = report.lower()
    _assert_no_autonomous_action(report, case_id)

    if case_id not in {"PM17", "PM18"}:
        _assert_not_confirmed_by_imaging(report, case_id)

    if case_id == "PM01":
        _clinical_assert(
            "IMAGING_LESION_WITHOUT_SUFFICIENT_MALIGNANCY_CONTEXT" in report,
            case_id,
            "CXR_ONLY_STATE",
        )
        _clinical_assert("Nodule/Mass" in report, case_id, "AI_PROVENANCE")
        _clinical_assert(
            "growth_status: unknown" in report or "tăng trưởng: chưa rõ" in lowered,
            case_id,
            "MISSING_PRIOR_REMAINS_UNKNOWN",
        )
    elif case_id == "PM02":
        _clinical_assert(
            "PULMONARY_MALIGNANCY_CONCERN_SUPPORTED" in report,
            case_id,
            "SUSPICIOUS_CT_SUPPORTS_BOUNDED_CONCERN",
        )
        _clinical_assert(
            "tua gai" in lowered or "spicul" in lowered,
            case_id,
            "MORPHOLOGY_PROVENANCE",
        )
    elif case_id == "PM03":
        _clinical_assert(
            "PULMONARY_MALIGNANCY_CONCERN_SUPPORTED" in report,
            case_id,
            "TRUE_GROWTH_SUPPORTS_BOUNDED_CONCERN",
        )
        _clinical_assert(
            "cùng một" in lowered or "same lesion" in lowered,
            case_id,
            "LESION_CORRESPONDENCE",
        )
    elif case_id == "PM04":
        _clinical_assert(
            "PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE" in report,
            case_id,
            "INCOMPLETE_CT_STATE",
        )
        _clinical_assert(
            "unknown" in lowered or "chưa rõ" in lowered,
            case_id,
            "GROWTH_UNKNOWN",
        )
    elif case_id == "PM05":
        _clinical_assert("Calcification" in report, case_id, "CALCIFICATION_PRESERVED")
        _clinical_assert(
            "Nodule/Mass" in report,
            case_id,
            "NODULE_MASS_PRESERVED",
        )
        _clinical_assert(
            not re.search(r"(vôi hóa|calcification).{0,50}(xác nhận|proves?)\s+(lành|benign)", lowered),
            case_id,
            "GENERIC_CALCIFICATION_IS_NOT_BENIGNITY",
        )
    elif case_id == "PM06":
        _clinical_assert(
            "vôi hóa trung tâm" in lowered or "central calcification" in lowered,
            case_id,
            "TRUSTED_CT_PATTERN_PRESERVED",
        )
        _clinical_assert(
            "lung-rads" not in lowered,
            case_id,
            "NO_LUNG_RADS_WITHOUT_SCREENING_CONTEXT",
        )
    elif case_id == "PM07":
        _clinical_assert(
            "34 mm" in lowered and ("khối" in lowered or "mass" in lowered),
            case_id,
            "RELIABLE_CT_MASS_TERM",
        )
        _clinical_assert(
            not re.search(r"(stage|giai đoạn|resectab|khả năng phẫu thuật)\s*[:=]\s*\w+", lowered),
            case_id,
            "NO_STAGE_OR_RESECTABILITY_INFERENCE",
        )
    elif case_id == "PM08":
        _clinical_assert("35%" in report, case_id, "EXTERNAL_ESTIMATE_PRESERVED")
        _clinical_assert(
            "bên ngoài" in lowered or "external" in lowered or "bác sĩ điều trị" in lowered,
            case_id,
            "EXTERNAL_ESTIMATE_PROVENANCE",
        )
        _clinical_assert(
            not re.search(r"(medvision|chúng tôi|we)\s+.{0,30}(ước tính|estimate).{0,20}35%", lowered),
            case_id,
            "NO_HIDDEN_MEDVISION_PROBABILITY",
        )
    elif case_id == "PM09":
        _clinical_assert("No finding" in report, case_id, "CXR_RESULT_PRESERVED")
        _clinical_assert("ct" in lowered and "nốt phổi" in lowered, case_id, "CT_LESION_PRESERVED")
        _clinical_assert(
            "NO_FINDING_CONTRADICTION" not in report,
            case_id,
            "NO_TARGET_IMAGE_CONTRADICTION",
        )
    elif case_id == "PM10":
        _clinical_assert("Other lesion" in report, case_id, "AI_PROVENANCE_PRESERVED")
        _clinical_assert("ct" in lowered and "nốt phổi" in lowered, case_id, "EXTERNAL_CHARACTERIZATION")
    elif case_id == "PM11":
        _clinical_assert(
            "ba nốt" in lowered or "three" in lowered or "3 nốt" in lowered,
            case_id,
            "MULTIPLE_LESIONS_PRESERVED",
        )
        _clinical_assert(
            not re.search(r"(xác nhận|confirmed|definite).{0,30}(di căn|metasta)", lowered),
            case_id,
            "MULTIPLICITY_DOES_NOT_CONFIRM_METASTASES",
        )
    elif case_id == "PM12":
        _clinical_assert("screen" in lowered or "sàng lọc" in lowered, case_id, "SCREENING_CONTEXT")
        _clinical_assert("lung-rads" in lowered, case_id, "SCREENING_SCOPE")
    elif case_id == "PM13":
        _clinical_assert(
            "tình cờ" in lowered or "incidental" in lowered,
            case_id,
            "INCIDENTAL_CONTEXT",
        )
        _clinical_assert(
            "fleischner" in lowered or "acr" in lowered,
            case_id,
            "INCIDENTAL_GUIDELINE_SCOPE",
        )
    elif case_id == "PM14":
        _clinical_assert(
            "PULMONARY_MALIGNANCY_CONCERN_SUPPORTED" in report,
            case_id,
            "MALIGNANCY_CONCERN_PRESERVED",
        )
        _clinical_assert(
            "pneumonia" in lowered or "viêm phổi" in lowered,
            case_id,
            "PNEUMONIA_HYPOTHESIS_PRESERVED",
        )
    elif case_id == "PM15":
        _clinical_assert(
            "PULMONARY_MALIGNANCY_CONCERN_CONFLICTED" in report
            or "PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE" in report,
            case_id,
            "NONDIAGNOSTIC_SAMPLE_REMAINS_UNRESOLVED",
        )
        _clinical_assert(
            "không chẩn đoán" in lowered or "nondiagnostic" in lowered,
            case_id,
            "SAMPLE_LIMITATION_PRESERVED",
        )
    elif case_id == "PM16":
        _clinical_assert(
            "EVIDENCE_CONFLICT" in report
            and "PULMONARY_MALIGNANCY_CONCERN_CONFLICTED" in report,
            case_id,
            "PATHOLOGY_IMAGING_CONFLICT_PRESERVED",
        )
    elif case_id == "PM17":
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY" in report,
            case_id,
            "EXPLICIT_PATHOLOGY_CONFIRMATION",
        )
        _clinical_assert(
            "MALIGNANCY_ORIGIN_UNRESOLVED" in report,
            case_id,
            "UNKNOWN_ORIGIN_REMAINS_UNRESOLVED",
        )
    elif case_id == "PM18":
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY" in report,
            case_id,
            "EXPLICIT_PATHOLOGY_CONFIRMATION",
        )
        _clinical_assert(
            "adenocarcinoma" in lowered or "biểu mô tuyến" in lowered,
            case_id,
            "EXPLICIT_HISTOLOGY_PRESERVED",
        )
        _clinical_assert(
            "nguyên phát" in lowered or "primary" in lowered,
            case_id,
            "EXPLICIT_ORIGIN_PRESERVED",
        )
