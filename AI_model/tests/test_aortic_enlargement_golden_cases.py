"""Provider-independent validation for the Aortic enlargement golden-case pack."""

import json
from pathlib import Path

import pytest

from hermes_report import build_report_prompt, resolve_hermes_skills


CASES_PATH = (
    Path(__file__).parent / "golden_cases" / "aortic_enlargement" / "cases.json"
)
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "positive_missing_direct_imaging",
    "cxr_with_ct_measured_dilatation",
    "high_risk_aas_symptoms",
    "nonspecific_cxr_with_high_risk_aas_context",
    "longstanding_hypertension_context",
    "cxr_direct_imaging_discordance",
    "score_semantics",
    "ai_human_cxr_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "radiographic_finding_preserved": {"S1"},
    "direct_measurement_missing_explicit": {"S1", "S2"},
    "aneurysm_or_dissection_not_invented": {"S1", "S2"},
    "direct_ct_measurement_stronger_for_true_size": {"S1", "S2", "S3"},
    "cxr_and_direct_imaging_preserved_separately": {"S1", "S2", "S3"},
    "aneurysm_requires_segment_measurement_context": {"S2", "S3"},
    "missing_growth_not_invented": {"S2", "S3"},
    "acute_aortic_syndrome_concern": {"S1", "S2"},
    "high_priority_clinical_review": {"S1", "S2"},
    "dissection_not_confirmed": {"S1", "S2"},
    "normal_or_nonspecific_cxr_does_not_exclude_aas": {"S1", "S2"},
    "hypertension_supports_remodeling_context": {"S4", "S5", "S6"},
    "hypertension_not_diagnosed_from_cxr": {"S6"},
    "no_universal_arch_width_cutoff": {"S5", "S6"},
    "direct_measurement_stronger_for_true_size": {"S1", "S2", "S3"},
    "modality_measurement_discordance": {"S1", "S2", "S3"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "score_0_88_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_aortic_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "aneurysm_from_cxr_class": {"S1", "S2"},
    "dissection_from_cxr_class": {"S1", "S2"},
    "invented_aortic_measurement": {"S1", "S2", "S3"},
    "invented_growth_rate": {"S2", "S3"},
    "dissection_confirmed": {"S1", "S2"},
    "autonomous_aortic_treatment": {"MEDVISION_SYSTEM_POLICY"},
    "aas_excluded_by_normal_or_nonspecific_cxr": {"S1", "S2"},
    "hypertension_diagnosed_from_cxr": {"S6"},
    "universal_cxr_aortic_width_threshold": {"S5", "S6"},
    "silent_ai_preference": {"MEDVISION_SYSTEM_POLICY"},
    "score_as_aneurysm_dissection_or_aas_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
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
    assert EXPECTATION_PROVENANCE["autonomous_aortic_treatment"] == {
        "MEDVISION_SYSTEM_POLICY"
    }
    assert not any(
        "treatment" in item or "procedure" in item
        for item in expectations
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_uses_canonical_finding_and_selects_aortic_skill_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt = build_report_prompt(**case["input"])
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Aortic enlargement"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-aortic-enlargement") == 1
    assert "requires_doctor_review: true" in prompt


def test_aas_cases_encode_high_risk_context_without_confirmed_dissection():
    for case_id in (
        "high_risk_aas_symptoms",
        "nonspecific_cxr_with_high_risk_aas_context",
    ):
        case = _case(case_id)
        expectations = set(case["semantic_expectations"])
        forbidden = set(case["forbidden_interpretations"])
        assert "đột ngột dữ dội" in case["input"]["symptoms"]
        assert {
            "acute_aortic_syndrome_concern",
            "high_priority_clinical_review",
        } <= expectations
        assert "dissection_confirmed" in forbidden
        assert "autonomous_aortic_treatment" in forbidden


def test_direct_imaging_and_hypertension_boundaries_are_explicit():
    measured = _case("cxr_with_ct_measured_dilatation")["input"]
    nonspecific = _case("nonspecific_cxr_with_high_risk_aas_context")["input"]
    hypertension = _case("longstanding_hypertension_context")["input"]
    discordance = _case("cxr_direct_imaging_discordance")["input"]
    score = _case("score_semantics")["input"]
    conflict = _case("ai_human_cxr_conflict")["input"]

    assert "CTA" in measured["history"] and "43 mm" in measured["history"]
    assert "tốc độ tăng trưởng" in measured["history"]
    assert "không đặc hiệu" in nonspecific["history"]
    assert "tăng huyết áp kéo dài" in hypertension["history"]
    assert not any(char.isdigit() for char in hypertension["history"])
    assert "CTA" in discordance["history"] and "giới hạn bình thường" in discordance["history"]
    assert score["results"][0]["score"] == 0.88
    assert "không to" in conflict["history"]
