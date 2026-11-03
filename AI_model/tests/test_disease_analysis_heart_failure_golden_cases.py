"""Provider-independent validation for Disease Analysis v2 Heart Failure."""

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
    / "disease_analysis_heart_failure"
    / "cases.json"
)
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
HF_ROOT = SKILL_ROOT / "medvision-disease-analysis" / "references" / "heart_failure"
EXPECTED_CASE_IDS = {f"HF{number:02d}" for number in range(1, 19)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "MEDVISION_SYSTEM_POLICY"}

DISEASE_AND_PHENOTYPE_LABELS = {
    "heart_failure_hypothesis_supported",
    "heart_failure_not_established",
    "heart_failure_possible_without_radiographic_congestion",
    "heart_failure_hypothesis_conflicted",
    "heart_failure_hypothesis_preserved",
    "heart_failure_confirmed",
    "hf_phenotype_unresolved",
    "phenotype_only_from_adequate_echo_and_syndrome",
    "current_phenotype_allowed_with_adequate_echo",
    "current_phenotype_invented",
    "phenotype_from_cxr_alone",
    "hfpef_may_be_supported_with_objective_evidence",
    "preserved_ef_alone_insufficient",
    "hfpef_from_preserved_ef_alone",
    "historical_hfmref_label_preserved",
    "historical_label_silently_rewritten",
    "hf_with_improved_ef_inferred_from_one_study",
    "longitudinal_evidence_missing",
    "prior_ef_invented",
}
IMAGING_LABELS = {
    "imaging_without_sufficient_hf_clinical_support",
    "cardiomegaly_preserved_as_cxr_evidence",
    "ef_inferred_from_cxr",
    "chamber_abnormality_inferred_from_cardiomegaly",
    "cardiogenic_cause_unknown_or_possible",
    "transudate_inferred",
    "generic_opacity_not_converted_to_edema",
    "generic_opacity_remains_nonspecific",
    "pulmonary_edema_inferred_from_generic_opacity",
    "generic_opacity_automatically_assigned_to_edema",
    "generic_opacity_automatically_assigned_to_pneumonia",
    "cardiogenic_congestion_hypothesis_supported",
    "trusted_congestion_description_preserved",
    "objective_evidence_preserved",
    "no_finding_not_universal_hf_exclusion",
    "no_finding_excludes_hf",
    "heart_failure_excluded_by_no_finding",
}
BIOMARKER_LABELS = {
    "natriuretic_peptide_supportive_nonspecific",
    "hf_objective_evidence_incomplete",
    "heart_failure_confirmed_from_np_alone",
    "hf_probability_from_np",
    "renal_dysfunction_preserved_as_np_modifier",
    "natriuretic_peptide_not_discarded",
    "natriuretic_peptide_discarded_due_to_renal_dysfunction",
    "obesity_preserved_as_np_modifier",
    "low_np_not_universal_hf_exclusion",
    "heart_failure_excluded_by_low_np",
}
SYSTEM_POLICY_LABELS = {
    "doctor_review_required",
    "echo_source_and_time_preserved",
    "historical_source_and_time_preserved",
    "source_and_timing_preserved",
    "evidence_conflict_preserved",
    "earlier_cxr_silently_preferred",
    "later_objective_evidence_erased",
    "no_finding_no_contradiction_without_positive_target",
    "no_finding_contradiction_without_positive_target",
    "pneumonia_hypothesis_preserved",
    "no_forced_disease_winner",
    "shared_evidence_not_double_counted",
    "single_forced_etiology",
    "hidden_disease_score",
    "score_0_95_preserved",
    "score_not_hf_probability",
    "ninety_five_percent_hf_probability",
    "high_priority_clinical_review",
    "autonomous_thoracentesis_or_drainage",
    "autonomous_treatment_or_disposition",
    "autonomous_diuretic_or_ventilation_order",
    "autonomous_icu_or_admission_decision",
    "autonomous_vasopressor_order",
}
EXPECTATION_PROVENANCE = {
    **{label: {"S1", "S2"} for label in DISEASE_AND_PHENOTYPE_LABELS},
    **{label: {"S1", "S3", "S4"} for label in IMAGING_LABELS},
    **{label: {"S1", "S2", "S3"} for label in BIOMARKER_LABELS},
    **{label: {"MEDVISION_SYSTEM_POLICY"} for label in SYSTEM_POLICY_LABELS},
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


def test_pack_has_eighteen_cases_and_every_rule_has_allowed_provenance():
    cases = _load_cases()
    labels = {
        label
        for case in cases
        for key in ("semantic_expectations", "forbidden_interpretations")
        for label in case[key]
    }

    assert len(cases) == 18
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
            for term in ("autonomous", "treatment", "thoracentesis")
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
    assert "requires_doctor_review: true" in prompt


def test_module_is_progressively_loaded_without_new_skill_or_mapping():
    content = DISEASE_SKILL.read_text(encoding="utf-8")

    assert len(FINDING_SKILL_MAP) == 14
    assert "Heart failure" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-heart-failure").exists()
    assert "references/heart_failure/HEART_FAILURE_POLICY.md" in content
    assert "references/heart_failure/HEART_FAILURE_EVIDENCE.md" in content
    assert "references/heart_failure/references.md" in content
    assert all(
        name in content
        for name in (
            "Cardiomegaly",
            "Pleural effusion",
            "Lung Opacity",
            "Infiltration",
            "Consolidation",
        )
    )
    assert "Do not load this module solely for unrelated findings" in content


def test_module_files_sources_and_current_source_precedence_are_present():
    assert {path.name for path in HF_ROOT.iterdir()} == {
        "HEART_FAILURE_EVIDENCE.md",
        "HEART_FAILURE_POLICY.md",
        "references.md",
    }
    references = (HF_ROOT / "references.md").read_text(encoding="utf-8")
    evidence = (HF_ROOT / "HEART_FAILURE_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert all(f"## S{number}" in references for number in range(1, 5))
    assert "When older phenotype conventions directly differ from 2026 sources" in references
    assert "Use current 2026 source precedence" in evidence
    assert "No single universal numeric NP cutoff" in evidence


def test_imaging_only_and_np_only_cases_do_not_establish_hf():
    hf01 = _case("HF01")
    hf03 = _case("HF03")
    hf06 = _case("HF06")

    assert hf01["input"]["symptoms"] == ""
    assert hf03["input"]["results"][0]["finding"] == "Pleural effusion"
    assert "heart_failure_confirmed" in hf01["forbidden_interpretations"]
    assert "transudate_inferred" in hf03["forbidden_interpretations"]
    assert "heart_failure_confirmed_from_np_alone" in hf06["forbidden_interpretations"]


def test_np_modifiers_and_no_finding_boundaries_are_explicit():
    assert "rối loạn chức năng thận" in _case("HF07")["input"]["history"]
    assert "béo phì" in _case("HF08")["input"]["history"]
    assert "BNP thấp" in _case("HF08")["input"]["laboratory"]
    assert _case("HF09")["input"]["results"][0]["finding"] == "No finding"
    assert "no_finding_no_contradiction_without_positive_target" in _case("HF09")[
        "semantic_expectations"
    ]


def test_cross_disease_case_preserves_both_hypotheses_without_assigning_generic_opacity():
    case = _case("HF13")
    _, data = _case_data(case)
    selected = resolve_hermes_skills(data)

    assert selected.count("medvision-consolidation") == 1
    assert selected.count("medvision-lung-opacity") == 1
    assert {
        "pneumonia_hypothesis_preserved",
        "heart_failure_hypothesis_preserved",
        "shared_evidence_not_double_counted",
        "no_forced_disease_winner",
    } <= set(case["semantic_expectations"])
    assert {
        "generic_opacity_automatically_assigned_to_edema",
        "generic_opacity_automatically_assigned_to_pneumonia",
        "single_forced_etiology",
    } <= set(case["forbidden_interpretations"])


def test_phenotype_boundaries_require_objective_and_longitudinal_evidence():
    current = _case("HF10")
    hfpef = _case("HF11")
    historical = _case("HF17")
    improved = _case("HF18")

    assert "Siêu âm tim hiện tại" in current["input"]["history"]
    assert "áp lực đổ đầy tăng" in hfpef["input"]["history"]
    assert "preserved_ef_alone_insufficient" in hfpef["semantic_expectations"]
    assert "HFmrEF" in historical["input"]["history"]
    assert "historical_label_silently_rewritten" in historical[
        "forbidden_interpretations"
    ]
    assert "không cung cấp giá trị EF trước đó" in improved["input"]["history"]
    assert "hf_with_improved_ef_inferred_from_one_study" in improved[
        "forbidden_interpretations"
    ]


def test_conflict_safety_and_score_semantics_are_bounded():
    conflict = _case("HF14")
    safety = _case("HF15")
    score = _case("HF16")

    assert "thực hiện sau đó" in conflict["input"]["history"]
    assert "heart_failure_hypothesis_conflicted" in conflict[
        "semantic_expectations"
    ]
    assert "high_priority_clinical_review" in safety["semantic_expectations"]
    assert score["input"]["results"][0]["score"] == 0.95
    assert "score_not_hf_probability" in score["semantic_expectations"]


def test_hard_constraints_forbid_diagnosis_probability_and_autonomous_actions():
    evidence = (HF_ROOT / "HEART_FAILURE_EVIDENCE.md").read_text(
        encoding="utf-8"
    )

    assert "Convert Cardiomegaly directly into HF" in evidence
    assert "Infer EF from CXR" in evidence
    assert "Infer HFpEF from preserved EF alone" in evidence
    assert "Infer improved EF from one study" in evidence
    assert "Force edema vs pneumonia when evidence is mixed" in evidence
    assert "Convert AI score to HF probability" in evidence
    assert "Issue autonomous treatment, imaging, procedure, or disposition" in evidence
