"""Provider-independent validation for Other lesion golden cases."""

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
    Path(__file__).parent / "golden_cases" / "other_lesion" / "cases.json"
)
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "isolated_other_lesion_with_bbox",
    "other_lesion_and_nodule_distinct_regions",
    "other_lesion_with_supported_specific_overlap",
    "other_lesion_with_lung_opacity_unknown_correspondence",
    "later_external_characterization_outside_taxonomy",
    "multiple_other_lesion_detections",
    "score_semantics",
    "ai_human_or_ct_conflict",
}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "MEDVISION_SYSTEM_POLICY"}
EXPECTATION_PROVENANCE = {
    "unspecified_local_finding": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "bbox_and_score_preserved": {"S1", "S2"},
    "morphology_unknown": {"S1", "S3"},
    "anatomical_compartment_unknown": {"S1", "S2"},
    "etiology_unknown": {"S1"},
    "both_upstream_labels_preserved": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "distinct_detections_remain_separate": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "same_lesion_overlap_not_asserted": {"MEDVISION_SYSTEM_POLICY"},
    "specific_finding_refines_morphology": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "overlapping_finding_evidence": {"MEDVISION_SYSTEM_POLICY"},
    "overlap_not_double_counted": {"MEDVISION_SYSTEM_POLICY"},
    "generic_finding_not_deleted": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "correspondence_unknown": {"MEDVISION_SYSTEM_POLICY"},
    "findings_not_automatically_merged": {"MEDVISION_SYSTEM_POLICY"},
    "other_lesion_ai_provenance_preserved": {"S1", "S4"},
    "external_characterization_preserved_separately": {"S3", "S4"},
    "external_source_and_modality_preserved": {"S3", "S4"},
    "refinement_not_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "multiple_detection_objects_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "selector_skill_once": {"MEDVISION_SYSTEM_POLICY"},
    "distinct_boxes_not_merged_by_default": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "score_0_93_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_disease_or_morphology_probability": {
        "S4", "MEDVISION_SYSTEM_POLICY"
    },
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ai_not_silently_preferred": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"S4", "MEDVISION_SYSTEM_POLICY"},
    "other_lesion_as_other_diseases": {"S1"},
    "bbox_as_lung_pleural_mediastinal_bone_or_named_structure": {"S1", "S2"},
    "other_lesion_as_tumor_cancer_nodule_or_infection": {"S1"},
    "reverse_mapping_to_omitted_vindr_class": {"S1", "S2"},
    "autonomous_imaging_or_procedure_order": {"MEDVISION_SYSTEM_POLICY"},
    "automatic_detection_merge": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "same_lesion_overlap_as_certainty": {"MEDVISION_SYSTEM_POLICY"},
    "morphology_double_attribution": {"S3", "MEDVISION_SYSTEM_POLICY"},
    "generic_finding_erased": {"S1", "MEDVISION_SYSTEM_POLICY"},
    "overlap_as_independent_disease_confirmation": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "etiologic_diagnosis_from_generic_findings": {"S1"},
    "invented_new_skill_or_mapping": {"S1", "S2"},
    "ai_claimed_to_predict_later_morphology": {"S3", "S4"},
    "upstream_ai_erased": {"S1", "S4"},
    "distinct_detections_collapsed": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "multiple_skill_invocations_for_same_class": {"MEDVISION_SYSTEM_POLICY"},
    "score_as_cancer_tumor_or_serious_disease_probability": {
        "S4", "MEDVISION_SYSTEM_POLICY"
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

    assert findings[0]["name"] == "Other lesion"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-other-lesion") == 1
    assert "requires_doctor_review: true" in prompt
    assert FINDING_SKILL_MAP["Other lesion"] == "medvision-other-lesion"
    assert "No finding" not in FINDING_SKILL_MAP


def test_isolated_bbox_preserves_unspecified_state_without_anatomy_or_disease():
    case = _case("isolated_other_lesion_with_bbox")
    _, case_data = _case_data(case)
    finding = case_data["model_findings"]["findings"][0]

    assert finding["bbox"] == [110, 70, 172, 136]
    assert finding["anatomic_location"] is None
    assert {
        "unspecified_local_finding",
        "morphology_unknown",
        "anatomical_compartment_unknown",
        "etiology_unknown",
    } <= set(case["semantic_expectations"])
    assert {
        "other_lesion_as_other_diseases",
        "bbox_as_lung_pleural_mediastinal_bone_or_named_structure",
        "other_lesion_as_tumor_cancer_nodule_or_infection",
        "reverse_mapping_to_omitted_vindr_class",
    } <= set(case["forbidden_interpretations"])


def test_distinct_region_nodule_and_other_lesion_remain_separate():
    case = _case("other_lesion_and_nodule_distinct_regions")
    _, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["bbox"] != findings[1]["bbox"]
    assert selected.count("medvision-other-lesion") == 1
    assert selected.count("medvision-nodule-mass") == 1
    assert "distinct_detections_remain_separate" in case[
        "semantic_expectations"
    ]
    assert "same_lesion_overlap_not_asserted" in case["semantic_expectations"]
    assert "automatic_detection_merge" in case["forbidden_interpretations"]


def test_supported_same_abnormality_uses_specific_refinement_and_overlap():
    case = _case("other_lesion_with_supported_specific_overlap")
    _, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert findings[0]["bbox"] == findings[1]["bbox"]
    assert selected.count("medvision-other-lesion") == 1
    assert selected.count("medvision-calcification") == 1
    assert {
        "specific_finding_refines_morphology",
        "overlapping_finding_evidence",
        "overlap_not_double_counted",
        "generic_finding_not_deleted",
    } <= set(case["semantic_expectations"])


def test_unknown_correspondence_with_lung_opacity_does_not_force_overlap():
    case = _case("other_lesion_with_lung_opacity_unknown_correspondence")
    _, case_data = _case_data(case)
    selected = resolve_hermes_skills(case_data)

    assert selected.count("medvision-other-lesion") == 1
    assert selected.count("medvision-lung-opacity") == 1
    assert "correspondence_unknown" in case["semantic_expectations"]
    assert "findings_not_automatically_merged" in case[
        "semantic_expectations"
    ]
    assert "overlapping_finding_evidence" not in case["semantic_expectations"]


def test_later_external_characterization_preserves_provenance_as_refinement():
    case = _case("later_external_characterization_outside_taxonomy")

    assert "ngoài taxonomy 14 lớp" in case["input"]["history"]
    assert {
        "other_lesion_ai_provenance_preserved",
        "external_characterization_preserved_separately",
        "external_source_and_modality_preserved",
        "refinement_not_conflict",
    } <= set(case["semantic_expectations"])
    assert "evidence_conflict" not in case["semantic_expectations"]
    assert "invented_new_skill_or_mapping" in case["forbidden_interpretations"]


def test_human_characterization_does_not_auto_select_another_finding_skill():
    prompt = build_report_prompt(
        results=[
            {"finding": "Other lesion", "score": 0.84, "threshold": 0.5}
        ],
        history="CT được bác sĩ tin cậy mô tả Consolidation.",
    )
    case_data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    selected = resolve_hermes_skills(case_data)

    assert selected.count("medvision-other-lesion") == 1
    assert "medvision-consolidation" not in selected


def test_multiple_detections_remain_objects_but_select_skill_once():
    case = _case("multiple_other_lesion_detections")
    _, case_data = _case_data(case)
    findings = case_data["model_findings"]["findings"]
    selected = resolve_hermes_skills(case_data)

    assert len(findings) == 2
    assert findings[0]["bbox"] != findings[1]["bbox"]
    assert selected.count("medvision-other-lesion") == 1
    assert "multiple_detection_objects_preserved" in case[
        "semantic_expectations"
    ]
    assert "distinct_boxes_not_merged_by_default" in case[
        "semantic_expectations"
    ]


def test_no_finding_boundary_remains_unmapped_to_a_finding_skill():
    selected = resolve_hermes_skills(
        {
            "model_findings": {
                "findings": [{"name": "No finding", "decision": "POSITIVE"}]
            }
        }
    )

    assert "No finding" not in FINDING_SKILL_MAP
    assert "medvision-other-lesion" not in selected


def test_no_case_expects_autonomous_imaging_procedure_or_treatment():
    cases = _load_cases()
    assert all(
        not any(
            item.startswith("autonomous_")
            for item in case["semantic_expectations"]
        )
        for case in cases
    )
    assert "autonomous_imaging_or_procedure_order" in {
        item for case in cases for item in case["forbidden_interpretations"]
    }


def test_score_is_preserved_without_patient_level_probability():
    case = _case("score_semantics")

    assert case["input"]["results"][0]["score"] == 0.93
    assert "score_not_disease_or_morphology_probability" in case[
        "semantic_expectations"
    ]
    assert not re.search(
        r"93\s*%\s*(cancer|tumor|serious disease)",
        " ".join(case["semantic_expectations"]),
        re.I,
    )
