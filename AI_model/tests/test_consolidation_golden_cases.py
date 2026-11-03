"""Provider-independent validation for the Consolidation golden-case pack."""

import json
from pathlib import Path

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = Path(__file__).parent / "golden_cases" / "consolidation" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "positive_missing_clinical_data",
    "infectious_context",
    "no_infectious_context",
    "edema_compatible_context",
    "hemorrhage_compatible_high_risk",
    "air_bronchogram",
    "score_semantics",
    "ai_human_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "radiographic_descriptor_preserved": {"S1"},
    "explicit_missing_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "etiology_not_invented": {"S1", "S2"},
    "pneumonia_or_infection_hypothesis": {"S3"},
    "pneumonia_not_automatically_confirmed": {"S1", "S3"},
    "absence_of_infection_symptoms_not_descriptor_contradiction": {"S1", "S3"},
    "pneumonia_unsupported_or_uncertain": {"S3"},
    "pulmonary_edema_hypothesis": {"S4"},
    "cardiogenic_mechanism_not_automatic": {"S4"},
    "pulmonary_hemorrhage_hypothesis": {"S5"},
    "high_priority_clinical_review": {"MEDVISION_SYSTEM_POLICY"},
    "hemorrhage_not_diagnosed_from_image_alone": {"S5"},
    "air_bronchogram_supports_morphology_only": {"S1"},
    "score_0_91_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_probability_or_chance": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "final_etiologic_diagnosis": {"S1", "S2"},
    "pneumonia_confirmed_from_consolidation": {"S1", "S3"},
    "autonomous_antibiotic_order": {"MEDVISION_SYSTEM_POLICY"},
    "consolidation_rejected_due_to_no_fever_or_cough": {"S1", "S3"},
    "automatic_cardiogenic_edema_diagnosis": {"S4"},
    "autonomous_diuretic_or_ventilatory_order": {"MEDVISION_SYSTEM_POLICY"},
    "definitive_pulmonary_hemorrhage_from_image": {"S5"},
    "autonomous_treatment_or_procedure": {"MEDVISION_SYSTEM_POLICY"},
    "pneumonia_inferred_from_air_bronchogram": {"S1", "S3"},
    "score_as_pneumonia_or_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
    "silent_ai_preference": {"MEDVISION_SYSTEM_POLICY"},
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def test_golden_pack_has_required_cases_and_only_provenanced_expectations():
    cases = _load_cases()
    expectations = {
        item
        for case in cases
        for item in case["semantic_expectations"]
    }
    forbidden = {
        item
        for case in cases
        for item in case["forbidden_interpretations"]
    }

    assert {case["id"] for case in cases} == EXPECTED_CASE_IDS
    assert len(cases) == len(EXPECTED_CASE_IDS)
    assert expectations <= EXPECTATION_PROVENANCE.keys()
    assert forbidden <= EXPECTATION_PROVENANCE.keys()
    assert all(
        sources and sources <= ALLOWED_PROVENANCE
        for sources in EXPECTATION_PROVENANCE.values()
    )
    assert all("doctor_review_required" in case["semantic_expectations"] for case in cases)
    assert all(
        EXPECTATION_PROVENANCE[item] == {"MEDVISION_SYSTEM_POLICY"}
        for item in (
            "autonomous_antibiotic_order",
            "autonomous_diuretic_or_ventilatory_order",
            "autonomous_treatment_or_procedure",
        )
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_uses_canonical_finding_and_selects_consolidation_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt = build_report_prompt(**case["input"])
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Consolidation"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-consolidation") == 1
    assert "requires_doctor_review: true" in prompt


def test_case_inputs_encode_the_required_evidence_boundaries():
    infection = _case("infectious_context")["input"]
    no_infection = _case("no_infectious_context")["input"]
    edema = _case("edema_compatible_context")["input"]
    hemorrhage = _case("hemorrhage_compatible_high_risk")["input"]
    air_bronchogram = _case("air_bronchogram")["input"]
    score = _case("score_semantics")["input"]
    conflict = _case("ai_human_conflict")["input"]

    assert "Sốt" in infection["symptoms"] and "ho" in infection["symptoms"]
    assert "Không sốt, không ho" in no_infection["symptoms"]
    assert "quá tải thể tích" in edema["history"]
    assert "Ho ra máu" in hemorrhage["symptoms"]
    assert "SpO2 82%" in hemorrhage["symptoms"]
    assert "Hemoglobin giảm" in hemorrhage["laboratory"]
    assert "air bronchogram" in air_bronchogram["history"]
    assert score["results"][0]["score"] == 0.91
    assert "không có consolidation" in conflict["history"]
