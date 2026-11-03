"""Eight real-provider Lung Opacity behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_lung_opacity_real.py -v
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
CASES_PATH = Path(__file__).parent / "golden_cases" / "lung_opacity" / "cases.json"
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

    inspect_hermes_skill("medvision-lung-opacity")
    inspect_hermes_skill("medvision-lung-opacity", "references/references.md")

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
        r"\b(phải|hãy)\s+(chụp ct|dùng kháng sinh|dùng lợi tiểu|dùng steroid|điều trị)",
        report.lower(),
    )


def test_isolated_opacity_remains_nonspecific_with_missing_distribution():
    report = _report("isolated_opacity_missing_context")
    lowered = report.lower()
    assert "lung opacity" in lowered or "đám mờ" in lowered or "mờ phổi" in lowered
    assert any(term in lowered for term in ("thiếu", "chưa có", "không được cung cấp"))
    assert "chẩn đoán viêm phổi" not in lowered
    assert "chẩn đoán ung thư" not in lowered
    assert "chẩn đoán phù phổi" not in lowered
    assert "chẩn đoán ild" not in lowered


def test_opacity_and_consolidation_are_preserved_and_deduplicated():
    report = _report("opacity_with_consolidation")
    lowered = report.lower()
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert "lung opacity" in lowered or "đám mờ" in lowered
    assert "consolidation" in lowered or "đông đặc" in lowered
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "double count"))
    assert "chẩn đoán viêm phổi" not in lowered


def test_opacity_and_atelectasis_are_preserved_without_pneumonia_or_obstruction():
    report = _report("opacity_with_atelectasis")
    lowered = report.lower()
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert "lung opacity" in lowered or "đám mờ" in lowered
    assert "atelectasis" in lowered or "xẹp phổi" in lowered
    assert "chẩn đoán viêm phổi" not in lowered
    assert "tắc nghẽn được xác nhận" not in lowered


def test_opacity_and_nodule_mass_do_not_duplicate_malignancy_evidence():
    report = _report("opacity_with_nodule_mass")
    lowered = report.lower()
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert "nodule/mass" in lowered or "nốt" in lowered or "khối" in lowered
    assert any(term in lowered for term in ("cụ thể hơn", "more specific", "focal"))
    assert "chẩn đoán ung thư" not in lowered
    assert any(term in lowered for term in ("không đếm", "tránh đếm", "trùng lặp", "double count"))


def test_diffuse_opacity_with_symptoms_stays_undetermined_without_compromise():
    report = _report("diffuse_opacity_with_respiratory_symptoms")
    lowered = report.lower()
    assert "lan tỏa" in lowered or "diffuse" in lowered
    assert "ho" in lowered and "khó thở" in lowered
    assert "chẩn đoán viêm phổi" not in lowered
    assert "chẩn đoán ild" not in lowered
    assert "HIGH_PRIORITY_CLINICAL_REVIEW" not in report
    _assert_no_autonomous_order(report)


def test_ct_ground_glass_is_preserved_separately_from_cxr_opacity():
    report = _report("cxr_opacity_with_ct_ground_glass")
    lowered = report.lower()
    assert "lung opacity" in lowered or "đám mờ" in lowered
    assert re.search(r"ct[^\n]{0,120}(kính mờ|ground.glass)", lowered)
    assert not re.search(r"x.quang[^\n]{0,80}(cho thấy|thể hiện)[^\n]{0,40}(kính mờ|ground.glass)", lowered)
    assert "chẩn đoán viêm phổi" not in lowered


def test_score_is_preserved_without_underlying_disease_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.89" in report
    assert "89%" not in report
    assert not re.search(
        r"89\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}89\s*%",
        lowered,
    )


def test_ai_ct_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_or_ct_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.8" in report
    assert "ct" in lowered and "không có" in lowered
    assert "lung opacity" in lowered or "đám mờ" in lowered or "mờ phổi" in lowered
