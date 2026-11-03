"""Provider-independent validation for Calcification golden cases."""

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
    Path(__file__).parent / "golden_cases" / "calcification" / "cases.json"
)
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "isolated_calcification_with_bbox",
    "calcification_with_nodule_mass_without_colocalization",
    "ct_confirmed_intranodular_calcification",
    "calcification_with_pleural_thickening_unknown_localization",
    "ct_confirmed_calcified_pleural_plaque",
    "calcified_nodes_with_prior_granulomatous_context",
    "score_semantics",
    "cxr_ai_ct_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "calcification_finding_and_bbox_preserved": {"S1"},
    "anatomical_compartment_unknown": {"S1", "S3", "S6"},
    "etiology_unknown": {"S2", "S3", "S4", "S5", "S6"},
    "both_upstream_labels_preserved": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "same_lesion_relationship_unknown": {"S1", "S4"},
    "explicit_pulmonary_intranodular_localization_preserved": {"S3", "S4"},
    "supplied_central_pattern_preserved": {"S4"},
    "pattern_refines_morphology": {"S4"},
    "overlapping_finding_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "pleural_localization_unknown": {"S1", "S3", "S5"},
    "upstream_findings_preserved": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "explicit_ct_pleural_plaque_preserved": {"S3", "S5"},
    "explicit_pleural_localization_preserved": {"S3", "S5"},
    "explicit_nodal_localization_preserved": {"S3", "S6"},
    "prior_healed_granulomatous_context_preserved": {"S3"},
    "bounded_granulomatous_hypothesis": {"S3"},
    "score_0_90_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_disease_or_benignity_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ct_more_specific_localization_evidence": {"S2", "S3", "S4", "S6"},
    "ai_not_silently_erased": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "bbox_as_pulmonary_pleural_nodal_or_cardiovascular_origin": {"S1"},
    "bbox_as_nodule_plaque_or_lymph_node": {"S1"},
    "calcification_as_etiologic_diagnosis": {"S1", "S3", "S6"},
    "autonomous_ct_order": {"MEDVISION_SYSTEM_POLICY"},
    "automatic_calcified_pulmonary_nodule": {"S1", "S4"},
    "calcification_as_benignity": {"S4"},
    "calcification_excludes_malignancy": {"S4"},
    "intranodular_calcification_as_benignity": {"S4"},
    "invented_calcification_pattern": {"S4"},
    "automatic_calcified_pleural_plaque": {"S3", "S5"},
    "invented_asbestos_exposure": {"S5"},
    "generic_cooccurrence_as_colocalization": {"S1", "S3", "S5"},
    "calcified_plaque_as_asbestosis": {"S5"},
    "active_tb_diagnosis": {"S3"},
    "tb_as_only_cause": {"S3"},
    "forced_sarcoidosis_or_silicosis": {"S3"},
    "score_as_benignity_tb_malignancy_granuloma_or_asbestos_probability": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "silent_ai_erasure": {"MEDVISION_SYSTEM_POLICY"},
    "conflict_erased": {"MEDVISION_SYSTEM_POLICY"},
}
FOCUSED_GUARDRAILS = {
    "calcification_with_pulmonary_fibrosis": {
        "findings": ["Calcification", "Pulmonary fibrosis"],
        "forbidden": {
            "automatic_dystrophic_pulmonary_calcification",
            "pulmonary_ossification_inference",
        },
        "provenance": {"S2"},
    },
    "calcification_with_cardiovascular_silhouette_findings": {
        "findings": ["Calcification", "Aortic enlargement", "Cardiomegaly"],
        "forbidden": {
            "automatic_aortic_calcification",
            "automatic_coronary_calcification",
            "automatic_valvular_calcification",
            "automatic_pericardial_calcification",
        },
        "provenance": {"S3", "S6"},
    },
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


def _resolve_names(names):
    payload = {
        "model_findings": {
            "findings": [
                {"name": name, "decision": "POSITIVE"} for name in names
            ]
        }
    }
    return resolve_hermes_skills(payload)


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
        item["provenance"] <= ALLOWED_PROVENANCE
        for item in FOCUSED_GUARDRAILS.values()
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

    assert findings[0]["name"] == "Calcification"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-calcification") == 1
    assert "requires_doctor_review: true" in prompt
    assert FINDING_SKILL_MAP["Calcification"] == "medvision-calcification"


def test_bbox_is_preserved_but_does_not_establish_anatomical_compartment():
    case = _case("isolated_calcification_with_bbox")
    _, case_data = _case_data(case)
    finding = case_data["model_findings"]["findings"][0]

    assert finding["bbox"] == [120, 85, 168, 133]
    assert finding["anatomic_location"] is None
    assert "anatomical_compartment_unknown" in case["semantic_expectations"]
    assert {
        "bbox_as_pulmonary_pleural_nodal_or_cardiovascular_origin",
        "bbox_as_nodule_plaque_or_lymph_node",
    } <= set(case["forbidden_interpretations"])


def test_nodule_coexistence_without_colocalization_keeps_relationship_unknown():
    case = _case("calcification_with_nodule_mass_without_colocalization")
    _, case_data = _case_data(case)
    selected = resolve_hermes_skills(case_data)

    assert selected.count("medvision-calcification") == 1
    assert selected.count("medvision-nodule-mass") == 1
    assert "same_lesion_relationship_unknown" in case["semantic_expectations"]
    assert "automatic_calcified_pulmonary_nodule" in case[
        "forbidden_interpretations"
    ]
    assert "calcification_excludes_malignancy" in case[
        "forbidden_interpretations"
    ]


def test_explicit_ct_intranodular_location_and_pattern_are_preserved_only_as_supplied():
    case = _case("ct_confirmed_intranodular_calcification")

    assert "nằm trong nốt phổi" in case["input"]["history"]
    assert "pattern trung tâm" in case["input"]["history"]
    assert "explicit_pulmonary_intranodular_localization_preserved" in case[
        "semantic_expectations"
    ]
    assert "supplied_central_pattern_preserved" in case["semantic_expectations"]
    assert "invented_calcification_pattern" in case[
        "forbidden_interpretations"
    ]
    assert "calcification_excludes_malignancy" in case[
        "forbidden_interpretations"
    ]


def test_pleural_coexistence_requires_explicit_localization_before_plaque_inference():
    unknown = _case("calcification_with_pleural_thickening_unknown_localization")
    confirmed = _case("ct_confirmed_calcified_pleural_plaque")
    _, unknown_data = _case_data(unknown)
    selected = resolve_hermes_skills(unknown_data)

    assert selected.count("medvision-calcification") == 1
    assert selected.count("medvision-pleural-thickening") == 1
    assert "pleural_localization_unknown" in unknown["semantic_expectations"]
    assert "automatic_calcified_pleural_plaque" in unknown[
        "forbidden_interpretations"
    ]
    assert "explicit_ct_pleural_plaque_preserved" in confirmed[
        "semantic_expectations"
    ]
    assert "invented_asbestos_exposure" in confirmed[
        "forbidden_interpretations"
    ]


def test_nodal_granulomatous_context_does_not_become_active_tb_or_only_cause():
    case = _case("calcified_nodes_with_prior_granulomatous_context")

    assert "hạch rốn phổi và trung thất vôi hóa" in case["input"]["history"]
    assert "explicit_nodal_localization_preserved" in case[
        "semantic_expectations"
    ]
    assert "prior_healed_granulomatous_context_preserved" in case[
        "semantic_expectations"
    ]
    assert {"active_tb_diagnosis", "tb_as_only_cause"} <= set(
        case["forbidden_interpretations"]
    )


@pytest.mark.parametrize(
    "guardrail_id",
    sorted(FOCUSED_GUARDRAILS),
)
def test_additional_cross_skill_guardrails_select_all_findings_without_colocalization(
    guardrail_id,
):
    guardrail = FOCUSED_GUARDRAILS[guardrail_id]
    selected = _resolve_names(guardrail["findings"])
    expected_skills = {
        FINDING_SKILL_MAP[name] for name in guardrail["findings"]
    }

    assert all(selected.count(skill) == 1 for skill in expected_skills)
    assert expected_skills <= set(selected)
    assert guardrail["forbidden"]
    assert guardrail["provenance"] <= ALLOWED_PROVENANCE


def test_calcification_is_never_promoted_to_ossification_mpc_or_dpc_without_context():
    pulmonary_guardrail = FOCUSED_GUARDRAILS[
        "calcification_with_pulmonary_fibrosis"
    ]

    assert "pulmonary_ossification_inference" in pulmonary_guardrail["forbidden"]
    assert "automatic_dystrophic_pulmonary_calcification" in (
        pulmonary_guardrail["forbidden"]
    )
    assert all(
        "metastatic_pulmonary_calcification" not in case["semantic_expectations"]
        for case in _load_cases()
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
    assert "autonomous_ct_order" in {
        item for case in cases for item in case["forbidden_interpretations"]
    }


def test_score_is_preserved_without_disease_or_benignity_probability():
    case = _case("score_semantics")

    assert case["input"]["results"][0]["score"] == 0.9
    assert "score_not_disease_or_benignity_probability" in case[
        "semantic_expectations"
    ]
    assert not re.search(
        r"90\s*%\s*(benign|tb|malignancy|granuloma|asbestos)",
        " ".join(case["semantic_expectations"]),
        re.I,
    )
