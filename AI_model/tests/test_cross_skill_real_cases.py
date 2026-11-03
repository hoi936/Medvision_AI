"""Provider-independent structure checks for cross-skill real golden inputs."""

import json
from pathlib import Path

import pytest

from hermes_report import (
    FINDING_SKILL_MAP,
    build_report_prompt_with_payload,
    resolve_hermes_skills,
)


CASES_PATH = (
    Path(__file__).parent / "golden_cases" / "cross_skill_real" / "cases.json"
)
ALLOWED_CATEGORIES = {
    "PROVENANCE_PRESERVED",
    "MISSING_STAYS_UNKNOWN",
    "NO_SCORE_TO_DISEASE_PROBABILITY",
    "NO_UNSUPPORTED_ETIOLOGY",
    "NO_UNSUPPORTED_DIAGNOSIS",
    "OVERLAP_NOT_DOUBLE_COUNTED",
    "CONFLICT_PRESERVED",
    "SAFETY_ESCALATION_WHEN_SUPPORTED",
    "NO_AUTONOMOUS_TREATMENT_OR_PROCEDURE",
    "DOCTOR_REVIEW_REQUIRED",
}


def _cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def test_cross_skill_pack_contains_exactly_c01_through_c12():
    cases = _cases()
    assert [case["id"] for case in cases] == [f"C{index:02d}" for index in range(1, 13)]
    assert all(set(case) == {"id", "description", "input", "assertion_categories"} for case in cases)
    assert all(set(case["assertion_categories"]) <= ALLOWED_CATEGORIES for case in cases)
    assert all("DOCTOR_REVIEW_REQUIRED" in case["assertion_categories"] for case in cases)


@pytest.mark.parametrize("case", _cases(), ids=lambda case: case["id"])
def test_cross_skill_input_routes_each_positive_target_once(case):
    _, case_data = build_report_prompt_with_payload(**case["input"])
    skills = resolve_hermes_skills(case_data)
    target_names = [
        item["finding"]
        for item in case["input"]["results"]
        if item["finding"] in FINDING_SKILL_MAP
    ]
    expected = []
    for name in target_names:
        skill = FINDING_SKILL_MAP[name]
        if skill not in expected:
            expected.append(skill)

    assert skills[0] == "medvision-evidence-fusion"
    assert skills[1:-2] == expected
    assert all(skills.count(skill) == 1 for skill in expected)
    assert skills[-2:] == ["medvision-safety-check", "medvision-disease-analysis"]
    assert "medvision-no-finding" not in skills


def test_c12_has_one_ordered_conflict_for_all_fourteen_target_findings():
    case = next(case for case in _cases() if case["id"] == "C12")
    _, case_data = build_report_prompt_with_payload(**case["input"])
    conflict = case_data["no_finding_policy"]["no_finding_conflict"]
    expected_names = [item["finding"] for item in case["input"]["results"]][1:]

    assert len(expected_names) == 14
    assert set(expected_names) == set(FINDING_SKILL_MAP)
    assert conflict["present"] is True
    assert conflict["parent_type"] == "EVIDENCE_CONFLICT"
    assert conflict["type"] == "NO_FINDING_CONTRADICTION"
    assert conflict["conflicting_positive_findings"] == expected_names
