"""Provider-independent validation for ILD/fibrotic ILD disease analysis."""

import json
from pathlib import Path

import pytest

from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_ild_fibrotic"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = (
    SKILL_ROOT / "medvision-disease-analysis" / "references" / "ild_fibrotic"
)
EXPECTED_CASE_IDS = {f"ILD{number:02d}" for number in range(1, 31)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "S5", "MEDVISION_SYSTEM_POLICY"}
POLICY = {"MEDVISION_SYSTEM_POLICY"}
PROVENANCE = {}


def _register(sources, labels):
    for label in labels.split():
        assert label not in PROVENANCE
        PROVENANCE[label] = set(sources)


_register(
    {"S1", "S2", "S5"} | POLICY,
    """
    ild_hypothesis_supported_bounded fibrotic_ild_hypothesis_bounded
    fibrotic_ild_hypothesis_supported fibrotic_scarring_evidence_preserved
    named_ild_subtype_inferred hp_or_ctd_ild_inferred
    two_independent_disease_confirmations same_process_relation_unknown
    both_upstream_findings_preserved overlap_deduplicated
    """,
)
_register(
    {"S1", "S2", "S5"} | POLICY,
    """
    hrct_pattern_not_assessable hrct_pattern_uip hrct_pattern_probable_uip
    hrct_pattern_indeterminate_for_uip hrct_pattern_alternative_diagnosis
    exact_hrct_category_preserved hrct_provenance_preserved
    supplied_alternative_pattern_preserved missing_hrct_explicit
    honeycombing_invented_from_cxr traction_bronchiectasis_invented_from_cxr
    uip_category_inferred_from_cxr uip_inferred_from_cxr
    probable_uip_silently_promoted_to_uip hrct_category_changed
    uip_inferred hrct_pattern_invented_from_histology
    """,
)
_register(
    {"S1", "S2"} | POLICY,
    """
    ipf_not_established ild_etiology_unresolved ipf_concern_supported_as_supplied
    ipf_trajectory_preserved trusted_mdd_ipf_diagnosis_preserved
    mdd_provenance_preserved histologic_uip_preserved uip_automatically_ipf
    histologic_uip_automatically_ipf automatic_ipf final_ipf_diagnosis
    ipf_confirmed ipf_inferred ipf_inferred_from_fibrosis
    uip_forces_ipf alternative_causes_assumed_excluded idiopathic_relabeling
    ipf_relabeling ipf_forced_despite_exposure additional_certainty_fabricated
    mdd_diagnosis_invented mdd_source_erased ipf_diagnosis_erased
    """,
)
_register(
    {"S3"} | POLICY,
    """
    hp_exposure_preserved fibrotic_hp_concern_supported
    fibrotic_hp_not_established multiple_hp_domains_preserved
    serum_igg_sensitization_preserved hp_confirmed_from_exposure_alone
    hp_confirmed_from_serum_igg causal_exposure_claimed causal_exposure_proven
    causality_inferred single_domain_hp_reasoning autonomous_exposure_challenge
    """,
)
_register(
    {"S4"} | POLICY,
    """
    ana_preserved_as_incomplete_autoimmune_evidence ctd_ild_concern_supported
    ctd_ild_not_established ctd_provenance_preserved
    established_ctd_provenance_preserved objective_ild_preserved
    ctd_ild_confirmed_from_ana_alone ctd_subtype_invented
    new_ctd_subtype_invented ctd_context_erased
    """,
)
_register(
    {"S1"} | POLICY,
    """
    ppf_not_assessable ppf_criteria_not_met ppf_criteria_met
    ppf_not_applicable_to_ipf progression_unknown severity_not_progression
    physiology_domain_present symptom_domain_present radiology_domain_present
    one_ppf_domain_only fvc_dlco_count_as_one_domain time_window_invalid
    comparability_insufficient ppf_from_single_study ppf_from_severity
    ppf_inferred_from_single_finding ppf_met_from_one_domain
    fvc_called_multiple_domains fvc_dlco_counted_as_two_domains
    ppf_met_from_physiology_alone hidden_third_domain third_domain_required
    symptom_domain_required physiology_domain_required relative_decline_substituted
    outside_window_silently_accepted radiological_progression_assumed_valid
    ppf_criteria_applied_to_ipf treatment_inferred_from_ppf
    additional_progression_invented missing_prior_called_stable
    radiology_source_erased
    """,
)
_register(
    {"S1", "S5"} | POLICY,
    """
    no_finding_cxr_preserved hrct_fibrotic_ild_preserved
    hrct_ild_excluded_by_no_finding cxr_result_erased
    pulmonary_ossification_inferred pneumoconiosis_or_asbestos_disease_inferred
    healed_granulomatous_disease_inferred specific_etiology_invented
    """,
)
_register(
    {"S1"} | POLICY,
    """
    pneumonia_hypothesis_preserved heart_failure_hypothesis_preserved
    ild_hypothesis_preserved acute_opacity_not_fibrotic_progression
    acute_edema_not_fibrotic_progression acute_infection_counted_as_ppf
    edema_counted_as_ppf forced_ild_pneumonia_winner forced_hf_ild_winner
    shared_evidence_double_counted shared_dyspnea_opacity_double_counted
    """,
)
_register(
    POLICY,
    """
    doctor_review_required model_scores_preserved score_not_disease_probability
    score_not_progression_probability ninety_one_percent_ild_probability
    eighty_eight_percent_ipf_probability progression_probability_from_scores
    no_finding_contradiction_without_positive_target autonomous_antifibrotic
    autonomous_bal_or_biopsy autonomous_immunosuppression
    autonomous_steroid_or_immunosuppression autonomous_treatment
    """,
)


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


def _evaluate_ppf(evidence):
    prerequisites = (
        evidence["ild_other_than_ipf"] is True
        and evidence["radiological_fibrosis"] is True
        and evidence["within_one_year"] is True
        and evidence["comparable"] is True
        and evidence["alternative_explanation_present"] is False
    )
    if not prerequisites:
        return "PPF_NOT_ASSESSABLE", set()

    physiology = (
        (evidence["fvc_absolute_decline_points"] or 0) >= 5
        or (evidence["dlco_hb_absolute_decline_points"] or 0) >= 10
    )
    domains = {
        name
        for name, present in (
            ("SYMPTOMS", evidence["symptoms_worsened"] is True),
            ("PHYSIOLOGY", physiology),
            ("RADIOLOGY", evidence["radiological_progression"] is True),
        )
        if present
    }
    state = "PPF_CRITERIA_MET" if len(domains) >= 2 else "PPF_CRITERIA_NOT_MET"
    return state, domains


def test_pack_has_thirty_cases_and_every_rule_has_provenance():
    cases = _load_cases()
    labels = {
        label
        for case in cases
        for key in ("semantic_expectations", "forbidden_interpretations")
        for label in case[key]
    }

    assert len(cases) == 30
    assert {case["id"] for case in cases} == EXPECTED_CASE_IDS
    assert labels == PROVENANCE.keys()
    assert all(
        sources and sources <= ALLOWED_PROVENANCE
        for sources in PROVENANCE.values()
    )
    assert all(
        "doctor_review_required" in case["semantic_expectations"]
        for case in cases
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
    assert "IPF" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-ild-disease").exists()
    assert not (SKILL_ROOT / "medvision-ipf").exists()
    assert "references/ild_fibrotic/ILD_FIBROTIC_POLICY.md" in content
    assert "references/ild_fibrotic/ILD_FIBROTIC_EVIDENCE.md" in content
    assert "references/ild_fibrotic/references.md" in content


def test_loading_triggers_and_generic_non_trigger_boundary_are_encoded():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    for trigger in (
        "canonical AI finding `ILD` or `Pulmonary fibrosis`",
        "trusted HRCT or report describes fibrotic ILD",
        "traction bronchiectasis or bronchiolectasis",
        "multidisciplinary discussion raises known or suspected ILD",
        "serial PFT or HRCT data",
    ):
        assert trigger in content
    assert "Do not load this module solely for generic `Lung Opacity`" in content
    assert "`Infiltration`,\n`Calcification`" in content


def test_module_files_sources_and_all_states_are_present():
    assert {path.name for path in MODULE_ROOT.iterdir()} == {
        "ILD_FIBROTIC_EVIDENCE.md",
        "ILD_FIBROTIC_POLICY.md",
        "references.md",
    }
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (MODULE_ROOT / "ILD_FIBROTIC_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert all(f"## S{number}" in references for number in range(1, 6))
    states = {
        "ILD_HYPOTHESIS_SUPPORTED",
        "FIBROTIC_ILD_HYPOTHESIS_SUPPORTED",
        "ILD_HYPOTHESIS_INDETERMINATE",
        "ILD_HYPOTHESIS_CONFLICTED",
        "ILD_HYPOTHESIS_NOT_ESTABLISHED",
        "HRCT_PATTERN_UIP",
        "HRCT_PATTERN_PROBABLE_UIP",
        "HRCT_PATTERN_INDETERMINATE_FOR_UIP",
        "HRCT_PATTERN_ALTERNATIVE_DIAGNOSIS",
        "HRCT_PATTERN_NOT_ASSESSABLE",
        "IPF_CONCERN_SUPPORTED",
        "IPF_NOT_ESTABLISHED",
        "ILD_ETIOLOGY_UNRESOLVED",
        "FIBROTIC_HP_CONCERN_SUPPORTED",
        "CTD_ILD_CONCERN_SUPPORTED",
        "PPF_CRITERIA_MET",
        "PPF_CRITERIA_NOT_MET",
        "PPF_NOT_ASSESSABLE",
    }
    assert all(state in evidence for state in states)


def test_cxr_cannot_determine_hrct_morphology_or_category():
    evidence = (MODULE_ROOT / "ILD_FIBROTIC_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "CXR != HRCT pattern classification" in evidence
    assert "honeycombing" in _case("ILD04")["forbidden_interpretations"][0]
    assert "traction_bronchiectasis_invented_from_cxr" in _case("ILD04")[
        "forbidden_interpretations"
    ]
    assert "HRCT_PATTERN_NOT_ASSESSABLE" in evidence


def test_explicit_hrct_categories_are_preserved_without_ipf_conversion():
    expected = {
        "ILD05": "hrct_pattern_uip",
        "ILD06": "hrct_pattern_probable_uip",
        "ILD07": "hrct_pattern_indeterminate_for_uip",
        "ILD08": "hrct_pattern_alternative_diagnosis",
    }

    for case_id, label in expected.items():
        assert label in _case(case_id)["semantic_expectations"]
        assert "HRCT" in _case(case_id)["input"]["history"]
    assert "uip_automatically_ipf" in _case("ILD05")[
        "forbidden_interpretations"
    ]


def test_ipf_requires_alternative_cause_assessment_and_preserves_mdd_provenance():
    assert "đánh giá nguyên nhân thay thế chưa đầy đủ" in _case("ILD05")[
        "input"
    ]["history"]
    assert "ipf_not_established" in _case("ILD28")["semantic_expectations"]
    assert "trusted_mdd_ipf_diagnosis_preserved" in _case("ILD29")[
        "semantic_expectations"
    ]
    assert "nguồn và ngày được cung cấp" in _case("ILD29")["input"]["history"]


def test_ctd_ild_requires_established_ctd_and_objective_ild():
    assert "ANA dương tính đơn độc" in _case("ILD11")["input"]["laboratory"]
    assert "ctd_ild_not_established" in _case("ILD11")["semantic_expectations"]
    assert "xơ cứng bì hệ thống" in _case("ILD12")["input"]["history"].lower()
    assert "ctd_ild_concern_supported" in _case("ILD12")[
        "semantic_expectations"
    ]


def test_hp_requires_multiple_domains_and_serum_igg_is_not_causal():
    assert "hp_confirmed_from_exposure_alone" in _case("ILD13")[
        "forbidden_interpretations"
    ]
    assert "multiple_hp_domains_preserved" in _case("ILD14")[
        "semantic_expectations"
    ]
    assert "Serum IgG" in _case("ILD15")["input"]["laboratory"]
    assert "hp_confirmed_from_serum_igg" in _case("ILD15")[
        "forbidden_interpretations"
    ]


def test_no_finding_and_calcification_boundaries():
    _, no_finding_data = _case_data(_case("ILD16"))

    assert no_finding_data["no_finding_policy"]["policy_state"] == (
        "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"
    )
    assert "hrct_ild_excluded_by_no_finding" in _case("ILD16")[
        "forbidden_interpretations"
    ]
    assert [item["finding"] for item in _case("ILD17")["input"]["results"]] == [
        "Pulmonary fibrosis",
        "Calcification",
    ]
    assert "same_process_relation_unknown" in _case("ILD17")[
        "semantic_expectations"
    ]


@pytest.mark.parametrize(
    ("case_id", "expected_state", "expected_domains"),
    [
        ("ILD18", "PPF_NOT_ASSESSABLE", set()),
        ("ILD19", "PPF_CRITERIA_NOT_MET", {"PHYSIOLOGY"}),
        ("ILD20", "PPF_CRITERIA_NOT_MET", {"PHYSIOLOGY"}),
        ("ILD21", "PPF_CRITERIA_MET", {"SYMPTOMS", "PHYSIOLOGY"}),
        ("ILD22", "PPF_CRITERIA_MET", {"PHYSIOLOGY", "RADIOLOGY"}),
        ("ILD23", "PPF_CRITERIA_MET", {"SYMPTOMS", "RADIOLOGY"}),
        ("ILD24", "PPF_NOT_ASSESSABLE", set()),
        ("ILD25", "PPF_NOT_ASSESSABLE", set()),
        ("ILD26", "PPF_NOT_ASSESSABLE", set()),
        ("ILD27", "PPF_NOT_ASSESSABLE", set()),
    ],
)
def test_ppf_structured_two_of_three_domain_rules(
    case_id, expected_state, expected_domains
):
    state, domains = _evaluate_ppf(_case(case_id)["ppf_evidence"])

    assert state == expected_state
    assert domains == expected_domains


def test_fvc_and_dlco_are_one_physiology_domain():
    state, domains = _evaluate_ppf(_case("ILD20")["ppf_evidence"])

    assert state == "PPF_CRITERIA_NOT_MET"
    assert domains == {"PHYSIOLOGY"}
    assert "fvc_dlco_count_as_one_domain" in _case("ILD20")[
        "semantic_expectations"
    ]


def test_ppf_thresholds_are_absolute_and_exactly_sourced():
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (MODULE_ROOT / "ILD_FIBROTIC_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "absolute FVC decline >=5% predicted within 1 year" in references
    assert "absolute Hb-corrected DLCO decline >=10% predicted within 1 year" in references
    assert "Do not substitute relative decline" in evidence


def test_pneumonia_and_hf_alternatives_block_automatic_ppf_counting():
    assert _case("ILD26")["ppf_evidence"]["alternative_explanation_present"] is True
    assert "pneumonia_hypothesis_preserved" in _case("ILD26")[
        "semantic_expectations"
    ]
    assert _case("ILD27")["ppf_evidence"]["alternative_explanation_present"] is True
    assert "heart_failure_hypothesis_preserved" in _case("ILD27")[
        "semantic_expectations"
    ]


def test_cross_disease_selectors_preserve_findings_without_forced_winner():
    _, pneumonia_data = _case_data(_case("ILD26"))
    _, hf_data = _case_data(_case("ILD27"))

    pneumonia_skills = resolve_hermes_skills(pneumonia_data)
    hf_skills = resolve_hermes_skills(hf_data)
    assert "medvision-pulmonary-fibrosis" in pneumonia_skills
    assert "medvision-consolidation" in pneumonia_skills
    assert "medvision-ild" in hf_skills
    assert "medvision-cardiomegaly" in hf_skills
    assert "medvision-lung-opacity" in hf_skills
    assert "forced_ild_pneumonia_winner" in _case("ILD26")[
        "forbidden_interpretations"
    ]
    assert "forced_hf_ild_winner" in _case("ILD27")[
        "forbidden_interpretations"
    ]


def test_score_semantics_and_action_boundary_are_explicit():
    case = _case("ILD30")
    evidence = (MODULE_ROOT / "ILD_FIBROTIC_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert [item["score"] for item in case["input"]["results"]] == [0.91, 0.88]
    assert "score_not_disease_probability" in case["semantic_expectations"]
    assert "Never convert image-model scores into disease or progression probabilities" in evidence
    for prohibited in (
        "prescribe antifibrotics",
        "steroids/immunosuppression",
        "oxygen",
        "order HRCT/PFT/BAL/biopsy/transplant evaluation",
    ):
        assert prohibited in evidence
