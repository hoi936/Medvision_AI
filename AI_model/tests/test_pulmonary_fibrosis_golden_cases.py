"""Provider-independent validation for the Pulmonary fibrosis golden cases."""

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


CASES_PATH = (
    Path(__file__).parent / "golden_cases" / "pulmonary_fibrosis" / "cases.json"
)
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "cxr_fibrosis_without_ct",
    "ild_pulmonary_fibrosis_overlap",
    "fibrosis_lung_opacity_infiltration_overlap",
    "explicit_hrct_reticulation_traction_bronchiectasis",
    "hrct_honeycombing_uip_compatible_pattern",
    "longitudinal_ppf_two_domains_within_one_year",
    "score_semantics",
    "cxr_ai_hrct_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "local_cxr_fibrosis_finding_preserved": {"S2"},
    "hrct_characterization_unknown": {"S1", "S4", "S5"},
    "etiology_unknown": {"S3", "S6"},
    "both_upstream_labels_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "overlapping_finding_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "fibrosis_refines_broad_ild_pattern": {"S2", "S6"},
    "overlap_not_double_counted": {"MEDVISION_SYSTEM_POLICY"},
    "all_three_upstream_labels_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "fibrosis_more_specific_chronic_pattern": {"S1", "S2"},
    "triple_counting_prevented": {"MEDVISION_SYSTEM_POLICY"},
    "explicit_ct_morphology_preserved": {"S1", "S4", "S5"},
    "fibrotic_imaging_evidence_strengthened": {"S4", "S5"},
    "ipf_not_confirmed": {"S3"},
    "reported_honeycombing_preserved": {"S1", "S4", "S5"},
    "reported_uip_compatible_pattern_preserved": {"S3"},
    "ipf_not_automatically_diagnosed": {"S3"},
    "missing_etiologic_mdd_context_explicit": {"S3", "S4", "S5", "S6"},
    "non_ipf_ild_fibrosis_context_preserved": {"S3"},
    "ppf_evaluable": {"S3"},
    "ppf_supported_from_two_supplied_domains": {"S3"},
    "within_one_year_explicit": {"S3"},
    "alternative_explanation_handling_explicit": {"S3"},
    "score_0_92_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_ipf_uip_ppf_or_fibrotic_ild_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "hrct_more_specific_fibrosis_characterization": {"S4", "S5"},
    "ai_not_silently_erased": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "cxr_fibrosis_as_ipf_uip_ppf": {"S3"},
    "invented_ct_morphology": {"S1", "S4", "S5"},
    "autonomous_hrct_order": {"MEDVISION_SYSTEM_POLICY"},
    "overlap_as_ipf": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "independent_disease_evidence_double_count": {"MEDVISION_SYSTEM_POLICY"},
    "independent_disease_evidence_triple_count": {"MEDVISION_SYSTEM_POLICY"},
    "overlap_as_specific_etiology": {"S3", "S6"},
    "invented_honeycombing": {"S1", "S4", "S5"},
    "ct_morphology_as_ipf": {"S3"},
    "autonomous_treatment_order": {"MEDVISION_SYSTEM_POLICY"},
    "uip_pattern_equals_ipf": {"S3"},
    "invented_etiology": {"S3", "S6"},
    "autonomous_biopsy_or_bronchoscopy_order": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "ppf_from_single_study": {"S3"},
    "invented_physiological_progression": {"S3"},
    "score_as_ipf_uip_ppf_or_fibrotic_ild_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "silent_ai_erasure": {"MEDVISION_SYSTEM_POLICY"},
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
    *, non_ipf_ild, radiological_fibrosis, progression_domains,
    start_date, end_date, alternative_explanation_absent
):
    interval_days = (end_date - start_date).days
    return (
        non_ipf_ild
        and radiological_fibrosis
        and len(set(progression_domains)) >= 2
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
def test_each_case_preserves_canonical_finding_and_selects_skill_once(case):
    canonical_names = set(json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8")))
    prompt, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["name"] == "Pulmonary fibrosis"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-pulmonary-fibrosis") == 1
    assert "requires_doctor_review: true" in prompt
    assert FINDING_SKILL_MAP["Pulmonary fibrosis"] == (
        "medvision-pulmonary-fibrosis"
    )


def test_cxr_only_case_separates_finding_from_diagnosis_and_ct_morphology():
    case = _case("cxr_fibrosis_without_ct")

    assert {
        "local_cxr_fibrosis_finding_preserved",
        "hrct_characterization_unknown",
        "etiology_unknown",
    } <= set(case["semantic_expectations"])
    assert {
        "cxr_fibrosis_as_ipf_uip_ppf",
        "invented_ct_morphology",
    } <= set(case["forbidden_interpretations"])
    assert "honeycombing" not in case["input"]["history"].lower()
    assert "traction" not in case["input"]["history"].lower()


def test_ct_morphology_is_allowed_only_when_explicitly_supplied():
    explicit = _case("explicit_hrct_reticulation_traction_bronchiectasis")
    cxr_only = _case("cxr_fibrosis_without_ct")

    assert "lưới hóa" in explicit["input"]["history"]
    assert "giãn phế quản co kéo" in explicit["input"]["history"]
    assert "explicit_ct_morphology_preserved" in explicit["semantic_expectations"]
    assert "invented_honeycombing" in explicit["forbidden_interpretations"]
    assert "explicit_ct_morphology_preserved" not in cxr_only[
        "semantic_expectations"
    ]


def test_reported_honeycombing_and_uip_do_not_automatically_establish_ipf():
    case = _case("hrct_honeycombing_uip_compatible_pattern")

    assert "honeycombing" in case["input"]["history"]
    assert "reported_honeycombing_preserved" in case["semantic_expectations"]
    assert "reported_uip_compatible_pattern_preserved" in case[
        "semantic_expectations"
    ]
    assert "uip_pattern_equals_ipf" in case["forbidden_interpretations"]


def test_ild_fibrosis_overlap_preserves_both_and_selects_both_once():
    case = _case("ild_pulmonary_fibrosis_overlap")
    _, case_data = _case_data(case)
    names = [item["name"] for item in case_data["model_findings"]["findings"]]
    selected = resolve_hermes_skills(case_data)

    assert names == ["Pulmonary fibrosis", "ILD"]
    assert selected.count("medvision-pulmonary-fibrosis") == 1
    assert selected.count("medvision-ild") == 1
    assert "overlapping_finding_evidence" in case["semantic_expectations"]
    assert "overlap_not_double_counted" in case["semantic_expectations"]


def test_triple_overlap_preserves_labels_without_triple_counting():
    case = _case("fibrosis_lung_opacity_infiltration_overlap")
    _, case_data = _case_data(case)
    names = [item["name"] for item in case_data["model_findings"]["findings"]]
    selected = resolve_hermes_skills(case_data)
    expected_skills = {
        "medvision-pulmonary-fibrosis",
        "medvision-lung-opacity",
        "medvision-infiltration",
    }

    assert names == ["Pulmonary fibrosis", "Lung Opacity", "Infiltration"]
    assert all(selected.count(skill) == 1 for skill in expected_skills)
    assert expected_skills <= set(selected)
    assert "triple_counting_prevented" in case["semantic_expectations"]


def test_ppf_positive_case_meets_all_context_and_longitudinal_requirements():
    case = _case("longitudinal_ppf_two_domains_within_one_year")
    assert _ppf_criteria_satisfied(
        non_ipf_ild=True,
        radiological_fibrosis=True,
        progression_domains={"worsening_symptoms", "radiological_progression"},
        start_date=date(2026, 1, 1),
        end_date=date(2026, 9, 1),
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


def test_single_study_or_missing_non_ipf_context_cannot_satisfy_ppf():
    assert not _ppf_criteria_satisfied(
        non_ipf_ild=True,
        radiological_fibrosis=True,
        progression_domains={"radiological_progression"},
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 1),
        alternative_explanation_absent=True,
    )
    assert not _ppf_criteria_satisfied(
        non_ipf_ild=False,
        radiological_fibrosis=True,
        progression_domains={"worsening_symptoms", "radiological_progression"},
        start_date=date(2026, 1, 1),
        end_date=date(2026, 9, 1),
        alternative_explanation_absent=True,
    )


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


def test_score_is_preserved_without_disease_probability_semantics():
    case = _case("score_semantics")

    assert case["input"]["results"][0]["score"] == 0.92
    assert "score_not_ipf_uip_ppf_or_fibrotic_ild_probability" in case[
        "semantic_expectations"
    ]
    assert not re.search(
        r"92\s*%\s*(ipf|uip|ppf|fibrotic ild)",
        " ".join(case["semantic_expectations"]),
        re.I,
    )
