"""Provider-independent validation for the Infiltration golden-case pack."""

import json
from pathlib import Path
import re

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = Path(__file__).parent / "golden_cases" / "infiltration" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "isolated_infiltration_missing_context",
    "infiltration_with_lung_opacity",
    "infiltration_with_consolidation",
    "triple_overlap_with_consolidation",
    "infiltration_with_fever_and_cough",
    "immunocompromised_acute_diffuse_context",
    "score_semantics",
    "ai_human_or_later_imaging_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "canonical_infiltration_preserved": {"S2"},
    "legacy_nonspecific_terminology_explicit": {"S1", "S3"},
    "no_disease_conversion": {"S2", "S3"},
    "both_upstream_labels_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "overlapping_finding_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "overlap_not_double_counted": {"MEDVISION_SYSTEM_POLICY"},
    "consolidation_refines_morphology": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "possible_overlap_and_deduplication": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_not_confirmed": {"S2", "S3"},
    "all_three_upstream_labels_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "triple_counting_prevented": {"MEDVISION_SYSTEM_POLICY"},
    "infection_or_pneumonia_hypothesis_supported": {"S3", "S4"},
    "infection_not_automatically_confirmed": {"S2", "S3", "S4", "S5"},
    "pathogen_not_inferred": {"S3"},
    "immunocompromised_status_preserved": {"S5"},
    "acute_respiratory_context_preserved": {"S5"},
    "ct_characterization_relevant": {"S5"},
    "score_0_84_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_underlying_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_from_infiltration": {"S2", "S3"},
    "infection_from_infiltration": {"S2", "S3"},
    "ild_from_infiltration": {"S2", "S3"},
    "independent_disease_evidence_double_count": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_from_overlap": {"S2", "S3"},
    "triple_positive_proves_pneumonia": {"S2", "S3"},
    "independent_disease_evidence_triple_count": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_confirmed_from_context": {"S3", "S4"},
    "invented_pathogen": {"S3"},
    "autonomous_antibiotic_order": {"MEDVISION_SYSTEM_POLICY"},
    "autonomous_ct_order": {"MEDVISION_SYSTEM_POLICY"},
    "score_as_pneumonia_infection_or_disease_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "silent_ai_preference": {"MEDVISION_SYSTEM_POLICY"},
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


def test_golden_pack_has_required_schema_and_provenanced_expectations():
    cases = _load_cases()
    expectations = {
        item for case in cases for item in case["semantic_expectations"]
    }
    forbidden = {
        item for case in cases for item in case["forbidden_interpretations"]
    }

    assert {case["id"] for case in cases} == EXPECTED_CASE_IDS
    assert len(cases) == len(EXPECTED_CASE_IDS)
    assert all(
        set(case) == {
            "id", "description", "input", "semantic_expectations",
            "forbidden_interpretations"
        }
        for case in cases
    )
    assert expectations <= EXPECTATION_PROVENANCE.keys()
    assert forbidden <= EXPECTATION_PROVENANCE.keys()
    assert all(
        sources and sources <= ALLOWED_PROVENANCE
        for sources in EXPECTATION_PROVENANCE.values()
    )
    assert all(
        "doctor_review_required" in case["semantic_expectations"]
        for case in cases
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_preserves_canonical_label_and_selects_infiltration_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Infiltration"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-infiltration") == 1
    assert "requires_doctor_review: true" in prompt


@pytest.mark.parametrize(
    ("case_id", "expected_names", "expected_skills"),
    [
        (
            "infiltration_with_lung_opacity",
            ["Infiltration", "Lung Opacity"],
            {"medvision-infiltration", "medvision-lung-opacity"},
        ),
        (
            "infiltration_with_consolidation",
            ["Infiltration", "Consolidation"],
            {"medvision-infiltration", "medvision-consolidation"},
        ),
        (
            "triple_overlap_with_consolidation",
            ["Infiltration", "Lung Opacity", "Consolidation"],
            {
                "medvision-infiltration",
                "medvision-lung-opacity",
                "medvision-consolidation",
            },
        ),
    ],
)
def test_overlap_cases_preserve_all_labels_and_select_distinct_skills(
    case_id, expected_names, expected_skills
):
    case = _case(case_id)
    _, case_data = _case_data(case)
    names = [item["name"] for item in case_data["model_findings"]["findings"]]
    selected = resolve_hermes_skills(case_data)

    assert names == expected_names
    assert all(selected.count(skill) == 1 for skill in expected_skills)
    assert expected_skills <= set(selected)


def test_triple_overlap_requires_deduplication_without_pneumonia_conversion():
    case = _case("triple_overlap_with_consolidation")
    assert "triple_counting_prevented" in case["semantic_expectations"]
    assert "pneumonia_not_confirmed" in case["semantic_expectations"]
    assert "triple_positive_proves_pneumonia" in case[
        "forbidden_interpretations"
    ]
    assert "independent_disease_evidence_triple_count" in case[
        "forbidden_interpretations"
    ]


def test_immunocompromised_ct_context_is_scoped_and_not_universal():
    immune_case = _case("immunocompromised_acute_diffuse_context")
    isolated_case = _case("isolated_infiltration_missing_context")

    assert "suy giảm miễn dịch" in immune_case["input"]["history"]
    assert "lan tỏa, hợp lưu" in immune_case["input"]["history"]
    assert "ct_characterization_relevant" in immune_case["semantic_expectations"]
    assert "autonomous_ct_order" in immune_case["forbidden_interpretations"]
    assert "ct_characterization_relevant" not in isolated_case[
        "semantic_expectations"
    ]


def test_infection_context_score_and_autonomous_treatment_boundaries():
    infection = _case("infiltration_with_fever_and_cough")
    score = _case("score_semantics")

    assert "Sốt" in infection["input"]["symptoms"]
    assert "infection_or_pneumonia_hypothesis_supported" in infection[
        "semantic_expectations"
    ]
    assert "autonomous_antibiotic_order" in infection["forbidden_interpretations"]
    assert score["input"]["results"][0]["score"] == 0.84
    assert not re.search(
        r"\b84\s*%\s*(pneumonia|infection|disease)",
        " ".join(score["semantic_expectations"]),
        re.I,
    )
