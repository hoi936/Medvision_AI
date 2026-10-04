"""Provider-independent validation for the Lung Opacity golden-case pack."""

import json
from pathlib import Path
import re

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = Path(__file__).parent / "golden_cases" / "lung_opacity" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "isolated_opacity_missing_context",
    "opacity_with_consolidation",
    "opacity_with_atelectasis",
    "opacity_with_nodule_mass",
    "diffuse_opacity_with_respiratory_symptoms",
    "cxr_opacity_with_ct_ground_glass",
    "score_semantics",
    "ai_human_or_ct_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "nonspecific_radiographic_descriptor_preserved": {"S1", "S2"},
    "localization_and_distribution_missing_explicit": {"S1"},
    "no_disease_conversion": {"S1", "S2"},
    "both_upstream_findings_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "overlapping_finding_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "consolidation_refines_pattern_characterization": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "overlap_not_double_counted": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_not_inferred": {"S1", "S2"},
    "possible_overlap_and_deduplication": {"MEDVISION_SYSTEM_POLICY"},
    "nodule_mass_is_more_specific_focal_descriptor": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "opacity_not_separate_malignancy_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "cancer_not_diagnosed": {"S1", "S2"},
    "diffuse_distribution_preserved": {"S1"},
    "respiratory_context_preserved": {"S4"},
    "disease_remains_undetermined": {"S1", "S2", "S3", "S4"},
    "context_specific_characterization_may_be_relevant": {"S3", "S4"},
    "high_priority_not_automatic_without_compromise": {"MEDVISION_SYSTEM_POLICY"},
    "cxr_broad_finding_preserved": {"S1", "S2"},
    "ct_ground_glass_preserved_separately": {"S1"},
    "ground_glass_not_attributed_to_cxr": {"S1"},
    "etiology_not_inferred_from_ct_morphology": {"S1"},
    "score_0_89_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_underlying_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"S5", "MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"S5", "MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"S5", "MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_from_lung_opacity": {"S1", "S2"},
    "cancer_from_lung_opacity": {"S1", "S2"},
    "edema_from_lung_opacity": {"S1"},
    "ild_from_lung_opacity": {"S1", "S3"},
    "pneumonia_from_overlap": {"S1", "S2"},
    "independent_disease_evidence_double_count": {"MEDVISION_SYSTEM_POLICY"},
    "obstruction_from_overlap": {"S1", "S2"},
    "independent_malignancy_evidence_double_count": {"MEDVISION_SYSTEM_POLICY"},
    "automatic_high_priority_without_compromise": {"MEDVISION_SYSTEM_POLICY"},
    "autonomous_ct_or_treatment_order": {"MEDVISION_SYSTEM_POLICY"},
    "cxr_opacity_rewritten_as_ground_glass": {"S1"},
    "disease_from_ground_glass_morphology": {"S1"},
    "score_as_pneumonia_cancer_or_disease_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "silent_ai_preference": {"S5", "MEDVISION_SYSTEM_POLICY"},
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
def test_each_case_uses_canonical_finding_and_selects_lung_opacity_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Lung Opacity"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-lung-opacity") == 1
    assert "requires_doctor_review: true" in prompt


@pytest.mark.parametrize(
    ("case_id", "cofinding", "skill"),
    [
        ("opacity_with_consolidation", "Consolidation", "medvision-consolidation"),
        ("opacity_with_atelectasis", "Atelectasis", "medvision-atelectasis"),
        ("opacity_with_nodule_mass", "Nodule/Mass", "medvision-nodule-mass"),
    ],
)
def test_overlap_cases_preserve_both_findings_and_select_both_skills(
    case_id, cofinding, skill
):
    case = _case(case_id)
    _, case_data = _case_data(case)
    names = [item["name"] for item in case_data["model_findings"]["findings"]]
    selected = resolve_hermes_skills(case_data)

    assert names == ["Lung Opacity", cofinding]
    assert selected.count("medvision-lung-opacity") == 1
    assert selected.count(skill) == 1
    assert "overlap_not_double_counted" in case["semantic_expectations"] or (
        "opacity_not_separate_malignancy_evidence" in case["semantic_expectations"]
    )


def test_infiltration_remains_a_separate_canonical_upstream_finding():
    prompt = build_report_prompt(
        results=[
            {"finding": "Lung Opacity", "score": 0.82, "threshold": 0.5},
            {"finding": "Infiltration", "score": 0.8, "threshold": 0.5},
        ]
    )
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    names = [item["name"] for item in case_data["model_findings"]["findings"]]
    selected = resolve_hermes_skills(case_data)

    assert names == ["Lung Opacity", "Infiltration"]
    assert names.count("Lung Opacity") == 1
    assert names.count("Infiltration") == 1
    assert selected.count("medvision-lung-opacity") == 1
    assert selected.count("medvision-infiltration") == 1


def test_ct_ground_glass_and_score_boundaries_are_explicit():
    ct_case = _case("cxr_opacity_with_ct_ground_glass")
    score_case = _case("score_semantics")
    isolated = _case("isolated_opacity_missing_context")

    assert "CT ngực" in ct_case["input"]["history"]
    assert "kính mờ" in ct_case["input"]["history"]
    assert "ground_glass_not_attributed_to_cxr" in ct_case[
        "semantic_expectations"
    ]
    assert score_case["input"]["results"][0]["score"] == 0.89
    assert not re.search(
        r"pneumonia|cancer|edema|ild",
        " ".join(isolated["semantic_expectations"]),
        re.I,
    )


def test_autonomous_imaging_and_treatment_are_only_forbidden():
    cases = _load_cases()
    expectations = {
        item for case in cases for item in case["semantic_expectations"]
    }
    forbidden = {
        item for case in cases for item in case["forbidden_interpretations"]
    }

    assert "autonomous_ct_or_treatment_order" not in expectations
    assert "autonomous_ct_or_treatment_order" in forbidden
