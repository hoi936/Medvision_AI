"""Provider-backed ILD/fibrotic ILD cases."""

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
    / "disease_analysis_ild_fibrotic"
    / "cases.json"
)
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}
REAL_CASE_IDS = [
    "ILD01", "ILD02", "ILD04", "ILD05", "ILD09", "ILD11",
    "ILD14", "ILD16", "ILD18", "ILD20", "ILD21", "ILD22",
    "ILD25", "ILD26", "ILD27", "ILD28", "ILD29", "ILD30",
]


@pytest.fixture(scope="module", autouse=True)
def provider_preflight():
    try:
        metadata = run_provider_preflight()
    except ProviderPreflightError as exc:
        pytest.fail(f"{exc.classification}: {exc.reason}")

    for file_path in (
        "references/ild_fibrotic/ILD_FIBROTIC_POLICY.md",
        "references/ild_fibrotic/ILD_FIBROTIC_EVIDENCE.md",
        "references/ild_fibrotic/references.md",
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
        r"\b(phải|hãy|cần phải)\s+(dùng|khởi trị|cho oxy|chụp|đo pft|"
        r"nội soi|sinh thiết|chuyển ghép|nhập viện)|"
        r"\b(start|administer|perform|schedule)\s+(antifibrotic|steroid|"
        r"immunosuppress|oxygen|hrct|pft|bal|biopsy|transplant|admission)",
        report.lower(),
    )
    _clinical_assert(
        prohibited is None,
        case_id,
        "NO_AUTONOMOUS_TREATMENT_TESTING_PROCEDURE_TRANSPLANT_OR_DISPOSITION",
    )


def _assert_no_automatic_ipf(report, case_id):
    lowered = report.lower()
    _clinical_assert(
        not re.search(
            r"(xác nhận|confirmed|definitive).{0,40}(ipf|xơ phổi vô căn)",
            lowered,
        ),
        case_id,
        "NO_AUTOMATIC_IPF_CONFIRMATION",
    )


@pytest.mark.parametrize("case_id", REAL_CASE_IDS)
def test_real_ild_fibrotic_semantics(case_id):
    report = _report(case_id)
    lowered = report.lower()
    _assert_no_autonomous_action(report, case_id)

    if case_id not in {"ILD29"}:
        _assert_no_automatic_ipf(report, case_id)

    if case_id == "ILD01":
        _clinical_assert(
            "ILD_HYPOTHESIS_SUPPORTED" in report,
            case_id,
            "BOUNDED_ILD_SUPPORT",
        )
        _clinical_assert(
            "HRCT_PATTERN_NOT_ASSESSABLE" in report,
            case_id,
            "NO_HRCT_CATEGORY_FROM_CXR",
        )
    elif case_id == "ILD02":
        _clinical_assert(
            "FIBROTIC_ILD_HYPOTHESIS_SUPPORTED" in report
            or "ILD_HYPOTHESIS_SUPPORTED" in report,
            case_id,
            "BOUNDED_FIBROTIC_EVIDENCE",
        )
        _clinical_assert(
            "HRCT_PATTERN_NOT_ASSESSABLE" in report,
            case_id,
            "NO_UIP_FROM_CXR",
        )
    elif case_id == "ILD04":
        _clinical_assert(
            "HRCT_PATTERN_NOT_ASSESSABLE" in report,
            case_id,
            "CXR_CANNOT_CLASSIFY_HRCT",
        )
        _clinical_assert(
            "honeycombing" not in lowered and "traction bronchiectasis" not in lowered,
            case_id,
            "NO_INVENTED_HRCT_MORPHOLOGY",
        )
    elif case_id == "ILD05":
        _clinical_assert("HRCT_PATTERN_UIP" in report, case_id, "EXPLICIT_UIP_PRESERVED")
        _clinical_assert(
            "IPF_NOT_ESTABLISHED" in report
            and "ILD_ETIOLOGY_UNRESOLVED" in report,
            case_id,
            "UIP_IS_NOT_AUTOMATIC_IPF",
        )
    elif case_id == "ILD09":
        _clinical_assert("HRCT_PATTERN_UIP" in report, case_id, "UIP_PATTERN_PRESERVED")
        _clinical_assert(
            "CTD_ILD_CONCERN_SUPPORTED" in report,
            case_id,
            "ESTABLISHED_CTD_CONTEXT_PRESERVED",
        )
    elif case_id == "ILD11":
        _clinical_assert("ana" in lowered, case_id, "ANA_PROVENANCE_PRESERVED")
        _clinical_assert(
            "CTD_ILD_CONCERN_SUPPORTED" not in report,
            case_id,
            "ANA_ALONE_DOES_NOT_CONFIRM_CTD_ILD",
        )
        _clinical_assert(
            "ILD_ETIOLOGY_UNRESOLVED" in report,
            case_id,
            "INCOMPLETE_AUTOIMMUNE_EVIDENCE",
        )
    elif case_id == "ILD14":
        _clinical_assert(
            "FIBROTIC_HP_CONCERN_SUPPORTED" in report,
            case_id,
            "MULTIPLE_HP_DOMAINS_SUPPORT_CONCERN",
        )
        _clinical_assert(
            "mdd" in lowered or "đa chuyên khoa" in lowered,
            case_id,
            "MDD_PROVENANCE_PRESERVED",
        )
    elif case_id == "ILD16":
        _clinical_assert("No finding" in report, case_id, "CXR_RESULT_PRESERVED")
        _clinical_assert(
            "hrct" in lowered and ("fibrotic ild" in lowered or "ild xơ hóa" in lowered),
            case_id,
            "HRCT_ILD_PRESERVED",
        )
        _clinical_assert(
            "NO_FINDING_CONTRADICTION" not in report,
            case_id,
            "NO_FALSE_IMAGE_CONTRADICTION",
        )
    elif case_id == "ILD18":
        _clinical_assert(
            "PPF_NOT_ASSESSABLE" in report,
            case_id,
            "SINGLE_STUDY_IS_NOT_PROGRESSION",
        )
    elif case_id == "ILD20":
        _clinical_assert(
            "PPF_CRITERIA_NOT_MET" in report,
            case_id,
            "FVC_AND_DLCO_ARE_ONE_DOMAIN",
        )
        _clinical_assert(
            "PHYSIOLOGY" in report,
            case_id,
            "PHYSIOLOGY_DOMAIN_PRESERVED",
        )
    elif case_id == "ILD21":
        _clinical_assert("PPF_CRITERIA_MET" in report, case_id, "SYMPTOMS_PLUS_PHYSIOLOGY")
    elif case_id == "ILD22":
        _clinical_assert("PPF_CRITERIA_MET" in report, case_id, "PHYSIOLOGY_PLUS_RADIOLOGY")
    elif case_id == "ILD25":
        _clinical_assert(
            "PPF_CRITERIA_MET" not in report,
            case_id,
            "PPF_DEFINITION_NOT_APPLIED_TO_IPF",
        )
        _clinical_assert("ipf" in lowered, case_id, "IPF_TRAJECTORY_PRESERVED")
    elif case_id == "ILD26":
        _clinical_assert(
            "pneumonia" in lowered or "viêm phổi" in lowered,
            case_id,
            "PNEUMONIA_HYPOTHESIS_PRESERVED",
        )
        _clinical_assert(
            "PPF_CRITERIA_MET" not in report,
            case_id,
            "ACUTE_INFECTION_NOT_COUNTED_AS_PPF",
        )
    elif case_id == "ILD27":
        _clinical_assert(
            "heart failure" in lowered or "suy tim" in lowered,
            case_id,
            "HF_HYPOTHESIS_PRESERVED",
        )
        _clinical_assert(
            "PPF_CRITERIA_MET" not in report,
            case_id,
            "ACUTE_EDEMA_NOT_COUNTED_AS_PPF",
        )
    elif case_id == "ILD28":
        _clinical_assert(
            "uip" in lowered and ("bệnh lý" in lowered or "histolog" in lowered),
            case_id,
            "HISTOLOGIC_UIP_PROVENANCE",
        )
        _clinical_assert(
            "ILD_ETIOLOGY_UNRESOLVED" in report
            and "IPF_NOT_ESTABLISHED" in report,
            case_id,
            "HISTOLOGIC_UIP_IS_NOT_AUTOMATIC_IPF",
        )
    elif case_id == "ILD29":
        _clinical_assert(
            "ipf" in lowered or "xơ phổi vô căn" in lowered,
            case_id,
            "TRUSTED_MDD_DIAGNOSIS_PRESERVED",
        )
        _clinical_assert(
            "mdd" in lowered or "đa chuyên khoa" in lowered,
            case_id,
            "MDD_PROVENANCE_PRESERVED",
        )
    elif case_id == "ILD30":
        _clinical_assert("0.91" in report and "0.88" in report, case_id, "MODEL_SCORES_PRESERVED")
        _clinical_assert(
            not re.search(
                r"(91|88)%\s*(xác suất|khả năng|probability|chance).{0,30}"
                r"(ild|ipf|tiến triển|progression)",
                lowered,
            ),
            case_id,
            "MODEL_SCORES_ARE_NOT_DISEASE_OR_PROGRESSION_PROBABILITY",
        )
