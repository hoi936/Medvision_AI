"""Provider-independent validation for TB/chronic mycobacterial analysis."""

import json
from pathlib import Path

import pytest

from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_tb_chronic_mycobacterial"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = (
    SKILL_ROOT
    / "medvision-disease-analysis"
    / "references"
    / "tb_chronic_mycobacterial"
)
EXPECTED_CASE_IDS = {f"TB{number:02d}" for number in range(1, 35)}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "S7", "MEDVISION_SYSTEM_POLICY"
}
POLICY = {"MEDVISION_SYSTEM_POLICY"}
PROVENANCE = {}


def _register(sources, labels):
    for label in labels.split():
        assert label not in PROVENANCE
        PROVENANCE[label] = set(sources)


_register(
    {"S4", "S5"} | POLICY,
    """
    calcification_preserved calcified_nodes_preserved pulmonary_fibrosis_preserved
    infiltration_remains_nonspecific ct_cavity_provenance_preserved
    tree_in_bud_and_context_preserved no_finding_cxr_preserved
    active_tb_from_calcification prior_or_healed_tb_from_calcification
    granulomatous_disease_inferred prior_tb_from_fibrosis active_tb_from_fibrosis
    recurrence_inferred active_tb_from_upper_lobe_opacity tb_confirmation_from_imaging
    chronicity_inferred cavity_confirms_tb tree_in_bud_confirms_tb
    active_tb_from_calcified_nodes prior_or_healed_tb_inferred
    tb_excluded_by_normal_cxr microbiology_erased_by_no_finding ct_findings_erased
    """,
)
_register(
    {"S1", "S3", "S4", "S5"} | POLICY,
    """
    igra_sensitization_evidence_preserved negative_igra_preserved
    tb_exposure_preserved_as_risk_context immunocompromised_context_preserved
    active_tb_from_positive_igra active_tb_excluded_by_negative_igra
    active_tb_from_exposure tb_probability_from_exposure infectiousness_inferred
    tb_concern_erased hidden_tb_probability
    """,
)
_register(
    {"S1", "S2", "S4", "S5"} | POLICY,
    """
    afb_detected_species_unresolved afb_smear_provenance_preserved
    negative_afb_smear_preserved tb_not_excluded_by_smear ntm_remains_possible
    microbiologically_confirmed_tb naat_provenance_preserved culture_provenance_preserved
    culture_confirmation_preserved discordant_test_timing_preserved
    microbiology_conflict_preserved pulmonary_site_supported_by_sputum_specimen
    pulmonary_site_supported_by_bal_specimen pleural_site_supported_by_specimen
    tb_site_unresolved missing_specimen_site_explicit
    mtb_confirmed_from_afb_smear tb_forced_over_ntm smear_grade_as_tb_probability
    tb_excluded_by_negative_smear microbiologic_confirmation_invented
    untested_drug_resistance_inferred untested_resistance_inferred
    drug_resistance_inferred negative_naat_universal_exclusion
    positive_culture_erased negative_naat_called_species_identification
    mtb_confirmed ntm_confirmed additional_site_inferred other_site_inferred
    pulmonary_site_inferred pleural_site_inferred specimen_invented
    """,
)
_register(
    {"S1", "S5", "S6"} | POLICY,
    """
    pleural_tb_concern_indeterminate pleural_tb_concern_supported
    pleural_tb_not_confirmed ada_provenance_preserved
    ada_and_epidemiology_preserved negative_pleural_naat_preserved
    pleural_tb_confirmed_from_ada universal_ada_cutoff_invented
    pleural_tb_excluded_by_negative_naat autonomous_pleural_biopsy
    """,
)
_register(
    {"S1", "S5"} | POLICY,
    """
    granulomatous_pathology_preserved pathology_supported_tb
    pathology_and_naat_provenance_preserved chronic_infection_etiology_unresolved
    tb_not_confirmed granuloma_equated_with_tb
    ntm_fungal_inflammatory_alternatives_erased
    ntm_or_fungal_alternatives_erased pathology_erased
    """,
)
_register(
    {"S7"} | POLICY,
    """
    ntm_pulmonary_disease_not_established ntm_pulmonary_disease_concern_supported
    ntm_species_and_single_culture_preserved same_ntm_species_repeated_cultures_preserved
    clinical_radiographic_criteria_preserved afb_and_ntm_provenance_preserved
    tb_ntm_both_unresolved ntm_disease_from_single_sputum_culture
    mtb_relabeling ntm_relabelled_as_tb ntm_relabelled_as_mtb
    afb_relabelled_as_tb drug_susceptibility_invented
    """,
)
_register(
    {"S1", "S4", "S5"} | POLICY,
    """
    pulmonary_tb_concern_supported pulmonary_tb_concern_indeterminate
    pulmonary_tb_not_established tb_not_established microbiology_missing_explicit
    tb_module_nontrigger_boundary symptom_cluster_confirms_tb
    mtb_species_inferred site_or_activity_confirmed missing_microbiology_invented
    """,
)
_register(
    {"S1", "S4", "S5"} | POLICY,
    """
    prior_treated_tb_provenance_preserved residual_fibrosis_preserved
    tb_activity_unresolved prior_tb_and_new_symptoms_preserved
    recurrence_from_residual_fibrosis prior_tb_derived_from_image
    reactivation_confirmed active_tb_confirmed current_microbiology_invented
    """,
)
_register(
    {"S1", "S5"} | POLICY,
    """
    pneumonia_hypothesis_preserved pulmonary_malignancy_concern_preserved
    shared_evidence_not_double_counted shared_lesion_evidence_not_double_counted
    forced_pneumonia_tb_winner forced_malignancy_tb_winner
    acute_consolidation_equated_with_tb cavitary_mass_confirms_tb
    cavitary_mass_confirms_cancer
    """,
)
_register(
    POLICY,
    """
    doctor_review_required model_scores_preserved score_not_tb_probability
    high_priority_clinical_review severe_respiratory_evidence_preserved
    activity_probability_from_scores tb_probability_from_scores
    infectiousness_or_prior_tb_probability_from_scores
    no_finding_contradiction_without_positive_target autonomous_microbiology_order
    autonomous_ntm_treatment autonomous_tb_treatment autonomous_treatment
    autonomous_isolation_instruction autonomous_admission_or_disposition
    treatment_regimen_generated
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


def test_pack_has_thirty_four_cases_and_every_rule_has_provenance():
    cases = _load_cases()
    labels = {
        label
        for case in cases
        for key in ("semantic_expectations", "forbidden_interpretations")
        for label in case[key]
    }

    assert len(cases) == 34
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
    assert "Tuberculosis" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-tuberculosis").exists()
    assert not (SKILL_ROOT / "medvision-chronic-infection").exists()
    assert "references/tb_chronic_mycobacterial/TB_CHRONIC_MYCOBACTERIAL_POLICY.md" in content
    assert "references/tb_chronic_mycobacterial/TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md" in content
    assert "references/tb_chronic_mycobacterial/references.md" in content


def test_loading_triggers_and_generic_non_trigger_boundary_are_encoded():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    for trigger in (
        "explicit pulmonary or pleural TB",
        "cavitation, tree-in-bud",
        "AFB smear, M. tuberculosis-specific molecular testing",
        "IGRA/TST or known TB exposure",
        "pleural ADA/IFN-gamma",
    ):
        assert trigger in content
    assert "Do not load this module solely for generic `Calcification`" in content
    assert "`Pleural effusion`" in content


def test_module_files_sources_and_all_states_are_present():
    assert {path.name for path in MODULE_ROOT.iterdir()} == {
        "TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md",
        "TB_CHRONIC_MYCOBACTERIAL_POLICY.md",
        "references.md",
    }
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (MODULE_ROOT / "TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert all(f"## S{number}" in references for number in range(1, 8))
    states = {
        "PULMONARY_TB_CONCERN_SUPPORTED",
        "PULMONARY_TB_CONCERN_INDETERMINATE",
        "PULMONARY_TB_NOT_ESTABLISHED",
        "PLEURAL_TB_CONCERN_SUPPORTED",
        "PLEURAL_TB_CONCERN_INDETERMINATE",
        "PLEURAL_TB_NOT_ESTABLISHED",
        "MICROBIOLOGICALLY_CONFIRMED_TB",
        "PATHOLOGY_SUPPORTED_TB",
        "TB_ACTIVITY_UNRESOLVED",
        "TB_SITE_UNRESOLVED",
        "AFB_DETECTED_SPECIES_UNRESOLVED",
        "NTM_PULMONARY_DISEASE_CONCERN_SUPPORTED",
        "NTM_PULMONARY_DISEASE_NOT_ESTABLISHED",
        "CHRONIC_THORACIC_INFECTION_CONCERN_SUPPORTED",
        "CHRONIC_INFECTION_ETIOLOGY_UNRESOLVED",
    }
    assert all(state in evidence for state in states)


def test_generic_image_findings_do_not_establish_active_or_prior_tb():
    evidence = (MODULE_ROOT / "TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    for boundary in (
        "Calcification != active TB",
        "Pulmonary fibrosis != prior or active TB",
        "Pleural effusion != tuberculous pleuritis",
        "Upper-lobe opacity != TB",
        "Cavity != TB",
    ):
        assert boundary in evidence
    for case_id in ("TB01", "TB02", "TB03"):
        assert "tb_module_nontrigger_boundary" in _case(case_id)[
            "semantic_expectations"
        ]


def test_infection_tests_and_exposure_do_not_establish_active_tb():
    assert "active_tb_from_positive_igra" in _case("TB06")[
        "forbidden_interpretations"
    ]
    assert "active_tb_excluded_by_negative_igra" in _case("TB07")[
        "forbidden_interpretations"
    ]
    assert "active_tb_from_exposure" in _case("TB08")[
        "forbidden_interpretations"
    ]


def test_afb_smear_neither_identifies_mtb_nor_excludes_tb_when_negative():
    assert "afb_detected_species_unresolved" in _case("TB09")[
        "semantic_expectations"
    ]
    assert "ntm_remains_possible" in _case("TB09")["semantic_expectations"]
    assert "tb_not_excluded_by_smear" in _case("TB10")[
        "semantic_expectations"
    ]
    assert "tb_excluded_by_negative_smear" in _case("TB10")[
        "forbidden_interpretations"
    ]


def test_mtb_specific_naat_and_culture_confirmation_preserve_specimen_and_timing():
    for case_id in ("TB11", "TB12", "TB13", "TB19", "TB20", "TB23", "TB32"):
        assert "microbiologically_confirmed_tb" in _case(case_id)[
            "semantic_expectations"
        ]
    assert "đờm" in _case("TB11")["input"]["laboratory"]
    assert "BAL" in _case("TB12")["input"]["laboratory"]
    assert "discordant_test_timing_preserved" in _case("TB13")[
        "semantic_expectations"
    ]
    assert "tb_site_unresolved" in _case("TB32")["semantic_expectations"]
    assert "untested_drug_resistance_inferred" in _case("TB11")[
        "forbidden_interpretations"
    ]


def test_discordant_smear_and_naat_remain_species_unresolved():
    case = _case("TB14")

    assert "AFB smear" in case["input"]["laboratory"]
    assert "NAAT âm tính" in case["input"]["laboratory"]
    assert "afb_detected_species_unresolved" in case["semantic_expectations"]
    assert "tb_ntm_both_unresolved" in case["semantic_expectations"]


def test_no_finding_does_not_erase_microbiologic_confirmation():
    _, data = _case_data(_case("TB15"))

    assert data["no_finding_policy"]["policy_state"] == (
        "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"
    )
    assert "microbiologically_confirmed_tb" in _case("TB15")[
        "semantic_expectations"
    ]
    assert "tb_excluded_by_normal_cxr" in _case("TB15")[
        "forbidden_interpretations"
    ]


def test_pleural_ada_is_supportive_without_a_universal_cutoff():
    assert "pleural_tb_concern_indeterminate" in _case("TB17")[
        "semantic_expectations"
    ]
    assert "universal_ada_cutoff_invented" in _case("TB17")[
        "forbidden_interpretations"
    ]
    assert "pleural_tb_concern_supported" in _case("TB18")[
        "semantic_expectations"
    ]
    assert "microbiologically_confirmed_tb" in _case("TB18")[
        "forbidden_interpretations"
    ]


def test_negative_pleural_naat_and_granulomas_remain_contextual():
    assert "negative_pleural_naat_preserved" in _case("TB21")[
        "semantic_expectations"
    ]
    assert "pleural_tb_excluded_by_negative_naat" in _case("TB21")[
        "forbidden_interpretations"
    ]
    assert "granuloma_equated_with_tb" in _case("TB22")[
        "forbidden_interpretations"
    ]
    assert "pathology_supported_tb" in _case("TB23")[
        "semantic_expectations"
    ]


def test_prior_tb_and_residual_fibrosis_do_not_establish_current_activity():
    assert "prior_treated_tb_provenance_preserved" in _case("TB25")[
        "semantic_expectations"
    ]
    assert "tb_activity_unresolved" in _case("TB25")["semantic_expectations"]
    assert "reactivation_confirmed" in _case("TB26")[
        "forbidden_interpretations"
    ]


def test_ntm_standard_sputum_boundary_requires_repeated_same_species_and_full_context():
    single = _case("TB29")
    repeated = _case("TB30")
    afb_ntm = _case("TB31")

    assert "Một culture đờm" in single["input"]["laboratory"]
    assert "ntm_pulmonary_disease_not_established" in single[
        "semantic_expectations"
    ]
    assert "Hai culture đờm riêng biệt" in repeated["input"]["laboratory"]
    assert "cùng NTM species X" in repeated["input"]["laboratory"]
    assert "ntm_pulmonary_disease_concern_supported" in repeated[
        "semantic_expectations"
    ]
    assert "afb_and_ntm_provenance_preserved" in afb_ntm[
        "semantic_expectations"
    ]
    assert "afb_relabelled_as_tb" in afb_ntm["forbidden_interpretations"]


def test_cross_disease_hypotheses_are_preserved_without_forced_winner():
    _, pneumonia_data = _case_data(_case("TB27"))
    _, malignancy_data = _case_data(_case("TB28"))

    assert {
        "medvision-consolidation",
        "medvision-infiltration",
    } <= set(resolve_hermes_skills(pneumonia_data))
    assert {
        "medvision-nodule-mass",
        "medvision-other-lesion",
    } <= set(resolve_hermes_skills(malignancy_data))
    assert "forced_pneumonia_tb_winner" in _case("TB27")[
        "forbidden_interpretations"
    ]
    assert "forced_malignancy_tb_winner" in _case("TB28")[
        "forbidden_interpretations"
    ]


def test_score_semantics_and_action_boundary_are_explicit():
    case = _case("TB33")
    evidence = (MODULE_ROOT / "TB_CHRONIC_MYCOBACTERIAL_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert [item["score"] for item in case["input"]["results"]] == [0.93, 0.89]
    assert "score_not_tb_probability" in case["semantic_expectations"]
    for prohibited in (
        "order sputum/NAAT/culture",
        "order bronchoscopy",
        "order pleural biopsy",
        "initiate respiratory isolation",
        "start anti-TB treatment",
        "recommend a regimen",
        "perform contact tracing",
        "make admission/disposition decisions",
    ):
        assert prohibited in evidence
