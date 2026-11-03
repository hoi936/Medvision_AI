"""Provider-backed acute aortic syndrome cases AAS01-AAS18."""

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
    / "disease_analysis_acute_aortic_syndrome"
    / "cases.json"
)
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}
REAL_CASE_IDS = [f"AAS{number:02d}" for number in range(1, 19)]


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")

    for file_path in (
        "references/acute_aortic_syndrome/ACUTE_AORTIC_SYNDROME_POLICY.md",
        "references/acute_aortic_syndrome/ACUTE_AORTIC_SYNDROME_EVIDENCE.md",
        "references/acute_aortic_syndrome/references.md",
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
        r"\b(phải|hãy|cần phải)\s+(chụp|chỉ định|dùng|khởi trị|chuyển|"
        r"phẫu thuật|can thiệp|cho thuốc)|"
        r"\b(start|administer|perform|schedule)\s+(cta|tee|mri|"
        r"antihypertensive|anti-impulse|analgesia|surgery|repair|transfer)",
        report.lower(),
    )
    _clinical_assert(
        prohibited is None,
        case_id,
        "NO_AUTONOMOUS_IMAGING_MEDICATION_PROCEDURE_SURGERY_TRANSFER_OR_DISPOSITION",
    )


def _assert_not_definitively_confirmed(report, case_id):
    _clinical_assert(
        "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS" not in report,
        case_id,
        "CONFIRMATION_REQUIRES_DEFINITIVE_SOURCE",
    )
    lowered = report.lower()
    _clinical_assert(
        not re.search(
            r"(x-quang|cxr).{0,70}(xác nhận|confirmed).{0,40}"
            r"(aas|bóc tách|hội chứng động mạch chủ cấp)",
            lowered,
        ),
        case_id,
        "CXR_DOES_NOT_CONFIRM_AAS",
    )


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_real_acute_aortic_syndrome_semantics(case_id):
    report = _report(case_id)
    lowered = report.lower()
    _assert_no_autonomous_action(report, case_id)

    if case_id not in {"AAS05", "AAS13", "AAS14", "AAS15", "AAS16"}:
        _assert_not_definitively_confirmed(report, case_id)

    if case_id == "AAS01":
        _clinical_assert(
            "AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT" in report,
            case_id,
            "CXR_FINDING_ONLY_STATE",
        )
        _clinical_assert(
            "Aortic enlargement" in report,
            case_id,
            "UPSTREAM_FINDING_PRESERVED",
        )
    elif case_id == "AAS02":
        _clinical_assert(
            "ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED" in report,
            case_id,
            "ACUTE_SYNDROME_SUPPORTS_BOUNDED_CONCERN",
        )
        _clinical_assert(
            "HIGH_PRIORITY_CLINICAL_REVIEW" in report,
            case_id,
            "HIGH_RISK_SAFETY_PRIORITY",
        )
    elif case_id == "AAS03":
        _clinical_assert(
            "AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT" in report
            or "ACUTE_AORTIC_SYNDROME_NOT_ESTABLISHED" in report,
            case_id,
            "CHRONIC_ANEURYSM_IS_NOT_ACUTE_AAS",
        )
        _clinical_assert(
            "mạn" in lowered or "chronic" in lowered,
            case_id,
            "CHRONIC_PROVENANCE_PRESERVED",
        )
    elif case_id == "AAS04":
        _clinical_assert(
            "ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED" in report
            or "ACUTE_AORTIC_SYNDROME_CONCERN_INDETERMINATE" in report,
            case_id,
            "NO_FINDING_DOES_NOT_ERASE_ACUTE_CONCERN",
        )
        _clinical_assert(
            "NO_FINDING_CONTRADICTION" not in report,
            case_id,
            "SYMPTOMS_DO_NOT_CREATE_IMAGE_CONTRADICTION",
        )
    elif case_id == "AAS05":
        _clinical_assert(
            "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS" in report,
            case_id,
            "CTA_CONFIRMATION",
        )
        _clinical_assert("type B" in report, case_id, "EXPLICIT_SUBTYPE_PRESERVED")
        _clinical_assert("No finding" in report, case_id, "CXR_PROVENANCE_PRESERVED")
    elif case_id == "AAS06":
        _clinical_assert(
            "ACUTE_AORTIC_SYNDROME_CONCERN_INDETERMINATE" in report,
            case_id,
            "WIDENED_MEDIASTINUM_IS_ONLY_A_CLUE",
        )
        _clinical_assert(
            "trung thất rộng" in lowered or "widened mediastinum" in lowered,
            case_id,
            "CXR_CLUE_PRESERVED",
        )
    elif case_id == "AAS07":
        _clinical_assert(
            "Pleural effusion" in report,
            case_id,
            "PLEURAL_EFFUSION_PRESERVED",
        )
        _clinical_assert(
            not re.search(r"(xác nhận|confirmed).{0,30}(vỡ|rupture|hemothorax)", lowered),
            case_id,
            "EFFUSION_DOES_NOT_CONFIRM_RUPTURE",
        )
    elif case_id == "AAS08":
        _clinical_assert(
            "ACUTE_AORTIC_SYNDROME_NOT_ESTABLISHED" in report
            or "AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT" in report,
            case_id,
            "CHRONIC_RISK_WITHOUT_ACUTE_SYNDROME",
        )
        _clinical_assert(
            "di truyền" in lowered or "genetic" in lowered,
            case_id,
            "AORTOPATHY_PROVENANCE",
        )
    elif case_id == "AAS09":
        _clinical_assert(
            "ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED" in report,
            case_id,
            "STRONG_CLINICAL_CONCERN",
        )
        _clinical_assert(
            "AAS_SUBTYPE_UNRESOLVED" in report,
            case_id,
            "NO_SUBTYPE_WITHOUT_DEFINITIVE_SOURCE",
        )
    elif case_id == "AAS10":
        _clinical_assert("d-dimer" in lowered, case_id, "BIOMARKER_PRESERVED")
        _clinical_assert(
            not re.search(r"(loại trừ|ruled out|excluded).{0,30}(aas|động mạch chủ)", lowered),
            case_id,
            "LOW_D_DIMER_ALONE_DOES_NOT_RULE_OUT",
        )
    elif case_id == "AAS11":
        _clinical_assert("d-dimer" in lowered, case_id, "BIOMARKER_PRESERVED")
        _clinical_assert(
            not re.search(r"(xác nhận|confirmed).{0,30}(aas|động mạch chủ)", lowered),
            case_id,
            "HIGH_D_DIMER_ALONE_DOES_NOT_CONFIRM",
        )
    elif case_id == "AAS12":
        _clinical_assert("AAD-RS" in report, case_id, "EXTERNAL_SCORE_PRESERVED")
        _clinical_assert("2" in report, case_id, "EXTERNAL_SCORE_VALUE_PRESERVED")
        _clinical_assert(
            "bác sĩ" in lowered or "external" in lowered,
            case_id,
            "EXTERNAL_SCORE_PROVENANCE",
        )
    elif case_id == "AAS13":
        _clinical_assert(
            "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS" in report,
            case_id,
            "CTA_CONFIRMATION",
        )
        _clinical_assert("type A" in report, case_id, "EXPLICIT_SUBTYPE_PRESERVED")
    elif case_id == "AAS14":
        _clinical_assert(
            "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS" in report,
            case_id,
            "MRI_CONFIRMATION",
        )
        _clinical_assert(
            "tụ máu trong thành" in lowered or "intramural" in lowered,
            case_id,
            "EXPLICIT_IMH_SUBTYPE_PRESERVED",
        )
    elif case_id == "AAS15":
        _clinical_assert(
            "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS" in report,
            case_id,
            "EXPLICIT_AAS_CONFIRMATION",
        )
        _clinical_assert(
            "AAS_SUBTYPE_UNRESOLVED" in report,
            case_id,
            "MISSING_SUBTYPE_REMAINS_UNRESOLVED",
        )
    elif case_id == "AAS16":
        _clinical_assert(
            "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS" in report,
            case_id,
            "EXPLICIT_AAS_CONFIRMATION",
        )
        _clinical_assert(
            "MALPERFUSION_CONCERN" in report,
            case_id,
            "SUPPLIED_TERRITORY_SUPPORTS_MALPERFUSION_CONCERN",
        )
        _clinical_assert(
            "chi phải" in lowered or "right limb" in lowered,
            case_id,
            "SUPPLIED_TERRITORY_PRESERVED",
        )
    elif case_id == "AAS17":
        _clinical_assert(
            "ACUTE_AORTIC_SYNDROME_CONCERN_CONFLICTED" in report
            or "ACUTE_AORTIC_SYNDROME_NOT_ESTABLISHED" in report,
            case_id,
            "DEFINITIVE_NEGATIVE_IMAGING_BOUNDARY",
        )
        _clinical_assert(
            "cta" in lowered and ("x-quang" in lowered or "cxr" in lowered),
            case_id,
            "BOTH_MODALITIES_PRESERVED",
        )
    elif case_id == "AAS18":
        for term in ("Pneumothorax", "Consolidation", "Cardiomegaly"):
            _clinical_assert(term in report, case_id, f"{term}_PRESERVED")
        _clinical_assert(
            "pneumonia" in lowered or "viêm phổi" in lowered,
            case_id,
            "PNEUMONIA_HYPOTHESIS_PRESERVED",
        )
        _clinical_assert(
            "heart failure" in lowered or "suy tim" in lowered,
            case_id,
            "HEART_FAILURE_HYPOTHESIS_PRESERVED",
        )
