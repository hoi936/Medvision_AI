"""Provider-independent validation for the Nodule/Mass golden-case pack."""

import json
from pathlib import Path
import re

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = Path(__file__).parent / "golden_cases" / "nodule_mass" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "cxr_positive_without_ct",
    "ct_solid_nodule_measured",
    "ct_spiculated_lesion",
    "ct_mass_over_30_mm",
    "ct_calcification_and_fat_morphology",
    "comparable_prior_imaging_growth",
    "score_semantics",
    "cxr_ct_modality_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "focal_lesion_finding_preserved": {"S1"},
    "ct_characterization_relevant": {"S2"},
    "missing_ct_characterization_explicit": {"S1", "S2"},
    "fleischner_not_evaluable_without_ct": {"S3"},
    "lung_cancer_not_diagnosed": {"S1", "S3", "S4", "S5"},
    "nodule_terminology_from_supplied_size": {"S1"},
    "size_18_mm_preserved": {"S1"},
    "malignancy_remains_hypothesis": {"S3", "S4", "S5"},
    "fleischner_scope_explicitly_evaluated": {"S3"},
    "spiculation_increases_malignancy_concern": {"S3"},
    "cancer_not_confirmed": {"S1", "S3", "S4", "S5"},
    "no_numeric_risk_invented": {"S4", "S5"},
    "mass_terminology_from_supplied_size": {"S1"},
    "size_38_mm_preserved": {"S1"},
    "malignancy_not_confirmed_by_mass_term": {"S1"},
    "stage_or_histology_not_inferred": {"S1", "S5"},
    "calcification_and_fat_recorded": {"S1"},
    "specific_benign_diagnosis_not_invented": {"S1"},
    "cancer_not_automatic": {"S1", "S3"},
    "prior_dates_and_measurements_preserved": {"S3", "S5"},
    "growth_derived_only_from_comparable_data": {"S3", "S5"},
    "growth_rate_not_invented": {"S3", "S5"},
    "ai_score_not_used_as_growth": {"MEDVISION_SYSTEM_POLICY"},
    "score_0_94_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_malignancy_probability": {"MEDVISION_SYSTEM_POLICY"},
    "cxr_ct_modality_discordance": {"S1", "S2"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ct_stronger_for_lesion_characterization": {"S1", "S2"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "lesion_not_treated_as_ct_confirmed": {"S1", "S2"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "lung_cancer_from_cxr_class": {"S1", "S2", "S3"},
    "autonomous_ct_order": {"MEDVISION_SYSTEM_POLICY"},
    "direct_pet_biopsy_or_surgery_from_cxr": {"S2", "S4", "S5"},
    "invented_lesion_size": {"S1"},
    "lung_cancer_from_nodule": {"S1", "S3", "S4", "S5"},
    "invented_numeric_malignancy_probability": {"S4", "S5"},
    "spiculation_proves_cancer": {"S3"},
    "mass_term_proves_malignancy": {"S1"},
    "invented_stage_or_histology": {"S1", "S5"},
    "calcification_or_fat_proves_specific_benign_diagnosis": {"S1"},
    "lung_cancer_from_morphology": {"S1", "S3"},
    "growth_from_ai_score_change": {"MEDVISION_SYSTEM_POLICY"},
    "invented_growth_rate": {"S3", "S5"},
    "score_as_lung_cancer_or_malignancy_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "silent_ai_preference": {"MEDVISION_SYSTEM_POLICY"},
    "ct_confirmation_invented": {"S1", "S2"},
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


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
    autonomous_actions = {
        item for item in forbidden
        if item in {"autonomous_ct_order", "direct_pet_biopsy_or_surgery_from_cxr"}
    }
    assert autonomous_actions == {
        "autonomous_ct_order",
        "direct_pet_biopsy_or_surgery_from_cxr",
    }


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_uses_canonical_finding_and_selects_nodule_mass_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt = build_report_prompt(**case["input"])
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Nodule/Mass"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-nodule-mass") == 1
    assert "requires_doctor_review: true" in prompt


def test_cxr_to_ct_case_matches_acr_age_and_scope_boundary():
    case = _case("cxr_positive_without_ct")
    expectations = set(case["semantic_expectations"])

    assert "56" in case["input"]["demographics"]
    assert "Chưa có CT" in case["input"]["history"]
    assert "ct_characterization_relevant" in expectations
    assert "fleischner_not_evaluable_without_ct" in expectations
    assert "autonomous_ct_order" in case["forbidden_interpretations"]
    assert "direct_pet_biopsy_or_surgery_from_cxr" in case[
        "forbidden_interpretations"
    ]


def test_nodule_mass_terminology_uses_only_supplied_ct_measurements():
    nodule = _case("ct_solid_nodule_measured")
    mass = _case("ct_mass_over_30_mm")

    assert "18 mm" in nodule["input"]["history"]
    assert "nodule_terminology_from_supplied_size" in nodule[
        "semantic_expectations"
    ]
    assert "38 mm" in mass["input"]["history"]
    assert "mass_terminology_from_supplied_size" in mass[
        "semantic_expectations"
    ]
    assert "mass_term_proves_malignancy" in mass["forbidden_interpretations"]


def test_fleischner_scope_is_explicit_in_ct_nodule_case():
    history = _case("ct_solid_nodule_measured")["input"]["history"]
    assert "phát hiện tình cờ" in history
    assert "Không phải CT tầm soát" in history
    assert "không suy giảm miễn dịch" in history
    assert "không có ung thư nguyên phát" in history


def test_no_fixture_encodes_numeric_malignancy_risk_or_ai_growth():
    cases = _load_cases()
    risk_language = "\n".join(
        case["description"] + " " + " ".join(case["semantic_expectations"])
        for case in cases
    )
    growth = _case("comparable_prior_imaging_growth")
    score = _case("score_semantics")

    assert not re.search(r"\b\d+(?:\.\d+)?\s*%\s*(malignancy|cancer|ác tính)", risk_language, re.I)
    assert "12 mm" in growth["input"]["history"]
    assert "15 mm" in growth["input"]["history"]
    assert len(growth["input"]["results"]) == 1
    assert score["input"]["results"][0]["score"] == 0.94
