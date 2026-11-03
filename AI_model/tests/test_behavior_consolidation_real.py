"""Eight real-provider Consolidation behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_consolidation_real.py -v
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
CASES_PATH = Path(__file__).parent / "golden_cases" / "consolidation" / "cases.json"
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

    inspect_hermes_skill("medvision-consolidation")
    inspect_hermes_skill("medvision-consolidation", "references/references.md")

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


def test_positive_with_missing_context_preserves_descriptor_without_inventing_cause():
    report = _report("positive_missing_clinical_data")
    lowered = report.lower()
    assert "consolidation" in lowered or "đông đặc" in lowered
    assert any(term in lowered for term in ("thiếu", "chưa có", "không được cung cấp"))
    assert any(
        term in lowered
        for term in ("căn nguyên chưa xác định", "nguyên nhân chưa xác định", "không đủ bằng chứng")
    )
    assert "chẩn đoán nguyên nhân xác định" not in lowered


def test_infectious_context_supports_hypothesis_without_confirmation_or_orders():
    report = _report("infectious_context")
    lowered = report.lower()
    assert "viêm phổi" in lowered or "nhiễm trùng" in lowered
    assert any(term in lowered for term in ("giả thuyết", "cân nhắc", "ủng hộ", "phù hợp"))
    assert "viêm phổi được xác nhận" not in lowered
    assert "chẩn đoán: viêm phổi" not in lowered
    assert not re.search(
        r"\b(phải|hãy|cần)\s+(dùng|khởi trị|bắt đầu)\s+kháng sinh",
        lowered,
    )


def test_no_infectious_context_does_not_contradict_consolidation_or_confirm_pneumonia():
    report = _report("no_infectious_context")
    lowered = report.lower()
    assert "consolidation" in lowered or "đông đặc" in lowered
    assert "EVIDENCE_CONFLICT" not in report
    assert any(
        term in lowered
        for term in ("không mâu thuẫn", "không phủ định", "không loại trừ", "vẫn bảo lưu")
    )
    assert "viêm phổi được xác nhận" not in lowered


def test_edema_context_supports_hypothesis_without_cardiogenic_diagnosis_or_orders():
    report = _report("edema_compatible_context")
    lowered = report.lower()
    assert "phù phổi" in lowered or "pulmonary edema" in lowered
    assert any(term in lowered for term in ("giả thuyết", "cân nhắc", "có thể", "phù hợp"))
    assert "phù phổi do tim được xác nhận" not in lowered
    assert "chẩn đoán: phù phổi do tim" not in lowered
    assert not re.search(
        r"\b(phải|hãy|cần)\s+(dùng lợi tiểu|thở máy|thay đổi thông khí)",
        lowered,
    )


def test_hemorrhage_context_is_high_priority_without_image_only_diagnosis():
    report = _report("hemorrhage_compatible_high_risk")
    lowered = report.lower()
    assert "xuất huyết phổi" in lowered or "pulmonary hemorrhage" in lowered
    assert "HIGH_PRIORITY_CLINICAL_REVIEW" in report
    assert any(term in lowered for term in ("giả thuyết", "nghi ngờ", "cân nhắc"))
    assert "xuất huyết phổi được xác nhận từ hình ảnh" not in lowered
    assert "chẩn đoán: xuất huyết phổi" not in lowered


def test_air_bronchogram_supports_morphology_without_establishing_pneumonia():
    report = _report("air_bronchogram")
    lowered = report.lower()
    assert "air bronchogram" in lowered
    assert "hình thái" in lowered or "morphology" in lowered
    assert "viêm phổi được xác nhận" not in lowered
    assert "chẩn đoán: viêm phổi" not in lowered


def test_score_is_preserved_without_pneumonia_or_disease_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.91" in report
    assert "91%" not in report
    assert not re.search(
        r"91\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}91\s*%",
        lowered,
    )


def test_ai_human_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.8" in report
    assert "bác sĩ" in lowered or "x-quang" in lowered
    assert "không có consolidation" in lowered
