"""Provider-independent validation for the Cardiomegaly golden-case pack."""

import json
from pathlib import Path
import re

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = Path(__file__).parent / "golden_cases" / "cardiomegaly" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "positive_missing_projection_and_context",
    "pa_ctr_above_0_50",
    "ap_portable_apparent_cardiomegaly",
    "heart_failure_compatible_context",
    "normal_ef_no_lv_dysfunction",
    "known_pericardial_effusion",
    "score_semantics",
    "ai_human_cxr_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "radiographic_finding_preserved": {"S1"},
    "projection_missing_explicit": {"S1"},
    "hf_or_reduced_ef_not_invented": {"S3", "S4"},
    "classic_pa_interpretation_evaluable": {"S1"},
    "radiographic_cardiac_enlargement_supported": {"S1"},
    "true_chamber_enlargement_not_automatic": {"S2"},
    "projection_limitation": {"S1", "S6"},
    "classic_pa_threshold_not_applied_unchanged": {"S1", "S6"},
    "projection_uncertainty_increased": {"S6"},
    "heart_failure_hypothesis_supported": {"S3", "S5"},
    "heart_failure_not_automatically_confirmed": {"S3"},
    "bnp_used_as_context_not_standalone_proof": {"S5"},
    "reduced_ef_not_inferred": {"S3", "S4"},
    "normal_ef_does_not_invalidate_radiographic_finding": {"S1", "S3"},
    "modality_distinction_preserved": {"S1", "S3"},
    "pericardial_process_may_contribute_to_silhouette": {"S1", "S3"},
    "silhouette_not_equated_with_chamber_enlargement": {"S1", "S2"},
    "cxr_did_not_diagnose_pericardial_effusion": {"S1", "S3"},
    "score_0_93_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_probability_or_chance": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "heart_failure_from_cardiomegaly": {"S3"},
    "reduced_ef_from_cardiomegaly": {"S4"},
    "true_chamber_enlargement_proven_by_ctr": {"S2"},
    "heart_failure_from_ctr": {"S1", "S3"},
    "reduced_ef_from_ctr": {"S1", "S4"},
    "pa_ctr_rule_applied_unchanged_to_ap": {"S1", "S6"},
    "universal_bnp_threshold": {"S5"},
    "autonomous_heart_failure_treatment": {"MEDVISION_SYSTEM_POLICY"},
    "normal_ef_proves_radiographic_finding_false": {"S1", "S3"},
    "silhouette_equals_myocardial_chamber_enlargement": {"S1", "S2"},
    "pericardial_effusion_diagnosed_from_cxr_alone": {"S1", "S3"},
    "score_as_heart_failure_or_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
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
    assert (
        EXPECTATION_PROVENANCE["autonomous_heart_failure_treatment"]
        == {"MEDVISION_SYSTEM_POLICY"}
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_uses_canonical_finding_and_selects_cardiomegaly_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt = build_report_prompt(**case["input"])
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Cardiomegaly"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-cardiomegaly") == 1
    assert "requires_doctor_review: true" in prompt


def test_case_inputs_encode_projection_and_modality_boundaries_without_bnp_cutoff():
    missing = _case("positive_missing_projection_and_context")["input"]
    pa = _case("pa_ctr_above_0_50")["input"]
    ap = _case("ap_portable_apparent_cardiomegaly")["input"]
    heart_failure = _case("heart_failure_compatible_context")["input"]
    normal_ef = _case("normal_ef_no_lv_dysfunction")["input"]
    pericardial = _case("known_pericardial_effusion")["input"]
    score = _case("score_semantics")["input"]
    conflict = _case("ai_human_cxr_conflict")["input"]

    assert not missing["history"]
    assert "tư thế PA" in pa["history"] and "CTR = 0.54" in pa["history"]
    assert "portable tư thế AP" in ap["history"] and "CTR đo được 0.56" in ap["history"]
    assert "BNP" in heart_failure["laboratory"]
    assert not re.search(r"BNP[^;]*\d", heart_failure["laboratory"])
    assert "EF 60%" in normal_ef["history"]
    assert "TTE" in pericardial["history"]
    assert score["results"][0]["score"] == 0.93
    assert "không có tim to" in conflict["history"]
