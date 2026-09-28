"""Provider-independent validation for No finding policy golden cases."""

import json
from pathlib import Path

import pytest

from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    NO_FINDING_CANONICAL_NAME,
    NO_FINDING_CONTRADICTION,
    NO_FINDING_WITHIN_14_CLASS_TAXONOMY,
    build_report_prompt,
    derive_no_finding_policy,
    resolve_hermes_skills,
)


CASES_PATH = Path(__file__).parent / "golden_cases" / "no_finding" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "no_finding_only",
    "no_finding_with_pneumothorax",
    "no_finding_with_multiple_findings",
    "no_finding_negative_all_targets_negative",
    "no_finding_negative_with_nodule_mass",
    "no_finding_with_severe_clinical_state",
    "no_finding_score_semantics",
    "no_finding_ai_vs_human_ct_abnormality",
}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "MEDVISION_SYSTEM_POLICY"}
EXPECTATION_PROVENANCE = {
    "no_finding_within_14_class_taxonomy": {"S1", "S2", "MEDVISION_SYSTEM_POLICY"},
    "core_chain_only": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "no_finding_contradiction": {"S1", "S2", "MEDVISION_SYSTEM_POLICY"},
    "positive_findings_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "pneumothorax_skill_once": {"MEDVISION_SYSTEM_POLICY"},
    "single_structured_contradiction": {"MEDVISION_SYSTEM_POLICY"},
    "all_positive_findings_listed": {"MEDVISION_SYSTEM_POLICY"},
    "no_finding_not_established": {"MEDVISION_SYSTEM_POLICY"},
    "positive_finding_routed": {"MEDVISION_SYSTEM_POLICY"},
    "no_no_finding_contradiction": {"MEDVISION_SYSTEM_POLICY"},
    "clinical_safety_evidence_active": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "high_priority_clinical_review": {"MEDVISION_SYSTEM_POLICY"},
    "score_0_96_preserved": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "score_not_health_probability": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "healthy_or_no_disease": {"S2", "S3"},
    "universal_normality": {"S2", "S3"},
    "new_no_finding_skill": {"MEDVISION_SYSTEM_POLICY"},
    "positive_finding_suppressed": {"MEDVISION_SYSTEM_POLICY"},
    "automatic_ai_winner": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "duplicate_conflict_objects": {"MEDVISION_SYSTEM_POLICY"},
    "synthetic_normality": {"MEDVISION_SYSTEM_POLICY"},
    "synthetic_abnormality": {"MEDVISION_SYSTEM_POLICY"},
    "synthetic_abnormality_from_no_finding_negative": {"MEDVISION_SYSTEM_POLICY"},
    "patient_safe_from_no_finding": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "symptoms_as_direct_image_contradiction": {"MEDVISION_SYSTEM_POLICY"},
    "autonomous_treatment_order": {"MEDVISION_SYSTEM_POLICY"},
    "ninety_six_percent_healthy_or_no_disease": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "silent_ai_preference": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "human_ct_evidence_erased": {"S3", "MEDVISION_SYSTEM_POLICY"},
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def _case_data(case):
    prompt = build_report_prompt(**case["input"])
    return prompt, json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )


def test_golden_pack_has_eight_cases_and_only_provenanced_expectations():
    cases = _load_cases()
    labels = {
        item
        for case in cases
        for key in ("semantic_expectations", "forbidden_interpretations")
        for item in case[key]
    }

    assert len(cases) == 8
    assert {case["id"] for case in cases} == EXPECTED_CASE_IDS
    assert all(
        set(case) == {
            "id", "description", "input", "semantic_expectations",
            "forbidden_interpretations"
        }
        for case in cases
    )
    assert labels <= EXPECTATION_PROVENANCE.keys()
    assert all(
        sources and sources <= ALLOWED_PROVENANCE
        for sources in EXPECTATION_PROVENANCE.values()
    )
    assert all(
        "doctor_review_required" in case["semantic_expectations"]
        for case in cases
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_uses_exact_canonical_label_without_a_fifteenth_skill(case):
    canonical_target_names = set(
        json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))
    )
    prompt, case_data = _case_data(case)
    names = [item["name"] for item in case_data["model_findings"]["findings"]]

    assert NO_FINDING_CANONICAL_NAME == "No finding"
    assert names[0] == NO_FINDING_CANONICAL_NAME
    assert set(names[1:]) <= canonical_target_names
    assert set(FINDING_SKILL_MAP) == canonical_target_names
    assert NO_FINDING_CANONICAL_NAME not in FINDING_SKILL_MAP
    assert "medvision-no-finding" not in resolve_hermes_skills(case_data)
    assert "requires_doctor_review: true" in prompt


def test_no_finding_only_is_bounded_and_uses_core_chain():
    _, case_data = _case_data(_case("no_finding_only"))
    policy = case_data["no_finding_policy"]

    assert resolve_hermes_skills(case_data) == list(CORE_HERMES_SKILLS)
    assert policy["policy_state"] == NO_FINDING_WITHIN_14_CLASS_TAXONOMY
    assert policy["assessment"]["disease_exclusion_supported"] is False
    assert policy["no_finding"]["model_scores"] == [0.95]


def test_single_positive_target_is_preserved_and_structurally_conflicted():
    _, case_data = _case_data(_case("no_finding_with_pneumothorax"))
    skills = resolve_hermes_skills(case_data)
    conflict = case_data["no_finding_policy"]["no_finding_conflict"]

    assert skills.count("medvision-pneumothorax") == 1
    assert conflict["present"] is True
    assert conflict["parent_type"] == "EVIDENCE_CONFLICT"
    assert conflict["type"] == NO_FINDING_CONTRADICTION
    assert conflict["conflicting_positive_findings"] == ["Pneumothorax"]


def test_multiple_positive_targets_share_one_conflict_without_suppression():
    _, case_data = _case_data(_case("no_finding_with_multiple_findings"))
    skills = resolve_hermes_skills(case_data)
    conflict = case_data["no_finding_policy"]["no_finding_conflict"]

    assert skills.count("medvision-cardiomegaly") == 1
    assert skills.count("medvision-pleural-effusion") == 1
    assert conflict["conflicting_positive_findings"] == [
        "Cardiomegaly", "Pleural effusion"
    ]


def test_negative_no_finding_neither_implies_abnormality_nor_blocks_a_positive():
    _, all_negative = _case_data(
        _case("no_finding_negative_all_targets_negative")
    )
    _, with_positive = _case_data(
        _case("no_finding_negative_with_nodule_mass")
    )

    assert all_negative["no_finding_policy"]["policy_state"] == (
        "NO_FINDING_NOT_ESTABLISHED"
    )
    assert resolve_hermes_skills(all_negative) == list(CORE_HERMES_SKILLS)
    assert with_positive["no_finding_policy"]["policy_state"] == (
        "POSITIVE_FINDING_WITH_NO_FINDING_NEGATIVE"
    )
    assert with_positive["no_finding_policy"]["no_finding_conflict"][
        "present"
    ] is False
    assert "medvision-nodule-mass" in resolve_hermes_skills(with_positive)


def test_missing_no_finding_stays_missing_and_does_not_synthesize_normality():
    results = [
        {"finding": name, "score": 0.1, "threshold": 0.5}
        for name in FINDING_SKILL_MAP
    ]
    prompt = build_report_prompt(results=results)
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    policy = case_data["no_finding_policy"]

    assert policy["policy_state"] == "NO_FINDING_MISSING"
    assert policy["no_finding"]["decision"] == "MISSING"
    assert policy["no_finding"]["present_in_payload"] is False
    assert policy["assessment"]["no_target_finding_within_taxonomy"] == "unknown"


def test_clinical_severity_reaches_safety_without_becoming_image_conflict():
    prompt, case_data = _case_data(
        _case("no_finding_with_severe_clinical_state")
    )

    assert "SpO2 giảm nhanh" in prompt
    assert case_data["no_finding_policy"]["no_finding_conflict"]["present"] is False
    assert "medvision-safety-check" in resolve_hermes_skills(case_data)
    assert "high_priority_clinical_review" in _case(
        "no_finding_with_severe_clinical_state"
    )["semantic_expectations"]


def test_score_is_preserved_without_health_probability_semantics():
    case = _case("no_finding_score_semantics")
    _, case_data = _case_data(case)

    assert case_data["no_finding_policy"]["no_finding"]["model_scores"] == [0.96]
    assert "score_not_health_probability" in case["semantic_expectations"]
    assert "ninety_six_percent_healthy_or_no_disease" in case[
        "forbidden_interpretations"
    ]


def test_human_ct_disagreement_is_preserved_for_llm_evidence_conflict():
    case = _case("no_finding_ai_vs_human_ct_abnormality")
    prompt, case_data = _case_data(case)

    assert "CT gần đây" in prompt
    assert case_data["no_finding_policy"]["no_finding_conflict"]["present"] is False
    assert "evidence_conflict" in case["semantic_expectations"]
    assert "ai_not_silently_preferred" in case["semantic_expectations"]


def test_other_lesion_participates_in_no_finding_contradiction_normally():
    payload = {
        "model_findings": {
            "findings": [
                {"name": "No finding", "decision": "POSITIVE", "score": 0.9},
                {"name": "Other lesion", "decision": "POSITIVE", "score": 0.8},
            ]
        }
    }
    policy = derive_no_finding_policy(payload)

    assert policy["policy_state"] == NO_FINDING_CONTRADICTION
    assert policy["no_finding_conflict"]["conflicting_positive_findings"] == [
        "Other lesion"
    ]
    assert resolve_hermes_skills(payload).count("medvision-other-lesion") == 1
