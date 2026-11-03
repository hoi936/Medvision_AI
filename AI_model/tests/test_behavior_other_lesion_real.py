"""Eight real-provider Other lesion behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_other_lesion_real.py -v
"""

import json
import os
from pathlib import Path
import re
import subprocess

import pytest

from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    HERMES_HOME,
    discover_hermes_skills,
    generate_hermes_report,
    hermes_environment,
    hermes_skill_write_approval_enabled,
    inspect_hermes_skill,
    locate_hermes,
)


RUN_REAL = os.environ.get("RUN_HERMES_REAL") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_REAL,
    reason="real Hermes tests disabled; set RUN_HERMES_REAL=1 to use the configured provider",
)
CASES_PATH = (
    Path(__file__).parent / "golden_cases" / "other_lesion" / "cases.json"
)
CASES = {
    case["id"]: case
    for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}


def _runtime_python():
    executable = locate_hermes()
    assert executable is not None
    return executable.parent / ("python.exe" if os.name == "nt" else "python")


def _provider_configuration():
    probe = """
import json
from hermes_cli.config import load_config
from hermes_cli.main import _has_any_provider_configured
cfg = load_config()
model_cfg = cfg.get("model")
if isinstance(model_cfg, dict):
    model = model_cfg.get("default") or model_cfg.get("model") or ""
    provider = model_cfg.get("provider") or ""
else:
    model = model_cfg or ""
    provider = ""
print(json.dumps({"provider_ready": bool(_has_any_provider_configured()), "model": str(model), "provider": str(provider)}))
"""
    completed = subprocess.run(
        [str(_runtime_python()), "-c", probe],
        cwd=Path(__file__).resolve().parents[2],
        env=hermes_environment(),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        shell=False,
    )
    if completed.returncode != 0:
        pytest.fail(f"INFRASTRUCTURE: provider probe failed: {completed.stderr[-1000:]}")
    return json.loads(completed.stdout)


@pytest.fixture(scope="module", autouse=True)
def runtime_smoke_validation():
    executable = locate_hermes()
    if executable is None:
        pytest.fail("INFRASTRUCTURE: isolated Hermes executable is missing")
    if not HERMES_HOME.is_dir():
        pytest.fail(f"INFRASTRUCTURE: HERMES_HOME does not exist: {HERMES_HOME}")

    expected_skills = {*CORE_HERMES_SKILLS, *FINDING_SKILL_MAP.values()}
    if discover_hermes_skills(executable) != expected_skills:
        pytest.fail("INFRASTRUCTURE: all MedVision skills are not discoverable")
    if not hermes_skill_write_approval_enabled(executable):
        pytest.fail("INFRASTRUCTURE: Hermes skills.write_approval is not enabled")

    inspect_hermes_skill("medvision-other-lesion")
    inspect_hermes_skill("medvision-other-lesion", "references/references.md")

    provider = _provider_configuration()
    if not provider["provider_ready"] or not provider["model"]:
        pytest.fail(
            "INFRASTRUCTURE: RUN_HERMES_REAL=1 but no usable provider/model is configured"
        )


def _report(case_id):
    report = generate_hermes_report(**CASES[case_id]["input"])
    assert "review_status: PENDING_CLINICIAN_REVIEW" in report
    assert "requires_doctor_review: true" in report
    return report


def _assert_no_autonomous_order(report):
    assert not re.search(
        r"\b(phải|hãy)\s+(chụp|làm)\s+(ct|mri|pet|sinh thiết|nội soi)|"
        r"\b(phải|hãy)\s+(điều trị|dùng thuốc|phẫu thuật)",
        report.lower(),
    )


def test_isolated_other_lesion_remains_unspecified_with_bbox_preserved():
    report = _report("isolated_other_lesion_with_bbox")
    lowered = report.lower()
    assert "UNSPECIFIED_LOCAL_FINDING" in report
    assert "Other lesion" in report
    assert all(str(value) in report for value in (110, 70, 172, 136))
    assert any(term in lowered for term in ("unknown", "chưa xác định"))
    assert "other diseases" not in lowered
    assert not re.search(
        r"\b(chẩn đoán|confirmed)\b[^\n]{0,60}"
        r"\b(tumor|cancer|nodule|infection|pneumonia)\b",
        lowered,
    )
    _assert_no_autonomous_order(report)


def test_distinct_region_nodule_and_other_lesion_are_not_merged():
    report = _report("other_lesion_and_nodule_distinct_regions")
    lowered = report.lower()
    assert "Other lesion" in report
    assert "Nodule/Mass" in report
    assert any(term in lowered for term in ("khác vùng", "tách biệt", "distinct", "separate"))
    assert "OVERLAPPING_FINDING_EVIDENCE" not in report
    assert not re.search(r"(cùng tổn thương|same lesion)\s*:\s*(true|yes|có)", lowered)


def test_supported_specific_overlap_refines_without_erasing_generic_finding():
    report = _report("other_lesion_with_supported_specific_overlap")
    lowered = report.lower()
    assert "Other lesion" in report
    assert "Calcification" in report
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert any(term in lowered for term in ("hình thái", "morphology", "refine", "cụ thể hơn"))
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "double count", "trùng lặp"))


def test_unknown_lung_opacity_correspondence_does_not_force_overlap_or_etiology():
    report = _report("other_lesion_with_lung_opacity_unknown_correspondence")
    lowered = report.lower()
    assert "Other lesion" in report
    assert "Lung Opacity" in report
    assert any(term in lowered for term in ("unknown", "chưa xác định", "không đủ"))
    assert "OVERLAPPING_FINDING_EVIDENCE" not in report
    assert not re.search(
        r"\b(chẩn đoán|confirmed)\b[^\n]{0,60}"
        r"\b(infection|pneumonia|cancer|tumor)\b",
        lowered,
    )


def test_later_external_characterization_is_refinement_with_separate_provenance():
    report = _report("later_external_characterization_outside_taxonomy")
    lowered = report.lower()
    assert "Other lesion" in report
    assert "ct" in lowered
    assert "x" in lowered
    assert any(term in lowered for term in ("riêng", "separate", "provenance", "nguồn"))
    assert "EVIDENCE_CONFLICT" not in report
    assert not re.search(r"ai[^\n]{0,60}(dự đoán|predicted)[^\n]{0,30}\bx\b", lowered)


def test_multiple_other_lesion_detections_remain_separate_objects():
    report = _report("multiple_other_lesion_detections")
    lowered = report.lower()
    assert report.count("Other lesion") >= 2
    assert all(
        str(value) in report
        for value in (55, 60, 105, 112, 325, 285, 382, 342)
    )
    assert any(term in lowered for term in ("hai", "two", "nhiều", "multiple"))
    assert any(term in lowered for term in ("tách biệt", "separate", "không gộp"))


def test_score_is_preserved_without_patient_level_disease_probability():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.93" in report
    assert not re.search(
        r"93\s*%\s*(xác suất|khả năng|probability|chance)[^\n]{0,60}"
        r"(cancer|tumor|serious disease)|"
        r"(xác suất|probability|chance)[^\n]{0,60}93\s*%",
        lowered,
    )


def test_ai_human_or_ct_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_or_ct_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.8" in report
    assert "ct" in lowered
    assert "không có" in lowered
    assert "other lesion" in lowered
