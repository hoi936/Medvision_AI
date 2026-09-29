"""Provider-independent validation for acute aortic syndrome disease analysis."""

import json
from pathlib import Path

import pytest

from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_acute_aortic_syndrome"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = (
    SKILL_ROOT
    / "medvision-disease-analysis"
    / "references"
    / "acute_aortic_syndrome"
)
EXPECTED_CASE_IDS = {f"AAS{number:02d}" for number in range(1, 21)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "MEDVISION_SYSTEM_POLICY"}
POLICY = {"MEDVISION_SYSTEM_POLICY"}

EXPECTATION_PROVENANCE = {
    "aortic_finding_without_acute_syndrome_support": {"S2", "S3", "S4"} | POLICY,
    "aortic_enlargement_preserved_as_cxr_evidence": {"S3", "S4"} | POLICY,
    "missing_acute_features_explicit": {"S1", "S2"} | POLICY,
    "doctor_review_required": POLICY,
    "aneurysm_from_aortic_enlargement": {"S2", "S3", "S4"},
    "dissection_or_aas_confirmed_from_cxr": {"S2", "S3", "S4"},
    "autonomous_imaging_or_treatment": {"S1", "S2"} | POLICY,
    "acute_aortic_syndrome_concern_supported": {"S1", "S2"} | POLICY,
    "high_priority_clinical_review": {"S1", "S2"} | POLICY,
    "cxr_and_clinical_provenance_preserved": {"S1", "S2", "S3", "S4"} | POLICY,
    "dissection_confirmed_without_definitive_imaging": {"S1", "S2"},
    "aas_subtype_invented": {"S1", "S2"} | POLICY,
    "autonomous_cta_or_transfer": {"S1", "S2"} | POLICY,
    "chronic_aortic_risk_preserved": {"S1", "S2"} | POLICY,
    "acute_aas_not_established": {"S1", "S2"} | POLICY,
    "chronic_aneurysm_equated_with_acute_dissection": {"S1", "S2"},
    "acute_syndrome_promoted_without_support": {"S1", "S2"} | POLICY,
    "autonomous_surveillance_or_surgery": {"S1", "S2"} | POLICY,
    "no_finding_not_aas_exclusion": {"S2", "S3", "S4"} | POLICY,
    "no_false_image_contradiction_from_symptoms": {"S3", "S4"} | POLICY,
    "aas_excluded_by_no_finding": {"S2", "S3", "S4"},
    "no_finding_contradiction_without_positive_target": POLICY,
    "subtype_from_symptoms": {"S1", "S2"} | POLICY,
    "no_finding_cxr_preserved": {"S3", "S4"} | POLICY,
    "definitive_aortic_imaging_confirmed_aas": {"S1", "S2"} | POLICY,
    "explicit_type_b_subtype_preserved": {"S1", "S2"} | POLICY,
    "cta_erased_by_no_finding": {"S2", "S3"} | POLICY,
    "subtype_relabelled": {"S1", "S2"} | POLICY,
    "autonomous_surgery_or_transfer": {"S1", "S2"} | POLICY,
    "acute_aortic_syndrome_concern_indeterminate": {"S1", "S2"} | POLICY,
    "widened_mediastinum_preserved_as_cxr_clue": {"S2", "S3"} | POLICY,
    "definitive_imaging_missing": {"S1", "S2"} | POLICY,
    "aas_confirmed_from_widened_mediastinum": {"S2", "S3"},
    "rupture_inferred": {"S1", "S2"} | POLICY,
    "subtype_inferred": {"S1", "S2"} | POLICY,
    "acute_aortic_syndrome_not_established": {"S1", "S2"} | POLICY,
    "pleural_effusion_preserved": {"S1", "S2"} | POLICY,
    "acute_context_missing": {"S1", "S2"} | POLICY,
    "aortic_rupture_from_pleural_effusion": {"S1", "S2"} | POLICY,
    "hemothorax_inferred": {"S1", "S2"} | POLICY,
    "aas_confirmed": {"S1", "S2"} | POLICY,
    "acute_dissection_from_chronic_risk": {"S1", "S2"},
    "hidden_risk_score": {"S2"} | POLICY,
    "aas_subtype_unresolved": {"S1", "S2"} | POLICY,
    "specific_subtype_from_symptoms": {"S1", "S2"},
    "definitive_aas_confirmation_without_imaging": {"S1", "S2"},
    "autonomous_procedure_or_disposition": {"S1", "S2"} | POLICY,
    "low_d_dimer_preserved_as_nonspecific": {"S2"} | POLICY,
    "risk_context_incomplete": {"S2"} | POLICY,
    "aas_ruled_out_by_low_d_dimer_alone": {"S2"},
    "hidden_d_dimer_ruleout_algorithm": {"S2"} | POLICY,
    "high_d_dimer_preserved_as_nonspecific": {"S2"} | POLICY,
    "aas_confirmed_by_high_d_dimer": {"S2"},
    "biomarker_called_diagnostic": {"S2"},
    "external_risk_score_provenance_preserved": {"S2"} | POLICY,
    "missing_score_variables_remain_missing": {"S2"} | POLICY,
    "aad_rs_recomputed": {"S2"} | POLICY,
    "score_relabelled_as_medvision": {"S2"} | POLICY,
    "missing_variables_inferred": {"S2"} | POLICY,
    "explicit_type_a_subtype_preserved": {"S1", "S2"} | POLICY,
    "cta_provenance_preserved": {"S1", "S2"} | POLICY,
    "subtype_invented_or_changed": {"S1", "S2"} | POLICY,
    "autonomous_anti_impulse_treatment": {"S1", "S2"} | POLICY,
    "explicit_imh_subtype_preserved": {"S1", "S2"} | POLICY,
    "mri_provenance_preserved": {"S1", "S2"} | POLICY,
    "imh_silently_relabelled_dissection": {"S1", "S2"} | POLICY,
    "additional_subtype_invented": {"S1", "S2"} | POLICY,
    "autonomous_treatment_or_procedure": {"S1", "S2"} | POLICY,
    "dissection_subtype_invented": {"S1", "S2"} | POLICY,
    "imh_or_pau_invented": {"S1", "S2"} | POLICY,
    "autonomous_management": {"S1", "S2"} | POLICY,
    "malperfusion_concern": {"S1", "S2"} | POLICY,
    "supplied_vascular_territories_preserved": {"S1", "S2"} | POLICY,
    "unsupplied_branch_territory_invented": {"S1", "S2"} | POLICY,
    "malperfusion_from_pain_alone": {"S1", "S2"},
    "autonomous_endovascular_or_surgical_procedure": {"S1", "S2"} | POLICY,
    "acute_aortic_syndrome_concern_conflicted_or_not_established": {"S1", "S2"} | POLICY,
    "both_modalities_and_timing_preserved": {"S1", "S2", "S3"} | POLICY,
    "definitive_imaging_stronger_for_aas_diagnosis": {"S1", "S2", "S3"},
    "earlier_cxr_silently_preferred": {"S1", "S2", "S3"},
    "later_cta_erased": {"S1", "S2"} | POLICY,
    "pneumothorax_pneumonia_hf_hypotheses_preserved": {"S1", "S2"} | POLICY,
    "other_chest_pain_hypotheses_preserved": {"S1", "S2"} | POLICY,
    "shared_evidence_not_double_counted": POLICY,
    "forced_aas_winner": {"S1", "S2"} | POLICY,
    "competing_urgent_evidence_suppressed": {"S1", "S2"} | POLICY,
    "single_etiology_for_all_findings": POLICY,
    "model_score_preserved": POLICY,
    "score_not_aas_probability": POLICY,
    "ninety_four_percent_aas_probability": POLICY,
    "aneurysm_probability_from_score": POLICY,
    "dissection_probability_from_score": POLICY,
    "missing_evidence_explicit": POLICY,
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
            for term in (
                "autonomous",
                "treatment",
                "procedure",
                "surgery",
                "transfer",
                "disposition",
            )
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
    assert "Acute aortic syndrome" not in FINDING_SKILL_MAP
    assert "Aortic dissection" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-acute-aortic-syndrome").exists()
    assert not (SKILL_ROOT / "medvision-aortic-dissection").exists()
    assert "references/acute_aortic_syndrome/ACUTE_AORTIC_SYNDROME_POLICY.md" in content
    assert "references/acute_aortic_syndrome/ACUTE_AORTIC_SYNDROME_EVIDENCE.md" in content
    assert "references/acute_aortic_syndrome/references.md" in content


def test_loading_triggers_and_unrelated_finding_boundary_are_encoded():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    for trigger in (
        "canonical AI finding `Aortic enlargement`",
        "widened mediastinum or abnormal aortic contour",
        "abrupt severe chest, back, or abdominal pain",
        "significant inter-arm blood-pressure differential",
        "known thoracic aneurysm",
        "definitive imaging or an explicit report",
    ):
        assert trigger in content
    assert "Do not load this module for unrelated findings alone" in content


def test_module_files_sources_and_all_bounded_states_are_present():
    assert {path.name for path in MODULE_ROOT.iterdir()} == {
        "ACUTE_AORTIC_SYNDROME_EVIDENCE.md",
        "ACUTE_AORTIC_SYNDROME_POLICY.md",
        "references.md",
    }
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (MODULE_ROOT / "ACUTE_AORTIC_SYNDROME_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert all(f"## S{number}" in references for number in range(1, 5))
    states = {
        "ACUTE_AORTIC_SYNDROME_CONCERN_SUPPORTED",
        "ACUTE_AORTIC_SYNDROME_CONCERN_INDETERMINATE",
        "AORTIC_FINDING_WITHOUT_ACUTE_SYNDROME_SUPPORT",
        "ACUTE_AORTIC_SYNDROME_CONCERN_CONFLICTED",
        "ACUTE_AORTIC_SYNDROME_NOT_ESTABLISHED",
        "DEFINITIVE_AORTIC_IMAGING_CONFIRMED_AAS",
        "AAS_SUBTYPE_UNRESOLVED",
        "MALPERFUSION_CONCERN",
    }
    assert all(state in evidence for state in states)


def test_cxr_finding_is_separated_from_aneurysm_dissection_and_aas():
    evidence = (MODULE_ROOT / "ACUTE_AORTIC_SYNDROME_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "Aortic enlargement != aneurysm" in evidence
    assert "Aortic enlargement != dissection" in evidence
    assert "Aortic enlargement != AAS" in evidence
    assert "Plain chest X-ray is not sufficiently sensitive or specific" in evidence
    assert "aortic_finding_without_acute_syndrome_support" in (
        _case("AAS01")["semantic_expectations"]
    )


def test_no_finding_does_not_exclude_aas_or_create_image_contradiction():
    _, data = _case_data(_case("AAS04"))

    assert data["model_findings"]["findings"][0]["name"] == "No finding"
    assert data["no_finding_policy"]["policy_state"] == (
        "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"
    )
    assert "no_finding_not_aas_exclusion" in _case("AAS04")[
        "semantic_expectations"
    ]
    assert "no_finding_contradiction_without_positive_target" in _case("AAS04")[
        "forbidden_interpretations"
    ]


def test_definitive_imaging_confirmation_and_subtype_boundaries():
    assert "type B" in _case("AAS05")["input"]["history"]
    assert "type A" in _case("AAS13")["input"]["history"]
    assert "tụ máu trong thành" in _case("AAS14")["input"]["history"]
    assert "aas_subtype_unresolved" in _case("AAS15")["semantic_expectations"]

    evidence = (MODULE_ROOT / "ACUTE_AORTIC_SYNDROME_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert "Only definitive aortic imaging or explicit definitive source evidence" in evidence
    assert "Do not infer subtype if the report only says" in evidence


def test_chronic_aneurysm_and_aortopathy_do_not_become_acute_dissection():
    assert "ổn định" in _case("AAS03")["input"]["history"]
    assert "chronic_aneurysm_equated_with_acute_dissection" in _case("AAS03")[
        "forbidden_interpretations"
    ]
    assert "bệnh lý động mạch chủ di truyền" in _case("AAS08")["input"]["history"]
    assert "acute_aas_not_established" in _case("AAS08")["semantic_expectations"]


def test_d_dimer_is_nondiagnostic_and_no_ruleout_algorithm_is_implemented():
    low_case = _case("AAS10")
    high_case = _case("AAS11")
    evidence = (MODULE_ROOT / "ACUTE_AORTIC_SYNDROME_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "D-dimer thấp" in low_case["input"]["laboratory"]
    assert "D-dimer tăng" in high_case["input"]["laboratory"]
    assert "low D-dimer alone != AAS excluded" in evidence
    assert "high D-dimer alone != AAS confirmed" in evidence
    assert "No universal MedVision AAS rule-out algorithm" in evidence


def test_external_risk_score_keeps_provenance_and_missing_variables():
    case = _case("AAS12")

    assert "Bác sĩ cấp cứu cung cấp AAD-RS = 2" in case["input"]["history"]
    assert "các biến thành phần không được cung cấp đầy đủ" in (
        case["input"]["history"]
    )
    assert "aad_rs_recomputed" in case["forbidden_interpretations"]


def test_malperfusion_requires_supplied_territory_evidence():
    supported = _case("AAS16")
    pain_only = _case("AAS09")

    assert "malperfusion_concern" in supported["semantic_expectations"]
    assert "chi phải lạnh và mất mạch" in supported["input"]["history"]
    assert "malperfusion_concern" not in pain_only["semantic_expectations"]

    evidence = (MODULE_ROOT / "ACUTE_AORTIC_SYNDROME_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert "Do not infer branch-vessel malperfusion from pain alone" in evidence


def test_cross_disease_case_selects_all_findings_once_without_clinical_priority():
    _, data = _case_data(_case("AAS18"))
    selected = resolve_hermes_skills(data)
    finding_skills = [
        "medvision-aortic-enlargement",
        "medvision-pneumothorax",
        "medvision-consolidation",
        "medvision-cardiomegaly",
    ]

    assert selected == [
        "medvision-evidence-fusion",
        *finding_skills,
        "medvision-safety-check",
        "medvision-disease-analysis",
    ]
    assert all(selected.count(skill) == 1 for skill in finding_skills)
    assert "forced_aas_winner" in _case("AAS18")["forbidden_interpretations"]


def test_score_semantics_missing_data_and_action_boundary_are_explicit():
    case = _case("AAS19")
    evidence = (MODULE_ROOT / "ACUTE_AORTIC_SYNDROME_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert case["input"]["results"][0]["score"] == 0.94
    assert "ninety_four_percent_aas_probability" in (
        case["forbidden_interpretations"]
    )
    assert "Convert AI score into AAS probability" in evidence
    for prohibited in (
        "order CTA/TEE/MRI",
        "initiate antihypertensive/anti-impulse therapy",
        "transfer to surgery",
        "recommend operative/endovascular repair",
        "start analgesia",
        "make disposition decisions",
    ):
        assert prohibited in evidence
