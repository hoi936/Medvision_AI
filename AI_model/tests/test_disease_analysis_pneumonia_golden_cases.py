"""Provider-independent validation for Disease Analysis v2 Pneumonia/CAP."""

import json
from pathlib import Path

import pytest

from hermes_report import (
    CORE_HERMES_SKILLS,
    FINDING_SKILL_MAP,
    build_report_prompt,
    resolve_hermes_skills,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = (
    Path(__file__).parent
    / "golden_cases"
    / "disease_analysis_pneumonia"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
PNEUMONIA_ROOT = (
    SKILL_ROOT / "medvision-disease-analysis" / "references" / "pneumonia"
)
EXPECTED_CASE_IDS = {f"P{number:02d}" for number in range(1, 16)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "MEDVISION_SYSTEM_POLICY"}

S1 = {"S1"}
S2 = {"S2"}
S3 = {"S3"}
S4 = {"S4"}
POLICY = {"MEDVISION_SYSTEM_POLICY"}
EXPECTATION_PROVENANCE = {
    "pneumonia_hypothesis_supported": S1 | POLICY,
    "community_acquired_true": S2 | POLICY,
    "doctor_review_required": POLICY,
    "confirmed_pneumonia": S1 | S4,
    "confirmed_bacterial_pneumonia": S1,
    "autonomous_treatment_or_procedure": POLICY,
    "imaging_without_sufficient_clinical_support": S1 | S4 | POLICY,
    "missing_evidence_explicit": POLICY,
    "invented_clinical_syndrome": POLICY,
    "pneumonia_possible_without_radiographic_support": S3 | POLICY,
    "no_finding_not_universal_exclusion": S3 | POLICY,
    "no_image_contradiction_from_symptoms": POLICY,
    "pneumonia_excluded": S3,
    "symptoms_create_no_finding_contradiction": POLICY,
    "autonomous_imaging_order": S3 | POLICY,
    "lung_opacity_remains_nonspecific": S4,
    "bacterial_etiology_inferred": S1 | S4,
    "infiltration_remains_legacy_nonspecific": S4 | POLICY,
    "infiltration_equated_with_pneumonia": S1 | S4,
    "pleural_effusion_preserved_as_associated_finding": S1 | POLICY,
    "empyema_inferred": S1 | POLICY,
    "complicated_parapneumonic_effusion_inferred": S1 | POLICY,
    "autonomous_drainage_or_treatment": POLICY,
    "low_procalcitonin_does_not_erase_evidence": S1,
    "bacterial_pneumonia_excluded_by_low_procalcitonin": S1,
    "antibiotic_decision_from_procalcitonin": S1 | POLICY,
    "broader_pneumonia_hypothesis_retained": S1 | S2 | POLICY,
    "cap_guideline_scope_limitation": S2 | POLICY,
    "immunocompetent_cap_pathway_fully_applicable": S2,
    "pathogen_inferred": S1 | POLICY,
    "community_acquired_false": S2 | POLICY,
    "cap_label_for_hospital_acquisition": S2,
    "community_acquired_unknown": S2 | POLICY,
    "community_acquired_invented": S2,
    "severe_cap_criteria_met": S1 | POLICY,
    "high_priority_clinical_review": POLICY,
    "autonomous_icu_admission_or_treatment": S1 | POLICY,
    "missing_severity_criteria_counted_negative": S1 | POLICY,
    "all_upstream_findings_preserved": POLICY,
    "overlap_deduplicated": POLICY,
    "three_independent_pneumonia_confirmations": S1 | S4 | POLICY,
    "multilobar_infiltrates_inferred_from_labels": S1 | POLICY,
    "severe_cap_criteria_not_met": S1 | POLICY,
    "infection_attributable_leukopenia_not_invented": S1 | POLICY,
    "severe_cap_from_two_minor_criteria": S1,
    "leukopenia_attributed_to_infection_without_evidence": S1,
    "pneumonia_hypothesis_conflicted": S1 | S3 | POLICY,
    "evidence_conflict_preserved": POLICY,
    "ai_silently_preferred": POLICY,
    "trusted_ct_erased": POLICY,
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


def _severe_cap_met(severity_evidence):
    return bool(severity_evidence["major_present"]) or len(
        severity_evidence["minor_present"]
    ) >= 3


def test_pack_has_fifteen_cases_and_every_rule_has_allowed_provenance():
    cases = _load_cases()
    labels = {
        label
        for case in cases
        for key in ("semantic_expectations", "forbidden_interpretations")
        for label in case[key]
    }

    assert len(cases) == 15
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
        not any("treatment" in item and item in case["semantic_expectations"] for item in case["semantic_expectations"])
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
    assert "requires_doctor_review: true" in prompt


def test_module_is_progressively_loaded_without_a_new_skill_or_mapping():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    assert len(FINDING_SKILL_MAP) == 14
    assert "Pneumonia" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-pneumonia").exists()
    assert "references/pneumonia/PNEUMONIA_POLICY.md" in content
    assert "references/pneumonia/PNEUMONIA_EVIDENCE.md" in content
    assert "references/pneumonia/references.md" in content
    assert all(name in content for name in ("Consolidation", "Lung Opacity", "Infiltration"))
    assert "acute respiratory infectious syndrome" in content
    assert "Do not load this module solely for unrelated findings" in content


def test_module_files_and_required_source_ids_are_present():
    expected_files = {
        "PNEUMONIA_EVIDENCE.md",
        "PNEUMONIA_POLICY.md",
        "references.md",
    }
    assert {path.name for path in PNEUMONIA_ROOT.iterdir()} == expected_files

    references = (PNEUMONIA_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (PNEUMONIA_ROOT / "PNEUMONIA_EVIDENCE.md").read_text(
        encoding="utf-8"
    )
    assert all(f"## S{number}" in references for number in range(1, 5))
    assert "RADIOGRAPHIC_FINDING != PNEUMONIA_DIAGNOSIS" in evidence
    assert ">=1 major criterion OR >=3 minor criteria" in evidence


def test_loading_triggers_and_non_trigger_boundary_are_encoded():
    assert "Consolidation" in _case("P01")["input"]["results"][0]["finding"]
    assert _case("P03")["input"]["results"][0]["finding"] == "No finding"
    assert "nghi ngờ viêm phổi" in _case("P03")["input"]["history"]
    assert "Ho cấp tính" in _case("P03")["input"]["symptoms"]

    content = DISEASE_SKILL.read_text(encoding="utf-8")
    assert "clinician or radiologist explicitly raises pneumonia" in content
    assert "negative or\n  indeterminate chest radiograph" in content


def test_one_major_criterion_is_sufficient_and_missing_stays_unknown():
    severity = _case("P11")["severity_evidence"]

    assert len(severity["major_present"]) == 1
    assert _severe_cap_met(severity) is True
    assert severity["minor_present"] == []
    assert "pao2_fio2" in severity["minor_unknown"]


def test_three_explicit_minor_criteria_are_sufficient():
    severity = _case("P13")["severity_evidence"]

    assert severity["major_present"] == []
    assert len(severity["minor_present"]) == 3
    assert _severe_cap_met(severity) is True


def test_two_minor_criteria_are_insufficient_and_leukopenia_is_not_invented():
    case = _case("P14")
    severity = case["severity_evidence"]

    assert len(severity["minor_present"]) == 2
    assert _severe_cap_met(severity) is False
    assert "infection_attributable_leukopenia" in severity["minor_unknown"]
    assert "infection_attributable_leukopenia" not in severity["minor_present"]
    assert "không cung cấp nguyên nhân" in case["input"]["laboratory"]


def test_multiple_image_labels_do_not_create_multilobar_criterion():
    case = _case("P12")
    severity = case["severity_evidence"]
    names = [item["finding"] for item in case["input"]["results"]]

    assert names == ["Consolidation", "Lung Opacity", "Infiltration"]
    assert "multilobar_infiltrates" in severity["minor_unknown"]
    assert "multilobar_infiltrates" not in severity["minor_present"]
    assert _severe_cap_met(severity) is False


def test_acquisition_scope_procalcitonin_effusion_and_conflict_boundaries():
    assert "ngoài bệnh viện" in _case("P01")["input"]["history"]
    assert "nằm viện" in _case("P09")["input"]["history"]
    assert "Không cung cấp" in _case("P10")["input"]["history"]
    assert "suy giảm miễn dịch nặng" in _case("P08")["input"]["history"]
    assert "Procalcitonin" in _case("P07")["input"]["laboratory"]
    assert any(
        item["finding"] == "Pleural effusion"
        for item in _case("P06")["input"]["results"]
    )
    assert "không có bất thường vùng khí phế nang" in _case("P15")["input"]["history"]


def test_policy_forbids_diagnosis_probability_and_autonomous_actions():
    evidence = (PNEUMONIA_ROOT / "PNEUMONIA_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "Convert AI score into pneumonia probability" in evidence
    assert "Convert severe-CAP criteria into autonomous disposition/treatment" in evidence
    assert "Infer empyema/parapneumonic effusion from pleural effusion alone" in evidence
    assert "Treat No Finding as universal pneumonia exclusion" in evidence
