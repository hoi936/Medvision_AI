"""Eight real-provider Calcification behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_calcification_real.py -v
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
    Path(__file__).parent / "golden_cases" / "calcification" / "cases.json"
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

    inspect_hermes_skill("medvision-calcification")
    inspect_hermes_skill("medvision-calcification", "references/references.md")

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
        r"\b(phải|hãy)\s+(chụp|làm)\s+(ct|sinh thiết|nội soi)|"
        r"\b(phải|hãy)\s+(điều trị|dùng thuốc|xét nghiệm chuyển hóa)",
        report.lower(),
    )


def test_bbox_is_preserved_without_claiming_anatomical_compartment():
    report = _report("isolated_calcification_with_bbox")
    lowered = report.lower()
    assert "calcification" in lowered or "vôi hóa" in lowered
    assert all(str(value) in report for value in (120, 85, 168, 133))
    assert any(term in lowered for term in ("unknown", "chưa xác định"))
    assert not re.search(
        r"compartment:\s*(pulmonary|pleural|nodal|cardiac|vascular)",
        lowered,
    )
    assert not re.search(
        r"\b(chẩn đoán|confirmed)\b[^\n]{0,60}"
        r"\b(nodule|plaque|lymph node|aortic|coronary|valvular)\b",
        lowered,
    )
    _assert_no_autonomous_order(report)


def test_nodule_coexistence_without_colocalization_does_not_create_calcified_nodule():
    report = _report("calcification_with_nodule_mass_without_colocalization")
    lowered = report.lower()
    assert "Calcification" in report
    assert "Nodule/Mass" in report
    assert any(term in lowered for term in ("không xác định", "unknown", "chưa được xác nhận"))
    assert "calcified pulmonary nodule confirmed" not in lowered
    assert "nốt phổi vôi hóa đã xác nhận" not in lowered
    assert "malignancy excluded" not in lowered
    assert "loại trừ ác tính" not in lowered


def test_ct_intranodular_calcification_preserves_location_and_pattern_without_benignity():
    report = _report("ct_confirmed_intranodular_calcification")
    lowered = report.lower()
    assert "ct" in lowered
    assert any(term in lowered for term in ("trong nốt", "intranodular"))
    assert any(term in lowered for term in ("trung tâm", "central"))
    assert "OVERLAPPING_FINDING_EVIDENCE" in report
    assert "benign confirmed" not in lowered
    assert "lành tính đã xác nhận" not in lowered
    assert "malignancy excluded" not in lowered


def test_pleural_coexistence_without_localization_does_not_create_plaque_or_exposure():
    report = _report("calcification_with_pleural_thickening_unknown_localization")
    lowered = report.lower()
    assert "Calcification" in report
    assert "Pleural thickening" in report
    assert not re.search(r"pleural plaque:\s*(present|confirmed|có)", lowered)
    assert "phơi nhiễm asbestos đã xác nhận" not in lowered
    assert "confirmed asbestos exposure" not in lowered


def test_ct_calcified_pleural_plaque_preserves_morphology_without_asbestosis():
    report = _report("ct_confirmed_calcified_pleural_plaque")
    lowered = report.lower()
    assert "ct" in lowered
    assert "pleural plaque" in lowered
    assert any(term in lowered for term in ("calcified", "vôi hóa"))
    assert "phơi nhiễm asbestos đã xác nhận" not in lowered
    assert "asbestosis đã xác nhận" not in lowered
    assert "asbestosis confirmed" not in lowered


def test_calcified_nodes_preserve_prior_context_without_active_tb_diagnosis():
    report = _report("calcified_nodes_with_prior_granulomatous_context")
    lowered = report.lower()
    assert any(term in lowered for term in ("hạch rốn phổi", "hilar"))
    assert any(term in lowered for term in ("hạch trung thất", "mediastinal"))
    assert any(term in lowered for term in ("đã lành", "healed", "prior"))
    assert "active tb confirmed" not in lowered
    assert "lao hoạt động đã xác nhận" not in lowered
    assert any(term in lowered for term in ("không duy nhất", "not the only", "không thể kết luận"))


def test_score_is_preserved_without_disease_or_benignity_probability():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.9" in report
    assert not re.search(
        r"90\s*%\s*(xác suất|khả năng|probability|chance)[^\n]{0,60}"
        r"(benign|tb|malignancy|granuloma|asbestos)|"
        r"(xác suất|probability|chance)[^\n]{0,60}90\s*%",
        lowered,
    )


def test_cxr_ai_ct_conflict_is_explicit_and_preserves_both_sources():
    report = _report("cxr_ai_ct_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.8" in report
    assert "ct" in lowered
    assert "không có" in lowered
    assert "calcification" in lowered or "vôi hóa" in lowered
    assert any(term in lowered for term in ("cụ thể hơn", "more specific", "localization"))
