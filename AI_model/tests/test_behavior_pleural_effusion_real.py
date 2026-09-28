"""Eight real-provider Pleural Effusion behavior tests.

Run explicitly with:
RUN_HERMES_REAL=1 PYTHONPATH=. .venv/bin/pytest tests/test_behavior_pleural_effusion_real.py -v
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
    Path(__file__).parent / "golden_cases" / "pleural_effusion" / "cases.json"
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

    inspect_hermes_skill("medvision-pleural-effusion")
    inspect_hermes_skill(
        "medvision-pleural-effusion", "references/references.md"
    )

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


def test_positive_with_missing_clinical_data_keeps_etiology_undetermined():
    report = _report("positive_missing_clinical_data")
    lowered = report.lower()
    assert any(term in lowered for term in ("thiếu", "chưa có", "không được cung cấp"))
    assert any(
        term in lowered
        for term in ("căn nguyên chưa xác định", "nguyên nhân chưa xác định", "không đủ bằng chứng")
    )
    assert "chẩn đoán xác định" not in lowered
    assert not re.search(
        r"(nguyên nhân|căn nguyên)\s+(là|do)\s+(suy tim|nhiễm trùng|ác tính|lao)",
        lowered,
    )


def test_heart_failure_context_and_nt_probnp_support_only_a_hypothesis():
    report = _report("heart_failure_supported_hypothesis")
    lowered = report.lower()
    assert "nt-probnp" in lowered
    assert "suy tim" in lowered
    assert any(term in lowered for term in ("ủng hộ", "hỗ trợ", "phù hợp"))
    assert re.search(
        r"(không|chưa).{0,100}(đơn độc|một mình|riêng lẻ|xác nhận|khẳng định)",
        lowered,
        re.DOTALL,
    )


def test_complete_light_data_is_exudative_without_final_etiology():
    report = _report("complete_light_exudative")
    lowered = report.lower()
    assert "EXUDATIVE_BY_LIGHT_CRITERIA" in report
    assert "light" in lowered
    assert re.search(
        r"(không|chưa).{0,120}(căn nguyên|nguyên nhân|chẩn đoán cuối cùng)",
        lowered,
        re.DOTALL,
    )


def test_incomplete_light_data_is_not_evaluable_and_reports_pairs_missing():
    report = _report("incomplete_light_data")
    lowered = report.lower()
    assert "EXUDATIVE_BY_LIGHT_CRITERIA" not in report
    assert "TRANSUDATIVE_BY_LIGHT_CRITERIA" not in report
    assert any(term in lowered for term in ("không thể đánh giá", "chưa thể đánh giá", "không đủ"))
    assert "serum protein" in lowered or "protein huyết thanh" in lowered
    assert "serum ldh" in lowered or "ldh huyết thanh" in lowered


def test_suspected_pleural_infection_high_risk_requires_review_without_orders():
    report = _report("pleural_infection_high_risk")
    lowered = report.lower()
    assert "PLEURAL_INFECTION_HIGH_RISK" in report
    assert "HIGH_PRIORITY_CLINICAL_REVIEW" in report
    assert not re.search(
        r"\b(phải|hãy|cần)\s+(chọc hút|dẫn lưu|đặt dẫn lưu|dùng kháng sinh|khởi trị kháng sinh)",
        lowered,
    )


def test_negative_cytology_does_not_definitively_exclude_malignancy():
    report = _report("malignancy_negative_cytology")
    lowered = report.lower()
    assert "cytology" in lowered or "tế bào học" in lowered
    assert "ác tính" in lowered
    assert any(
        term in lowered
        for term in ("không loại trừ", "chưa loại trừ", "không thể loại trừ")
    )


def test_score_is_preserved_without_probability_or_chance_language():
    report = _report("score_semantics")
    lowered = report.lower()
    assert "0.87" in report
    assert "87%" not in report
    assert not re.search(
        r"87\s*%\s*(xác suất|khả năng|probability|chance)|"
        r"(xác suất|probability|chance)[^\n]{0,50}87\s*%",
        lowered,
    )


def test_ai_human_conflict_is_explicit_and_preserves_both_sources():
    report = _report("ai_human_conflict")
    lowered = report.lower()
    assert "EVIDENCE_CONFLICT" in report
    assert "0.81" in report
    assert "bác sĩ" in lowered or "x-quang" in lowered
    assert "không có tràn dịch màng phổi" in lowered
