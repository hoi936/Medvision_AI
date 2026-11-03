"""Provider-independent validation for pleural disease analysis."""

import json
from pathlib import Path

import pytest

from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_pleural_disease"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = (
    SKILL_ROOT / "medvision-disease-analysis" / "references" / "pleural_disease"
)
EXPECTED_CASE_IDS = {f"PL{number:02d}" for number in range(1, 31)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "MEDVISION_SYSTEM_POLICY"}
POLICY = {"MEDVISION_SYSTEM_POLICY"}
PROVENANCE = {}


def _register(sources, labels):
    for label in labels.split():
        assert label not in PROVENANCE
        PROVENANCE[label] = set(sources)


_register(
    {"S1", "S3", "S4"} | POLICY,
    """
    pleural_disease_finding_preserved pleural_thickening_preserved
    pleural_disease_hypothesis_supported pleural_etiology_unresolved
    pleural_localization_unknown generic_calcification_provenance_preserved
    malignant_pleural_effusion_not_established pleural_malignancy_concern_supported
    pleural_malignancy_concern_indeterminate suspicious_ct_morphology_preserved
    negative_ct_preserved recurrence_provenance_preserved
    malignant_pleural_effusion_inferred heart_failure_inferred
    pleural_infection_inferred metastatic_pleural_disease_inferred
    pleural_calcification_inferred pleural_plaque_inferred
    recurrence_confirms_malignancy ct_morphology_called_pathology_confirmation
    malignancy_excluded_by_negative_ct benign_etiology_declared
    histology_or_origin_invented malignancy_confirmed malignancy_inferred
    """,
)
_register(
    {"S2", "S4"} | POLICY,
    """
    explicit_pleural_plaque_preserved asbestos_related_pleural_disease_concern
    exposure_provenance_preserved asbestos_exposure_preserved_as_risk_context
    plaque_and_exposure_preserved mesothelioma_concern_supported
    mesothelioma_not_established plaque_equated_with_mesothelioma
    asbestos_exposure_equated_with_mesothelioma asbestos_exposure_inferred
    pleural_plaque_invented mesothelioma_confirmed
    tissue_histology_invented mesothelioma_histology_invented
    pathology_missing_explicit
    """,
)
_register(
    {"S1", "S2", "S3"} | POLICY,
    """
    negative_cytology_preserved nondiagnostic_cytology_preserved
    ongoing_pleural_malignancy_concern pleural_malignancy_concern_conflicted
    cytology_confirmed_malignant_pleural_effusion cytology_provenance_preserved
    tumor_origin_unresolved explicit_tumor_origin_preserved
    pathology_confirmed_mesothelioma explicit_histologic_subtype_preserved
    pathology_ihc_provenance_preserved pathology_confirmed_pleural_malignancy
    explicit_primary_origin_preserved pathology_provenance_preserved
    nondiagnostic_biopsy_preserved lesion_correspondence_uncertain
    malignancy_excluded_by_negative_cytology negative_cytology_called_benign
    mesothelioma_excluded nondiagnostic_cytology_called_benign
    mpe_confirmed
    mesothelioma_inferred_from_generic_malignant_cytology primary_origin_invented
    additional_stage_inferred additional_histology_invented mesothelioma_relabeling
    mesothelioma_from_cytology_alone histologic_subtype_invented
    additional_subtype_invented secondary_malignancy_relabelled_mesothelioma
    lung_primary_inferred benign_conclusion_from_negative_cytology
    malignancy_excluded nondiagnostic_biopsy_called_benign
    pathology_confirmation_invented staging_inferred mesothelioma_inferred
    """,
)
_register(
    {"S1"} | POLICY,
    """
    pleural_infection_concern_supported pleural_infection_not_established
    microbiology_and_purulence_provenance_preserved pneumonia_hypothesis_preserved
    pneumonia_and_effusion_preserved bacterial_species_invented
    imaging_alone_called_empyema parapneumonic_effusion_inferred
    complicated_parapneumonic_effusion_inferred empyema_inferred
    """,
)
_register(
    {"S1", "S3"} | POLICY,
    """
    pulmonary_malignancy_and_effusion_preserved heart_failure_and_pleural_hypotheses_preserved
    heart_failure_not_established shared_evidence_not_double_counted
    pleural_metastasis_from_known_lung_cancer mpe_from_known_lung_cancer
    effusion_proves_cardiogenic_etiology heart_failure_confirmed_from_effusion
    forced_single_etiology
    """,
)
_register(
    {"S1", "S4"} | POLICY,
    """
    no_finding_cxr_preserved ct_pleural_disease_preserved
    external_pleural_characterization_preserved other_lesion_ai_provenance_preserved
    ct_pleural_disease_excluded_by_no_finding cxr_result_erased
    pleural_thickening_skill_auto_selected ai_relabelled_as_pleural_thickening
    """,
)
_register(
    {"S1"} | POLICY,
    """
    ada_result_preserved tb_pleuritis_not_established pleural_ana_preserved
    lupus_pleuritis_not_established external_exudate_label_preserved
    external_transudate_label_preserved fluid_interpretation_provenance_preserved
    tb_pleuritis_confirmed_from_ada future_tb_module_logic_invented
    lupus_pleuritis_confirmed_from_ana lupus_diagnosis_invented
    lights_criteria_silently_computed exudate_equated_with_malignancy
    transudate_equated_with_heart_failure missing_fluid_data_filled
    """,
)
_register(
    POLICY,
    """
    doctor_review_required model_scores_preserved score_not_disease_probability
    ninety_percent_mesothelioma_probability ninety_five_percent_mpe_probability
    asbestos_probability_from_score no_finding_contradiction_without_positive_target
    autonomous_biopsy_or_treatment autonomous_drainage_or_antibiotics
    autonomous_oncology_or_surgery autonomous_tb_treatment
    autonomous_immunosuppression
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
    assert "Pleural disease" not in FINDING_SKILL_MAP
    assert "Mesothelioma" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-pleural-disease").exists()
    assert not (SKILL_ROOT / "medvision-mesothelioma").exists()
    assert "references/pleural_disease/PLEURAL_DISEASE_POLICY.md" in content
    assert "references/pleural_disease/PLEURAL_DISEASE_EVIDENCE.md" in content
    assert "references/pleural_disease/references.md" in content


def test_loading_triggers_and_generic_non_trigger_boundary_are_encoded():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    for trigger in (
        "canonical AI finding `Pleural effusion` or `Pleural thickening`",
        "trusted CT, ultrasound, or human interpretation",
        "pleural-fluid studies, pleural cytology, or pleural pathology",
        "malignant pleural effusion, pleural malignancy",
        "`Other lesion` is externally characterized",
    ):
        assert trigger in content
    assert "Do not load this module solely for generic `Calcification`" in content
    assert "`Lung Opacity`, or\nunrelated findings" in content


def test_module_files_sources_and_all_states_are_present():
    assert {path.name for path in MODULE_ROOT.iterdir()} == {
        "PLEURAL_DISEASE_EVIDENCE.md",
        "PLEURAL_DISEASE_POLICY.md",
        "references.md",
    }
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (MODULE_ROOT / "PLEURAL_DISEASE_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert all(f"## S{number}" in references for number in range(1, 5))
    states = {
        "PLEURAL_DISEASE_HYPOTHESIS_SUPPORTED",
        "PLEURAL_DISEASE_HYPOTHESIS_INDETERMINATE",
        "PLEURAL_ETIOLOGY_UNRESOLVED",
        "PLEURAL_MALIGNANCY_CONCERN_SUPPORTED",
        "PLEURAL_MALIGNANCY_CONCERN_INDETERMINATE",
        "PLEURAL_MALIGNANCY_CONCERN_CONFLICTED",
        "PLEURAL_MALIGNANCY_NOT_ESTABLISHED",
        "MALIGNANT_PLEURAL_EFFUSION_NOT_ESTABLISHED",
        "CYTOLOGY_CONFIRMED_MALIGNANT_PLEURAL_EFFUSION",
        "PATHOLOGY_CONFIRMED_PLEURAL_MALIGNANCY",
        "MESOTHELIOMA_CONCERN_SUPPORTED",
        "MESOTHELIOMA_NOT_ESTABLISHED",
        "PATHOLOGY_CONFIRMED_MESOTHELIOMA",
        "PLEURAL_INFECTION_CONCERN_SUPPORTED",
        "PLEURAL_INFECTION_NOT_ESTABLISHED",
        "ASBESTOS_RELATED_PLEURAL_DISEASE_CONCERN",
    }
    assert all(state in evidence for state in states)


def test_finding_level_evidence_does_not_establish_etiology():
    evidence = (MODULE_ROOT / "PLEURAL_DISEASE_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "Pleural effusion != malignant pleural effusion" in evidence
    assert "Pleural thickening != pleural malignancy" in evidence
    assert "Generic `Calcification POSITIVE` does not establish pleural localization" in evidence
    assert "pleural_etiology_unresolved" in _case("PL01")["semantic_expectations"]


def test_plaque_and_asbestos_context_do_not_confirm_mesothelioma():
    assert "pleural plaque != mesothelioma" in (
        MODULE_ROOT / "PLEURAL_DISEASE_EVIDENCE.md"
    ).read_text(encoding="utf-8")
    assert "explicit_pleural_plaque_preserved" in _case("PL04")[
        "semantic_expectations"
    ]
    assert "asbestos_exposure_equated_with_mesothelioma" in _case("PL05")[
        "forbidden_interpretations"
    ]
    assert "mesothelioma_not_established" in _case("PL06")[
        "semantic_expectations"
    ]


def test_ct_morphology_raises_concern_but_is_not_pathology():
    assert "pleural_malignancy_concern_supported" in _case("PL08")[
        "semantic_expectations"
    ]
    assert "ct_morphology_called_pathology_confirmation" in _case("PL08")[
        "forbidden_interpretations"
    ]
    assert "malignancy_excluded_by_negative_ct" in _case("PL09")[
        "forbidden_interpretations"
    ]


def test_cytology_confirmation_and_negative_nondiagnostic_boundaries():
    assert "negative_cytology_preserved" in _case("PL10")[
        "semantic_expectations"
    ]
    assert "nondiagnostic_cytology_called_benign" in _case("PL11")[
        "forbidden_interpretations"
    ]
    assert "cytology_confirmed_malignant_pleural_effusion" in _case("PL12")[
        "semantic_expectations"
    ]
    assert "tumor_origin_unresolved" in _case("PL12")["semantic_expectations"]
    assert "explicit_tumor_origin_preserved" in _case("PL14")[
        "semantic_expectations"
    ]


def test_mesothelioma_and_secondary_malignancy_require_explicit_tissue_pathology():
    assert "pathology_confirmed_mesothelioma" in _case("PL17")[
        "semantic_expectations"
    ]
    assert "epithelioid" in _case("PL17")["input"]["history"]
    assert "pathology_confirmed_pleural_malignancy" in _case("PL18")[
        "semantic_expectations"
    ]
    assert "di căn từ vú" in _case("PL18")["input"]["history"]
    assert "secondary_malignancy_relabelled_mesothelioma" in _case("PL18")[
        "forbidden_interpretations"
    ]


def test_known_pulmonary_malignancy_does_not_create_pleural_metastasis_or_mpe():
    case = _case("PL13")

    assert [item["finding"] for item in case["input"]["results"]] == [
        "Pleural effusion",
        "Nodule/Mass",
    ]
    assert "pleural_metastasis_from_known_lung_cancer" in (
        case["forbidden_interpretations"]
    )
    assert "malignant_pleural_effusion_not_established" in (
        case["semantic_expectations"]
    )


def test_infection_requires_integrated_evidence_and_no_autonomous_action():
    supported = _case("PL19")
    insufficient = _case("PL20")

    assert "split-pleura sign" in supported["input"]["history"]
    assert "microbiology dương tính" in supported["input"]["laboratory"]
    assert "pleural_infection_concern_supported" in supported[
        "semantic_expectations"
    ]
    assert "pleural_infection_not_established" in insufficient[
        "semantic_expectations"
    ]
    assert "empyema_inferred" in insufficient["forbidden_interpretations"]


def test_cross_disease_hf_pneumonia_and_malignancy_are_preserved_without_winner():
    _, pneumonia_data = _case_data(_case("PL20"))
    _, hf_data = _case_data(_case("PL21"))
    _, malignancy_data = _case_data(_case("PL13"))

    assert {
        "medvision-consolidation",
        "medvision-pleural-effusion",
    } <= set(resolve_hermes_skills(pneumonia_data))
    assert {
        "medvision-cardiomegaly",
        "medvision-pleural-effusion",
    } <= set(resolve_hermes_skills(hf_data))
    assert {
        "medvision-nodule-mass",
        "medvision-pleural-effusion",
    } <= set(resolve_hermes_skills(malignancy_data))
    assert "forced_single_etiology" in _case("PL21")[
        "forbidden_interpretations"
    ]


def test_no_finding_and_other_lesion_preserve_modality_and_ai_provenance():
    _, no_finding_data = _case_data(_case("PL22"))
    _, other_data = _case_data(_case("PL23"))

    assert no_finding_data["no_finding_policy"]["policy_state"] == (
        "NO_FINDING_WITHIN_14_CLASS_TAXONOMY"
    )
    other_selected = resolve_hermes_skills(other_data)
    assert "medvision-other-lesion" in other_selected
    assert "medvision-pleural-thickening" not in other_selected
    assert other_data["model_findings"]["findings"][1]["decision"] == "NEGATIVE"


def test_fluid_categories_are_preserved_without_silent_lights_calculation():
    assert "external_exudate_label_preserved" in _case("PL29")[
        "semantic_expectations"
    ]
    assert "exudate_equated_with_malignancy" in _case("PL29")[
        "forbidden_interpretations"
    ]
    assert "external_transudate_label_preserved" in _case("PL30")[
        "semantic_expectations"
    ]
    assert "transudate_equated_with_heart_failure" in _case("PL30")[
        "forbidden_interpretations"
    ]


def test_ada_and_ana_alone_do_not_confirm_tb_or_lupus_pleuritis():
    assert "tb_pleuritis_not_established" in _case("PL27")[
        "semantic_expectations"
    ]
    assert "tb_pleuritis_confirmed_from_ada" in _case("PL27")[
        "forbidden_interpretations"
    ]
    assert "lupus_pleuritis_not_established" in _case("PL28")[
        "semantic_expectations"
    ]
    assert "lupus_pleuritis_confirmed_from_ana" in _case("PL28")[
        "forbidden_interpretations"
    ]


def test_score_semantics_and_action_boundary_are_explicit():
    case = _case("PL24")
    evidence = (MODULE_ROOT / "PLEURAL_DISEASE_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert [item["score"] for item in case["input"]["results"]] == [0.9, 0.95]
    assert "score_not_disease_probability" in case["semantic_expectations"]
    for prohibited in (
        "order thoracentesis",
        "order CT/PET",
        "perform pleural biopsy",
        "place chest tube/IPC",
        "prescribe antibiotics",
        "perform pleurodesis",
        "refer to oncology/surgery",
        "start cancer treatment",
    ):
        assert prohibited in evidence
