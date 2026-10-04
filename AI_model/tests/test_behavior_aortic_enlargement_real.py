"""Eight real-provider Aortic enlargement behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_aortic_enlargement_real.py -v
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
    Path(__file__).parent / "golden_cases" / "aortic_enlargement" / "cases.json"
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

    inspect_hermes_skill("medvision-aortic-enlargement")
    inspect_hermes_skill("medvision-aortic-enlargement", "references/references.md")

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


def _assert_no_autonomous_aortic_order(report):
    assert not re.search(
        r"\b(phải|hãy)\s+(dùng thuốc|khởi trị|phẫu thuật|can thiệp nội mạch|đặt stent)",
        report.lower(),
    )


def test_positive_missing_direct_imaging_preserves_finding_without_diagnosis():
    report = _report("positive_missing_direct_imaging")
    lowered = report.lower()
    assert "aortic enlargement" in lowered or "động mạch chủ" in lowered
    assert any(term in lowered for term in ("thiếu", "chưa có", "không được cung cấp"))
    assert not re.search(r"(phình|aneurysm|dissection|bóc tách)[^\n]{0,25}(đã xác nhận|confirmed)", lowered)


def test_ct_measurement_is_preserved_as_stronger_direct_evidence():
    report = _report("cxr_with_ct_measured_dilatation")
    lowered = report.lower()
    assert "cta" in lowered and "43" in report
    assert "động mạch chủ lên" in lowered or "ascending" in lowered
    assert any(term in lowered for term in ("trực tiếp", "mạnh hơn", "ưu tiên", "direct"))
    assert "tốc độ tăng trưởng" in lowered or "growth" in lowered
    assert not re.search(r"(tốc độ tăng|growth rate)\s*[:=]\s*\d", lowered)


def test_high_risk_symptoms_raise_aas_concern_without_confirming_dissection():
    report = _report("high_risk_aas_symptoms")
    lowered = report.lower()
    assert "ACUTE_AORTIC_SYNDROME_CONCERN" in report
    assert "HIGH_PRIORITY_CLINICAL_REVIEW" in report
    assert "bóc tách động mạch chủ đã xác nhận" not in lowered
    assert "aortic dissection confirmed" not in lowered
    _assert_no_autonomous_aortic_order(report)


def test_nonspecific_radiography_does_not_exclude_aas():
    report = _report("nonspecific_cxr_with_high_risk_aas_context")
    lowered = report.lower()
    assert "ACUTE_AORTIC_SYNDROME_CONCERN" in report
    assert "HIGH_PRIORITY_CLINICAL_REVIEW" in report
    assert any(term in lowered for term in ("không loại trừ", "không thể loại trừ", "does not exclude"))
    _assert_no_autonomous_aortic_order(report)


def test_hypertension_is_context_without_cxr_diagnosis_or_universal_cutoff():
    report = _report("longstanding_hypertension_context")
    lowered = report.lower()
    assert "tăng huyết áp" in lowered
    assert any(term in lowered for term in ("bối cảnh", "liên quan", "tương hợp", "remodel"))
    assert "chẩn đoán tăng huyết áp từ x-quang" not in lowered
    assert not re.search(r"(quai|arch)[^\n]{0,50}(ngưỡng|cutoff)\s*\d", lowered)


def test_direct_imaging_discordance_preserves_both_modalities():
    report = _report("cxr_direct_imaging_discordance")
    lowered = report.lower()
    assert "cta" in lowered
    assert "giới hạn bình thường" in lowered or "normal" in lowered
    assert any(term in lowered for term in ("khác biệt", "bất đồng", "discordance", "không tương hợp"))
    assert "aortic enlargement" in lowered or "động mạch chủ" in lowered


def test_score_is_preserved_without_aortic_disease_probability_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.88" in report
    assert "88%" not in report
    assert not re.search(
        r"88\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}88\s*%",
        lowered,
    )


def test_ai_human_cxr_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_cxr_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.8" in report
    assert "bác sĩ" in lowered or "x-quang" in lowered
    assert "không to" in lowered
