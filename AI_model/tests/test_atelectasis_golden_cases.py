"""Provider-independent validation for the Atelectasis golden-case pack."""

import json
from pathlib import Path

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = Path(__file__).parent / "golden_cases" / "atelectasis" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "positive_missing_clinical_data",
    "perioperative_hypoxemia",
    "possible_airway_obstruction",
    "infectious_symptoms",
    "no_infection_evidence",
    "atelectasis_with_pleural_effusion",
    "score_semantics",
    "ai_human_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "radiographic_finding_preserved": {"S1"},
    "explicit_missing_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "mechanism_or_etiology_not_invented": {"S1", "S3", "S4"},
    "perioperative_context_supported": {"S5", "S6"},
    "high_priority_clinical_review": {"MEDVISION_SYSTEM_POLICY"},
    "obstructive_mechanism_hypothesis": {"S1", "S3", "S4"},
    "obstructive_cause_to_review": {"S1", "S3", "S4"},
    "infection_hypothesis_evaluated_separately": {"S4"},
    "absence_of_infection_symptoms_not_finding_contradiction": {"S4"},
    "pneumonia_support_low_or_unknown": {"S4"},
    "compressive_mechanism_hypothesis": {"S1", "S4"},
    "cooccurrence_not_causation": {"S1", "S4"},
    "score_0_86_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_probability_or_chance": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "final_etiologic_diagnosis": {"S1", "S3", "S4"},
    "unsupported_mechanism": {"S1", "S3", "S4"},
    "autonomous_respiratory_treatment_or_procedure": {"MEDVISION_SYSTEM_POLICY"},
    "automatic_lung_cancer_diagnosis": {"S1", "S3", "S4"},
    "pneumonia_confirmed_from_atelectasis": {"S4"},
    "atelectasis_rejected_due_to_no_fever_or_cough": {"S4"},
    "pleural_effusion_proves_compressive_cause": {"S1", "S4"},
    "score_as_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
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


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_uses_canonical_findings_and_selects_atelectasis_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt = build_report_prompt(**case["input"])
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Atelectasis"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-atelectasis") == 1
    assert "requires_doctor_review: true" in prompt


def test_case_inputs_encode_the_required_evidence_boundaries():
    perioperative = _case("perioperative_hypoxemia")["input"]
    obstruction = _case("possible_airway_obstruction")["input"]
    combined = _case("atelectasis_with_pleural_effusion")["input"]
    score = _case("score_semantics")["input"]
    conflict = _case("ai_human_conflict")["input"]

    assert "phẫu thuật" in perioperative["history"]
    assert "gây mê" in perioperative["history"]
    assert "SpO2" in perioperative["symptoms"]
    assert obstruction["results"][0]["anatomic_location"] == "right upper lobe"
    assert "tắc nghẽn đường thở trung tâm" in obstruction["history"]
    assert [item["finding"] for item in combined["results"]] == [
        "Atelectasis",
        "Pleural effusion",
    ]
    assert score["results"][0]["score"] == 0.86
    assert "không có xẹp phổi" in conflict["history"]
