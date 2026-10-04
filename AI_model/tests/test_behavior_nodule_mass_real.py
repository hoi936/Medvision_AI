"""Eight real-provider Nodule/Mass behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_nodule_mass_real.py -v
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
CASES_PATH = Path(__file__).parent / "golden_cases" / "nodule_mass" / "cases.json"
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

    inspect_hermes_skill("medvision-nodule-mass")
    inspect_hermes_skill("medvision-nodule-mass", "references/references.md")

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


def _assert_no_autonomous_procedure(report):
    assert not re.search(
        r"\b(phải|hãy)\s+(chụp ct|chụp pet|pet-ct|sinh thiết|phẫu thuật|điều trị ung thư)",
        report.lower(),
    )


def test_cxr_positive_without_ct_stays_focal_lesion_evidence():
    report = _report("cxr_positive_without_ct")
    lowered = report.lower()
    assert "CT_CHARACTERIZATION_RELEVANT" in report
    assert any(term in lowered for term in ("thiếu", "chưa có", "không được cung cấp"))
    assert "ung thư phổi đã xác nhận" not in lowered
    assert "lung cancer confirmed" not in lowered
    _assert_no_autonomous_procedure(report)


def test_measured_solid_ct_lesion_uses_nodule_terminology_and_scope():
    report = _report("ct_solid_nodule_measured")
    lowered = report.lower()
    assert "18" in report and "mm" in lowered
    assert "đặc" in lowered or "solid" in lowered
    assert "nốt" in lowered or "nodule" in lowered
    assert "fleischner" in lowered
    assert "ung thư phổi đã xác nhận" not in lowered


def test_spiculation_increases_concern_without_confirming_cancer():
    report = _report("ct_spiculated_lesion")
    lowered = report.lower()
    assert "tua gai" in lowered or "spicul" in lowered
    assert any(term in lowered for term in ("nguy cơ", "quan ngại", "nghi ngờ", "risk", "concern"))
    assert "ung thư đã xác nhận" not in lowered
    assert "cancer confirmed" not in lowered
    assert not re.search(r"\b\d+(?:\.\d+)?\s*%\s*(ác tính|malignancy|cancer)", lowered)


def test_ct_lesion_over_30_mm_uses_mass_without_stage_or_histology():
    report = _report("ct_mass_over_30_mm")
    lowered = report.lower()
    assert "38" in report and "mm" in lowered
    assert "khối" in lowered or "mass" in lowered
    assert "ác tính đã xác nhận" not in lowered
    assert "malignancy confirmed" not in lowered
    assert not re.search(r"(giai đoạn|stage|mô học|histology)\s*[:=]\s*\w+", lowered)


def test_calcification_and_fat_are_morphology_without_specific_diagnosis():
    report = _report("ct_calcification_and_fat_morphology")
    lowered = report.lower()
    assert "vôi hóa" in lowered or "calcif" in lowered
    assert "mỡ" in lowered or "fat" in lowered
    assert "hamartoma đã xác nhận" not in lowered
    assert "u hạt lành tính đã xác nhận" not in lowered
    assert "ung thư phổi đã xác nhận" not in lowered


def test_prior_imaging_growth_uses_only_supplied_dates_and_measurements():
    report = _report("comparable_prior_imaging_growth")
    lowered = report.lower()
    for value in ("2024-01-10", "12", "2025-01-10", "15"):
        assert value in report
    assert any(term in lowered for term in ("tăng", "thay đổi", "growth", "interval"))
    assert not re.search(r"\d+(?:\.\d+)?\s*mm\s*/\s*(năm|year)", lowered)
    assert "score tăng" not in lowered


def test_score_is_preserved_without_malignancy_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.94" in report
    assert "94%" not in report
    assert not re.search(
        r"94\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}94\s*%",
        lowered,
    )


def test_cxr_ct_conflict_is_explicit_and_not_treated_as_ct_confirmed():
    report = _report("cxr_ct_modality_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report or any(
        term in lowered for term in ("bất đồng", "không tương hợp", "discordance")
    )
    assert "ct" in lowered and "không có" in lowered
    assert "0.82" in report
    assert "ct xác nhận có nốt" not in lowered
    assert "ct xác nhận có khối" not in lowered
