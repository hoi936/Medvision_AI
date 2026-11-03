"""Provider-independent validation for pulmonary malignancy disease analysis."""

import json
from pathlib import Path

import pytest

from hermes_report import (
    FINDING_SKILL_MAP,
    build_report_prompt,
    resolve_hermes_skills,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_pulmonary_malignancy"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = (
    SKILL_ROOT
    / "medvision-disease-analysis"
    / "references"
    / "pulmonary_malignancy"
)
EXPECTED_CASE_IDS = {f"PM{number:02d}" for number in range(1, 21)}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
ALL_CLINICAL_SOURCES = {"S1", "S2", "S3", "S4", "S5", "S6"}
POLICY = {"MEDVISION_SYSTEM_POLICY"}

EXPECTATION_PROVENANCE = {
    "imaging_lesion_without_sufficient_malignancy_context": {"S1", "S3", "S5"} | POLICY,
    "cxr_provenance_preserved": {"S1", "S5"} | POLICY,
    "growth_unknown": {"S2", "S3", "S4"} | POLICY,
    "doctor_review_required": POLICY,
    "cancer_confirmed": {"S1", "S2", "S3", "S4"} | POLICY,
    "ct_size_inferred_from_cxr_bbox": {"S1", "S2", "S5"} | POLICY,
    "autonomous_ct_or_procedure": {"S1"} | POLICY,
    "pulmonary_malignancy_concern_supported": {"S1", "S2", "S3", "S4"} | POLICY,
    "ct_morphology_provenance_preserved": {"S1", "S2", "S3", "S4"} | POLICY,
    "risk_context_preserved": {"S1", "S2", "S3", "S4"} | POLICY,
    "cancer_confirmed_from_spiculation": {"S1", "S2", "S3", "S4"},
    "histology_invented": {"S3"} | POLICY,
    "autonomous_pet_or_biopsy": {"S3", "S4"} | POLICY,
    "true_growth_preserved": {"S2", "S3", "S4"} | POLICY,
    "same_lesion_correspondence_required": {"S2", "S3", "S4"} | POLICY,
    "cancer_confirmed_from_growth": {"S2", "S3", "S4"},
    "pathology_confirmation_invented": {"S3"} | POLICY,
    "autonomous_surveillance_interval": {"S2", "S4", "S6"} | POLICY,
    "pulmonary_malignancy_concern_indeterminate": {"S1", "S2", "S3", "S4"} | POLICY,
    "missing_prior_explicit": {"S2", "S3", "S4"} | POLICY,
    "synthetic_growth": {"S2", "S3", "S4"},
    "synthetic_stability": {"S2", "S3", "S4"},
    "distinct_label_provenance_preserved": {"S5"} | POLICY,
    "same_lesion_correspondence_unknown": {"S2", "S3", "S4"} | POLICY,
    "benignity_from_generic_calcification": {"S2", "S6"} | POLICY,
    "labels_assumed_same_lesion": {"S2", "S3", "S4"} | POLICY,
    "concern_may_be_reduced_by_trusted_ct_pattern": {"S6"} | POLICY,
    "same_lesion_ct_morphology_preserved": {"S2", "S6"} | POLICY,
    "screening_context_unknown": {"S6"} | POLICY,
    "generic_benignity_rule": {"S2", "S6"} | POLICY,
    "lung_rads_without_screening_context": {"S6"},
    "ct_mass_term_supported": {"S5"},
    "ct_measurement_provenance_preserved": {"S5"} | POLICY,
    "cancer_confirmed_from_mass_size": {"S3", "S5"} | POLICY,
    "histology_or_stage_inferred": {"S3"} | POLICY,
    "resectability_inferred": {"S3"} | POLICY,
    "external_risk_estimate_provenance_preserved": {"S3", "S4"} | POLICY,
    "hidden_malignancy_probability": {"S3", "S4"} | POLICY,
    "implicit_brock_mayo_herder": {"S3", "S4"} | POLICY,
    "external_estimate_relabelled_as_medvision": {"S3", "S4"} | POLICY,
    "cxr_no_finding_preserved": {"S1", "S5"} | POLICY,
    "ct_lesion_preserved": {"S1", "S2"} | POLICY,
    "ct_nodule_excluded_by_no_finding": {"S1", "S5"} | POLICY,
    "no_finding_contradiction_without_positive_target": POLICY,
    "cxr_result_erased": POLICY,
    "other_lesion_ai_provenance_preserved": POLICY,
    "external_nodule_characterization_preserved": {"S1", "S5"} | POLICY,
    "nodule_mass_skill_auto_selected": POLICY,
    "ai_relabelled_as_nodule_mass": POLICY,
    "multiple_lesions_preserved_individually": {"S2", "S3", "S4"} | POLICY,
    "shared_etiology_uncertain": {"S2", "S3", "S4"} | POLICY,
    "metastases_from_multiplicity": {"S2", "S3", "S4"},
    "multifocal_primary_from_multiplicity": {"S2", "S3", "S4"},
    "distinct_lesions_fused": {"S2", "S3", "S4"} | POLICY,
    "screening_ct_context_explicit": {"S6"},
    "lung_rads_scope_may_be_referenced": {"S6"},
    "screening_category_invented": {"S6"} | POLICY,
    "incidental_ct_context_explicit": {"S1", "S2"},
    "acr_fleischner_scope_note": {"S1", "S2"},
    "guideline_scope_uncertainty_explicit": {"S1", "S2", "S6"} | POLICY,
    "lung_rads_applied_to_incidental_ct": {"S6"},
    "cxr_bbox_mapped_to_ct_table": {"S1", "S2"} | POLICY,
    "autonomous_ct_or_surveillance": {"S1", "S2"} | POLICY,
    "pneumonia_hypothesis_preserved": {"S3"} | POLICY,
    "shared_imaging_evidence_not_double_counted": POLICY,
    "forced_pneumonia_malignancy_winner": POLICY,
    "generic_consolidation_assigned_to_cancer": {"S5"} | POLICY,
    "generic_opacity_assigned_to_pneumonia": {"S5"} | POLICY,
    "pulmonary_malignancy_concern_conflicted": {"S3"} | POLICY,
    "nondiagnostic_sample_limitation_preserved": {"S3"} | POLICY,
    "pathology_not_confirmed": {"S3"} | POLICY,
    "nondiagnostic_biopsy_called_benign": {"S3"} | POLICY,
    "pathology_confirmed_malignancy": {"S3"} | POLICY,
    "autonomous_repeat_biopsy": {"S3"} | POLICY,
    "evidence_conflict": POLICY,
    "sample_correspondence_uncertain": {"S3"} | POLICY,
    "lesion_silently_called_benign": {"S3"} | POLICY,
    "imaging_conflict_erased": POLICY,
    "pathology_confirmed_pulmonary_malignancy": {"S3"} | POLICY,
    "malignancy_origin_unresolved": {"S3"} | POLICY,
    "pathology_provenance_preserved": {"S3"} | POLICY,
    "primary_lung_cancer_inferred": {"S3"} | POLICY,
    "stage_or_resectability_inferred": {"S3"} | POLICY,
    "explicit_histology_preserved": {"S3"} | POLICY,
    "explicit_primary_origin_preserved": {"S3"} | POLICY,
    "stage_inferred": {"S3"} | POLICY,
    "autonomous_oncology_treatment": POLICY,
    "explicit_metastatic_origin_preserved": {"S3"} | POLICY,
    "metastasis_relabelled_primary_lung_cancer": {"S3"} | POLICY,
    "model_score_preserved": POLICY,
    "score_not_cancer_probability": POLICY,
    "ninety_two_percent_cancer_probability": POLICY,
    "patient_level_malignancy_probability": POLICY,
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def _case_data(case):
    prompt = build_report_prompt(**case["input"])
    data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    return prompt, data


def test_pack_has_twenty_cases_and_every_rule_has_provenance():
    cases = _load_cases()
    labels = {
        label
        for case in cases
        for key in ("semantic_expectations", "forbidden_interpretations")
        for label in case[key]
    }

    assert len(cases) == 20
    assert {case["id"] for case in cases} == EXPECTED_CASE_IDS
    assert labels == EXPECTATION_PROVENANCE.keys()
    assert all(
        sources and sources <= ALLOWED_PROVENANCE
        for sources in EXPECTATION_PROVENANCE.values()
    )
    assert all(
        "doctor_review_required" in case["semantic_expectations"]
        for case in cases
    )
    assert all(
        not any(
            term in expectation
            for term in ("order", "treatment", "biopsy", "surgery", "surveillance")
        )
        for case in cases
        for expectation in case["semantic_expectations"]
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_preserves_canonical_findings_and_frozen_selector(case):
    prompt, data = _case_data(case)
    findings = data["model_findings"]["findings"]
    selected = resolve_hermes_skills(data)

    assert all(
        item["name"] == "No finding" or item["name"] in FINDING_SKILL_MAP
        for item in findings
    )
    assert selected[0] == "medvision-evidence-fusion"
    assert selected[-2:] == [
        "medvision-safety-check",
        "medvision-disease-analysis",
    ]
    for item in findings:
        if item["name"] in FINDING_SKILL_MAP and item["decision"] == "POSITIVE":
            assert selected.count(FINDING_SKILL_MAP[item["name"]]) == 1
        elif item["name"] in FINDING_SKILL_MAP:
            assert FINDING_SKILL_MAP[item["name"]] not in selected
    assert "requires_doctor_review: true" in prompt


def test_module_is_progressive_without_new_skill_or_mapping():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    assert len(FINDING_SKILL_MAP) == 14
    assert "Pulmonary malignancy" not in FINDING_SKILL_MAP
    assert "Lung cancer" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-pulmonary-malignancy").exists()
    assert not (SKILL_ROOT / "medvision-lung-cancer").exists()
    assert "references/pulmonary_malignancy/PULMONARY_MALIGNANCY_POLICY.md" in content
    assert "references/pulmonary_malignancy/PULMONARY_MALIGNANCY_EVIDENCE.md" in content
    assert "references/pulmonary_malignancy/references.md" in content
    assert "canonical AI finding `Nodule/Mass`" in content
    assert "pathology or cytology from a pulmonary lesion" in content


def test_loading_trigger_and_non_trigger_boundaries_are_encoded():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    for trigger in (
        "trusted CT or human report",
        "`Other lesion` is externally characterized",
        "despite a CXR `No finding`",
        "explicitly raises malignancy concern",
    ):
        assert trigger in content
    assert "Do not load this module solely for generic `Calcification`" in content
    assert "`Pleural\nthickening`, `Lung Opacity`" in content


def test_module_files_and_sources_s1_through_s6_are_present():
    assert {path.name for path in MODULE_ROOT.iterdir()} == {
        "PULMONARY_MALIGNANCY_EVIDENCE.md",
        "PULMONARY_MALIGNANCY_POLICY.md",
        "references.md",
    }
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (MODULE_ROOT / "PULMONARY_MALIGNANCY_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert all(f"## S{number}" in references for number in range(1, 7))
    assert "Nodule/Mass != Lung Cancer" in evidence
    assert "Only if actual pathology/cytology evidence is supplied" in evidence
    assert "No hidden Brock, Mayo, Herder, or other score" in evidence


def test_all_bounded_disease_states_are_defined_by_the_supplied_module():
    evidence = (MODULE_ROOT / "PULMONARY_MALIGNANCY_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    states = {
        "PULMONARY_MALIGNANCY_CONCERN_SUPPORTED",
        "PULMONARY_MALIGNANCY_CONCERN_INDETERMINATE",
        "IMAGING_LESION_WITHOUT_SUFFICIENT_MALIGNANCY_CONTEXT",
        "PULMONARY_MALIGNANCY_CONCERN_CONFLICTED",
        "PULMONARY_MALIGNANCY_NOT_ESTABLISHED",
        "PATHOLOGY_CONFIRMED_PULMONARY_MALIGNANCY",
        "MALIGNANCY_ORIGIN_UNRESOLVED",
    }

    assert all(state in evidence for state in states)


def test_cxr_ct_and_guideline_scope_boundaries():
    assert "CXR Nodule/Mass only" in _case("PM01")["description"]
    assert "34 mm" in _case("PM07")["input"]["history"]
    assert "CT sàng lọc ung thư phổi" in _case("PM12")["input"]["history"]
    assert "phát hiện tình cờ trên CT" in _case("PM13")["input"]["history"]

    evidence = (MODULE_ROOT / "PULMONARY_MALIGNANCY_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert "Do not infer a precise CT-size category from a chest-radiograph bounding box" in evidence
    assert "apply Lung-RADS to nonscreening CT" in evidence
    assert "apply Fleischner CT tables directly to CXR AI output" in evidence


def test_temporal_growth_requires_comparable_same_lesion_data():
    case_growth = _case("PM03")
    case_unknown = _case("PM04")

    assert "cùng một nốt phổi" in case_growth["input"]["history"]
    assert "ngày, phép đo" in case_growth["input"]["history"]
    assert "không có phim trước" in case_unknown["input"]["history"]
    assert "growth_unknown" in case_unknown["semantic_expectations"]

    evidence = (MODULE_ROOT / "PULMONARY_MALIGNANCY_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert "the same lesion has been matched with sufficient confidence" in evidence
    assert "growth_status: unknown" in evidence


def test_calcification_and_multiplicity_do_not_create_benignity_or_metastases():
    case_calcification = _case("PM05")
    case_multiple = _case("PM11")

    assert [item["finding"] for item in case_calcification["input"]["results"]] == [
        "Nodule/Mass",
        "Calcification",
    ]
    assert "không có ct" in case_calcification["input"]["history"].lower()
    assert "ba nốt phổi riêng biệt" in case_multiple["input"]["history"]
    assert "metastases_from_multiplicity" in case_multiple["forbidden_interpretations"]


def test_no_finding_ct_nodule_preserves_both_modalities_without_image_conflict():
    prompt, data = _case_data(_case("PM09"))

    assert data["model_findings"]["findings"][0]["name"] == "No finding"
    assert data["no_finding_policy"]["policy_state"] == (
        "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"
    )
    assert "CT ngực sau đó" in prompt
    assert "no_finding_contradiction_without_positive_target" in (
        _case("PM09")["forbidden_interpretations"]
    )


def test_other_lesion_external_characterization_does_not_select_nodule_skill():
    _, data = _case_data(_case("PM10"))
    selected = resolve_hermes_skills(data)

    assert "medvision-other-lesion" in selected
    assert "medvision-nodule-mass" not in selected
    assert data["model_findings"]["findings"][1]["decision"] == "NEGATIVE"


def test_pathology_confirmation_origin_histology_and_conflict_boundaries():
    assert "không chẩn đoán được" in _case("PM15")["input"]["history"]
    assert "sample_correspondence_uncertain" in _case("PM16")[
        "semantic_expectations"
    ]
    assert "malignancy_origin_unresolved" in _case("PM17")[
        "semantic_expectations"
    ]
    assert "ung thư biểu mô tuyến nguyên phát của phổi" in _case("PM18")[
        "input"
    ]["history"]
    assert "di căn từ đại trực tràng" in _case("PM19")["input"]["history"]


def test_pneumonia_and_malignancy_remain_separate_without_forced_winner():
    case = _case("PM14")
    findings = [item["finding"] for item in case["input"]["results"]]

    assert findings == ["Nodule/Mass", "Consolidation"]
    assert "pneumonia_hypothesis_preserved" in case["semantic_expectations"]
    assert "shared_imaging_evidence_not_double_counted" in (
        case["semantic_expectations"]
    )
    assert "forced_pneumonia_malignancy_winner" in (
        case["forbidden_interpretations"]
    )


def test_score_semantics_and_action_boundary_are_explicit():
    case = _case("PM20")
    evidence = (MODULE_ROOT / "PULMONARY_MALIGNANCY_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert case["input"]["results"][0]["score"] == 0.92
    assert "ninety_two_percent_cancer_probability" in (
        case["forbidden_interpretations"]
    )
    assert "92% probability of lung cancer" in evidence
    for prohibited in (
        "order CT/PET",
        "recommend biopsy",
        "schedule bronchoscopy",
        "recommend surgery",
        "make surveillance intervals",
    ):
        assert prohibited in evidence
