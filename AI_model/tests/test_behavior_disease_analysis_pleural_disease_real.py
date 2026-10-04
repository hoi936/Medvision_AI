"""Provider-backed pleural disease cases."""

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
    / "disease_analysis_pleural_disease"
    / "cases.json"
)
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}
REAL_CASE_IDS = [
    "PL01", "PL02", "PL03", "PL04", "PL07", "PL08", "PL09", "PL10",
    "PL12", "PL13", "PL15", "PL16", "PL17", "PL18", "PL19", "PL20",
    "PL21", "PL22", "PL23", "PL24",
]


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")

    for file_path in (
        "references/pleural_disease/PLEURAL_DISEASE_POLICY.md",
        "references/pleural_disease/PLEURAL_DISEASE_EVIDENCE.md",
        "references/pleural_disease/references.md",
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
        r"\b(phải|hãy|cần phải)\s+(chọc|chụp|sinh thiết|đặt|dẫn lưu|"
        r"dùng kháng sinh|phẫu thuật|điều trị|nhập viện)|"
        r"\b(start|administer|perform|schedule)\s+(thoracentesis|ct|pet|"
        r"biopsy|chest tube|ipc|pleurodesis|antibiotic|surgery|oncology)",
        report.lower(),
    )
    _clinical_assert(
        prohibited is None,
        case_id,
        "NO_AUTONOMOUS_IMAGING_DRAINAGE_BIOPSY_MEDICATION_ONCOLOGY_SURGERY_OR_DISPOSITION",
    )


def _assert_no_unjustified_confirmation(report, case_id):
    _clinical_assert(
        "CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION" not in report,
        case_id,
        "MPE_CONFIRMATION_REQUIRES_EXPLICIT_MALIGNANT_FLUID_CYTOLOGY",
    )
    _clinical_assert(
        "PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY" not in report,
        case_id,
        "PLEURAL_MALIGNANCY_CONFIRMATION_REQUIRES_TISSUE_PATHOLOGY",
    )
    _clinical_assert(
        "PATHOLOGY_CONFIRMED_MESOTHELIOMA" not in report,
        case_id,
        "MESOTHELIOMA_CONFIRMATION_REQUIRES_EXPLICIT_TISSUE_PATHOLOGY",
    )


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_real_pleural_disease_semantics(case_id):
    report = _report(case_id)
    lowered = report.lower()
    _assert_no_autonomous_action(report, case_id)

    if case_id not in {"PL12", "PL16", "PL17", "PL18"}:
        _assert_no_unjustified_confirmation(report, case_id)

    if case_id == "PL01":
        _clinical_assert("Pleural effusion" in report, case_id, "UPSTREAM_FINDING_PRESERVED")
        _clinical_assert(
            "PLEURAL_ETIOLOGY_UNRESOLVED" in report,
            case_id,
            "EFFUSION_ETIOLOGY_REMAINS_UNRESOLVED",
        )
    elif case_id == "PL02":
        _clinical_assert("Pleural thickening" in report, case_id, "UPSTREAM_FINDING_PRESERVED")
        _clinical_assert(
            "PLEURAL_ETIOLOGY_UNRESOLVED" in report,
            case_id,
            "THICKENING_ETIOLOGY_REMAINS_UNRESOLVED",
        )
    elif case_id == "PL03":
        _clinical_assert("Calcification" in report, case_id, "CALCIFICATION_PRESERVED")
        _clinical_assert(
            not re.search(r"(pleural plaque|mảng màng phổi).{0,30}(xác nhận|confirmed)", lowered),
            case_id,
            "GENERIC_CALCIFICATION_IS_NOT_PLEURAL_PLAQUE",
        )
    elif case_id == "PL04":
        _clinical_assert(
            "ASBESTOS_RELATED_PLEURAL_DISEASE_CONCERN" in report,
            case_id,
            "EXPLICIT_PLAQUE_AND_EXPOSURE_CONTEXT",
        )
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_MESOTHELIOMA" not in report,
            case_id,
            "PLAQUE_IS_NOT_MESOTHELIOMA",
        )
    elif case_id == "PL07":
        _clinical_assert(
            "PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE" in report,
            case_id,
            "RECURRENT_UNILATERAL_EFFUSION_IS_BOUNDED_CONCERN",
        )
        _clinical_assert(
            "MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED" in report,
            case_id,
            "RECURRENCE_DOES_NOT_CONFIRM_MPE",
        )
    elif case_id == "PL08":
        _clinical_assert(
            "PLEURAL_MALIGNANCY_CONCERN_SUPPORTED" in report,
            case_id,
            "SUSPICIOUS_CT_SUPPORTS_CONCERN",
        )
        _clinical_assert(
            "nodular" in lowered and ("circumferential" in lowered or "vòng quanh" in lowered),
            case_id,
            "CT_MORPHOLOGY_PROVENANCE",
        )
    elif case_id == "PL09":
        _clinical_assert("ct" in lowered, case_id, "NEGATIVE_CT_PROVENANCE")
        _clinical_assert(
            "PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE" in report,
            case_id,
            "NEGATIVE_CT_DOES_NOT_UNIVERSALLY_EXCLUDE",
        )
    elif case_id == "PL10":
        _clinical_assert(
            "âm tính" in lowered or "negative" in lowered,
            case_id,
            "NEGATIVE_CYTOLOGY_PRESERVED",
        )
        _clinical_assert(
            "MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED" in report,
            case_id,
            "NEGATIVE_CYTOLOGY_IS_NOT_MPE_CONFIRMATION",
        )
    elif case_id == "PL12":
        _clinical_assert(
            "CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION" in report,
            case_id,
            "EXPLICIT_MALIGNANT_FLUID_CYTOLOGY",
        )
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_MESOTHELIOMA" not in report,
            case_id,
            "GENERIC_MALIGNANT_CYTOLOGY_IS_NOT_MESOTHELIOMA",
        )
    elif case_id == "PL13":
        _clinical_assert(
            "MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED" in report,
            case_id,
            "KNOWN_LUNG_CANCER_DOES_NOT_CONFIRM_MPE",
        )
        _clinical_assert(
            not re.search(r"(confirmed|xác nhận).{0,30}(pleural metast|di căn màng phổi)", lowered),
            case_id,
            "NO_PLEURAL_METASTASIS_WITHOUT_DIRECT_EVIDENCE",
        )
    elif case_id == "PL15":
        _clinical_assert(
            "MESOTHELIOMA_CONCERN_SUPPORTED" in report,
            case_id,
            "BOUNDED_MESOTHELIOMA_CONCERN",
        )
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_MESOTHELIOMA" not in report,
            case_id,
            "NO_MESOTHELIOMA_CONFIRMATION_WITHOUT_TISSUE",
        )
    elif case_id == "PL16":
        _clinical_assert(
            "CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION" in report,
            case_id,
            "EXPLICIT_MALIGNANT_FLUID_CYTOLOGY",
        )
        _clinical_assert(
            "MESOTHELIOMA_NOT_ESTABLISHED" in report,
            case_id,
            "CYTOLOGY_ALONE_DOES_NOT_ESTABLISH_MESOTHELIOMA",
        )
    elif case_id == "PL17":
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_MESOTHELIOMA" in report,
            case_id,
            "EXPLICIT_TISSUE_PATHOLOGY",
        )
        _clinical_assert(
            "epithelioid" in lowered,
            case_id,
            "EXPLICIT_HISTOLOGIC_SUBTYPE_PRESERVED",
        )
    elif case_id == "PL18":
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY" in report,
            case_id,
            "EXPLICIT_SECONDARY_PLEURAL_MALIGNANCY",
        )
        _clinical_assert(
            "vú" in lowered or "breast" in lowered,
            case_id,
            "EXPLICIT_PRIMARY_ORIGIN_PRESERVED",
        )
        _clinical_assert(
            "PATHOLOGY_CONFIRMED_MESOTHELIOMA" not in report,
            case_id,
            "SECONDARY_MALIGNANCY_NOT_RELABELLED_MESOTHELIOMA",
        )
    elif case_id == "PL19":
        _clinical_assert(
            "PLEURAL_INFECTION_CONCERN_SUPPORTED" in report,
            case_id,
            "MULTIPLE_INFECTION_DOMAINS",
        )
        _clinical_assert(
            "microbiology" in lowered and ("mủ" in lowered or "purulent" in lowered),
            case_id,
            "FLUID_PROVENANCE_PRESERVED",
        )
    elif case_id == "PL20":
        _clinical_assert(
            "pneumonia" in lowered or "viêm phổi" in lowered,
            case_id,
            "PNEUMONIA_HYPOTHESIS_PRESERVED",
        )
        _clinical_assert(
            "PLEURAL_INFECTION_NOT_ESTABLISHED" in report,
            case_id,
            "EFFUSION_WITH_PNEUMONIA_IS_NOT_AUTOMATIC_INFECTION",
        )
    elif case_id == "PL21":
        _clinical_assert(
            "heart failure" in lowered or "suy tim" in lowered,
            case_id,
            "HF_HYPOTHESIS_PRESERVED",
        )
        _clinical_assert(
            "PLEURAL_ETIOLOGY_UNRESOLVED" in report,
            case_id,
            "EFFUSION_DOES_NOT_FORCE_CARDIOGENIC_ETIOLOGY",
        )
    elif case_id == "PL22":
        _clinical_assert("No finding" in report, case_id, "CXR_RESULT_PRESERVED")
        _clinical_assert(
            "ct" in lowered and ("nodular" in lowered or "nốt màng phổi" in lowered),
            case_id,
            "CT_PLEURAL_DISEASE_PRESERVED",
        )
        _clinical_assert(
            "NO_FINDING_CONTRADICTION" not in report,
            case_id,
            "NO_FALSE_IMAGE_CONTRADICTION",
        )
    elif case_id == "PL23":
        _clinical_assert("Other lesion" in report, case_id, "AI_PROVENANCE_PRESERVED")
        _clinical_assert(
            "ct" in lowered and ("pleural thickening" in lowered or "dày màng phổi" in lowered),
            case_id,
            "EXTERNAL_PLEURAL_CHARACTERIZATION",
        )
    elif case_id == "PL24":
        _clinical_assert("0.90" in report or "0.9" in report, case_id, "THICKENING_SCORE")
        _clinical_assert("0.95" in report, case_id, "EFFUSION_SCORE")
        _clinical_assert(
            not re.search(
                r"(90|95)%\s*(xác suất|khả năng|probability|chance).{0,35}"
                r"(mesothelioma|mpe|malignant pleural)",
                lowered,
            ),
            case_id,
            "MODEL_SCORES_ARE_NOT_DISEASE_PROBABILITIES",
        )
