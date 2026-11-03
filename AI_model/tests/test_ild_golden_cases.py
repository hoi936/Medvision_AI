"""Provider-independent validation for the ILD golden-case pack."""

from datetime import date
import json
from pathlib import Path
import re

import pytest

from hermes_report import (
    FINDING_SKILL_MAP,
    build_report_prompt,
    resolve_hermes_skills,
)


CASES_PATH = Path(__file__).parent / "golden_cases" / "ild" / "cases.json"
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "cxr_ild_without_ct",
    "ild_lung_opacity_infiltration_overlap",
    "explicit_hrct_reticulation_traction_bronchiectasis",
    "uip_pattern_incomplete_context",
    "ct_ila_without_disease_level_context",
    "longitudinal_ppf_two_domains_within_one_year",
    "score_semantics",
    "cxr_ai_hrct_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "broad_cxr_interstitial_pattern_preserved": {"S1", "S2"},
    "hrct_pattern_unknown": {"S1", "S4"},
    "fibrosis_status_unknown": {"S2"},
    "missing_characterization_explicit": {"S2", "S4"},
    "all_three_upstream_labels_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ild_more_specific_interstitial_reasoning": {"S1", "S2"},
    "overlapping_finding_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "triple_counting_prevented": {"MEDVISION_SYSTEM_POLICY"},
    "no_subtype_diagnosis": {"S2", "S3"},
    "explicit_ct_morphology_preserved": {"S1"},
    "fibrotic_concern_supported_by_supplied_ct": {"S1", "S2"},
    "ipf_not_confirmed": {"S3"},
    "reported_uip_compatible_pattern_preserved": {"S3"},
    "ipf_not_automatically_diagnosed": {"S3"},
    "missing_etiologic_clinical_mdd_context_explicit": {"S2", "S3"},
    "ct_ila_context_preserved": {"S5"},
    "ila_not_specific_clinical_ild": {"S5"},
    "cxr_classifier_not_ats_ila": {"S5"},
    "missing_disease_level_context_explicit": {"S5"},
    "ppf_evaluable": {"S3"},
    "ppf_supported_from_two_supplied_domains": {"S3"},
    "within_one_year_explicit": {"S3"},
    "alternative_explanation_handling_explicit": {"S3"},
    "score_0_91_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_ild_subtype_probability": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "hrct_more_specific_characterization": {"S1", "S4"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "cxr_ild_as_ipf_uip_nsip": {"S2", "S3"},
    "cxr_ild_as_pulmonary_fibrosis": {"S2"},
    "invented_ct_morphology": {"S1", "S4"},
    "autonomous_hrct_order": {"MEDVISION_SYSTEM_POLICY"},
    "independent_disease_evidence_triple_count": {"MEDVISION_SYSTEM_POLICY"},
    "overlap_as_ild_subtype": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "invented_honeycombing": {"S1"},
    "ct_morphology_as_ipf": {"S3"},
    "autonomous_treatment_order": {"MEDVISION_SYSTEM_POLICY"},
    "uip_pattern_equals_ipf": {"S3"},
    "invented_etiology": {"S2", "S3"},
    "autonomous_biopsy_or_bronchoscopy_order": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "ila_as_specific_ild": {"S5"},
    "cxr_ild_called_ats_ila": {"S5"},
    "ppf_from_single_study": {"S3"},
    "invented_physiological_progression": {"S3"},
    "score_as_ipf_uip_fibrosis_or_subtype_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "silent_ai_preference": {"MEDVISION_SYSTEM_POLICY"},
    "conflict_erased": {"MEDVISION_SYSTEM_POLICY"},
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


def _ppf_criteria_satisfied(
    progression_domains, start_date, end_date, alternative_explanation_absent
):
    interval_days = (end_date - start_date).days
    return (
        len(set(progression_domains)) >= 2
        and 0 < interval_days <= 366
        and alternative_explanation_absent
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
    assert len(cases) == 8
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
def test_each_case_preserves_canonical_ild_and_selects_skill_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "ILD"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-ild") == 1
    assert "requires_doctor_review: true" in prompt
    assert FINDING_SKILL_MAP["ILD"] == "medvision-ild"


def test_cxr_only_case_forbids_subtype_fibrosis_and_invented_ct_morphology():
    case = _case("cxr_ild_without_ct")

    assert {"hrct_pattern_unknown", "fibrosis_status_unknown"} <= set(
        case["semantic_expectations"]
    )
    assert {
        "cxr_ild_as_ipf_uip_nsip",
        "cxr_ild_as_pulmonary_fibrosis",
        "invented_ct_morphology",
    } <= set(case["forbidden_interpretations"])
    assert "reticulation" not in case["input"]["history"].lower()
    assert "honeycombing" not in case["input"]["history"].lower()


def test_ct_morphology_is_allowed_only_when_explicitly_supplied():
    explicit = _case("explicit_hrct_reticulation_traction_bronchiectasis")
    cxr_only = _case("cxr_ild_without_ct")

    assert "lưới hóa" in explicit["input"]["history"]
    assert "giãn phế quản co kéo" in explicit["input"]["history"]
    assert "explicit_ct_morphology_preserved" in explicit["semantic_expectations"]
    assert "invented_honeycombing" in explicit["forbidden_interpretations"]
    assert "explicit_ct_morphology_preserved" not in cxr_only[
        "semantic_expectations"
    ]


def test_uip_ipf_and_ila_clinical_ild_boundaries_are_explicit():
    uip = _case("uip_pattern_incomplete_context")
    ila = _case("ct_ila_without_disease_level_context")

    assert "reported_uip_compatible_pattern_preserved" in uip[
        "semantic_expectations"
    ]
    assert "uip_pattern_equals_ipf" in uip["forbidden_interpretations"]
    assert "ct_ila_context_preserved" in ila["semantic_expectations"]
    assert "ila_as_specific_ild" in ila["forbidden_interpretations"]
    assert "cxr_ild_called_ats_ila" in ila["forbidden_interpretations"]


def test_ppf_positive_case_meets_two_of_three_within_one_year():
    case = _case("longitudinal_ppf_two_domains_within_one_year")
    assert _ppf_criteria_satisfied(
        {"worsening_symptoms", "radiological_progression"},
        date(2026, 1, 1),
        date(2026, 9, 1),
        alternative_explanation_absent=True,
    )
    assert "ppf_supported_from_two_supplied_domains" in case[
        "semantic_expectations"
    ]
    assert "alternative_explanation_handling_explicit" in case[
        "semantic_expectations"
    ]
    assert "invented_physiological_progression" in case[
        "forbidden_interpretations"
    ]


def test_single_study_or_one_domain_cannot_satisfy_ppf():
    assert not _ppf_criteria_satisfied(
        {"radiological_progression"},
        date(2026, 4, 1),
        date(2026, 4, 1),
        alternative_explanation_absent=True,
    )
    assert "ppf_from_single_study" in _case(
        "longitudinal_ppf_two_domains_within_one_year"
    )["forbidden_interpretations"]


def test_overlap_preserves_three_labels_and_selects_distinct_skills():
    case = _case("ild_lung_opacity_infiltration_overlap")
    _, case_data = _case_data(case)
    names = [item["name"] for item in case_data["model_findings"]["findings"]]
    selected = resolve_hermes_skills(case_data)
    expected_skills = {
        "medvision-ild",
        "medvision-lung-opacity",
        "medvision-infiltration",
    }

    assert names == ["ILD", "Lung Opacity", "Infiltration"]
    assert all(selected.count(skill) == 1 for skill in expected_skills)
    assert expected_skills <= set(selected)
    assert "overlapping_finding_evidence" in case["semantic_expectations"]
    assert "triple_counting_prevented" in case["semantic_expectations"]


def test_no_case_expects_autonomous_imaging_procedure_or_treatment():
    cases = _load_cases()
    assert all(
        not any(
            item.startswith("autonomous_")
            for item in case["semantic_expectations"]
        )
        for case in cases
    )
    forbidden = {
        item for case in cases for item in case["forbidden_interpretations"]
    }
    assert {
        "autonomous_hrct_order",
        "autonomous_biopsy_or_bronchoscopy_order",
        "autonomous_treatment_order",
    } <= forbidden


def test_score_is_preserved_without_subtype_probability_semantics():
    case = _case("score_semantics")

    assert case["input"]["results"][0]["score"] == 0.91
    assert "score_not_ild_subtype_probability" in case["semantic_expectations"]
    assert not re.search(
        r"91\s*%\s*(ipf|uip|fibrosis|ild subtype)",
        " ".join(case["semantic_expectations"]),
        re.I,
    )
