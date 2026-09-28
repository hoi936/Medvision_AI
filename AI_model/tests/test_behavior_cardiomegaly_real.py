"""Eight real-provider Cardiomegaly behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_cardiomegaly_real.py -v
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
CASES_PATH = Path(__file__).parent / "golden_cases" / "cardiomegaly" / "cases.json"
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

    inspect_hermes_skill("medvision-cardiomegaly")
    inspect_hermes_skill("medvision-cardiomegaly", "references/references.md")

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


def test_positive_with_missing_projection_preserves_finding_without_hf_or_ef_inference():
    report = _report("positive_missing_projection_and_context")
    lowered = report.lower()
    assert "cardiomegaly" in lowered or "tim to" in lowered
    assert any(term in lowered for term in ("projection", "tư thế"))
    assert any(term in lowered for term in ("thiếu", "chưa có", "không được cung cấp"))
    assert "chẩn đoán: suy tim" not in lowered
    assert "phân suất tống máu giảm" not in lowered


def test_pa_ctr_above_0_50_supports_radiographic_enlargement_only():
    report = _report("pa_ctr_above_0_50")
    lowered = report.lower()
    assert "pa" in lowered
    assert "0.54" in report
    assert (
        "classic_pa_interpretation_evaluable" in report
        or any(term in lowered for term in ("có thể đánh giá ctr", "đủ điều kiện đánh giá ctr"))
    )
    assert (
        "RADIOGRAPHIC_CARDIAC_ENLARGEMENT_SUPPORTED" in report
        or "ủng hộ tim to trên x-quang" in lowered
        or "ủng hộ bóng tim lớn" in lowered
    )
    assert "phì đại buồng tim được xác nhận" not in lowered
    assert "chẩn đoán: suy tim" not in lowered
    assert "phân suất tống máu giảm" not in lowered


def test_ap_portable_case_has_projection_limitation_without_pa_rule_reuse():
    report = _report("ap_portable_apparent_cardiomegaly")
    lowered = report.lower()
    assert "PROJECTION_LIMITATION" in report
    assert "ap" in lowered and "portable" in lowered
    assert any(term in lowered for term in ("không áp dụng", "không thể áp dụng", "không dùng"))
    assert "không chắc chắn" in lowered or "bất định" in lowered or "uncertainty" in lowered


def test_heart_failure_context_supports_hypothesis_without_confirmation_or_orders():
    report = _report("heart_failure_compatible_context")
    lowered = report.lower()
    assert "bnp" in lowered
    assert "suy tim" in lowered
    assert any(term in lowered for term in ("giả thuyết", "ủng hộ", "hỗ trợ", "phù hợp"))
    assert "suy tim được xác nhận" not in lowered
    assert "chẩn đoán: suy tim" not in lowered
    assert not re.search(
        r"\b(phải|hãy|cần)\s+(dùng lợi tiểu|khởi trị|điều trị suy tim|thở máy)",
        lowered,
    )


def test_normal_ef_does_not_create_reduced_ef_or_invalidate_radiographic_finding():
    report = _report("normal_ef_no_lv_dysfunction")
    lowered = report.lower()
    assert "60%" in report
    assert "tte" in lowered or "siêu âm tim" in lowered
    assert "phân suất tống máu giảm" not in lowered
    assert "rối loạn chức năng tâm thu thất trái" in lowered
    assert "EVIDENCE_CONFLICT" not in report
    assert any(
        term in lowered
        for term in ("không phủ định", "không loại trừ", "khác biệt phương thức", "khác modality")
    )


def test_known_pericardial_effusion_may_affect_silhouette_without_cxr_only_diagnosis():
    report = _report("known_pericardial_effusion")
    lowered = report.lower()
    assert "tràn dịch màng ngoài tim" in lowered
    assert any(term in lowered for term in ("có thể góp phần", "có thể đóng góp", "có thể làm"))
    assert "phì đại buồng tim được xác nhận" not in lowered
    assert "x-quang chẩn đoán tràn dịch màng ngoài tim" not in lowered
    assert "cardiomegaly xác nhận tràn dịch màng ngoài tim" not in lowered


def test_score_is_preserved_without_heart_failure_or_disease_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.93" in report
    assert "93%" not in report
    assert not re.search(
        r"93\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}93\s*%",
        lowered,
    )


def test_ai_human_cxr_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_cxr_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.8" in report
    assert "bác sĩ" in lowered or "x-quang" in lowered
    assert "không có tim to" in lowered
