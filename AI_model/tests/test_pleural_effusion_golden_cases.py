"""Provider-independent validation for the Pleural Effusion golden-case pack."""

import json
from pathlib import Path

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = (
    Path(__file__).parent / "golden_cases" / "pleural_effusion" / "cases.json"
)
EXPECTED_CASE_IDS = {
    "positive_missing_clinical_data",
    "heart_failure_supported_hypothesis",
    "complete_light_exudative",
    "incomplete_light_data",
    "pleural_infection_high_risk",
    "malignancy_negative_cytology",
    "score_semantics",
    "ai_human_conflict",
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def test_golden_pack_has_all_required_cases_and_semantic_expectations():
    cases = _load_cases()
    assert {case["id"] for case in cases} == EXPECTED_CASE_IDS
    assert len(cases) == len(EXPECTED_CASE_IDS)
    assert all(case["semantic_expectations"] for case in cases)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_golden_case_selects_effusion_skill_and_preserves_input(case):
    prompt = build_report_prompt(**case["input"])
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    selected = resolve_hermes_skills(case_data)

    assert selected.count("medvision-pleural-effusion") == 1
    assert case_data["model_findings"]["findings"][0]["name"] == "Pleural effusion"
    assert "requires_doctor_review: true" in prompt


def test_score_golden_case_keeps_uncalibrated_score_as_numeric_evidence():
    case = next(case for case in _load_cases() if case["id"] == "score_semantics")
    prompt = build_report_prompt(**case["input"])
    assert '"score": 0.87' in prompt
    assert "Model score chưa calibration và không phải xác suất mắc bệnh." in prompt
