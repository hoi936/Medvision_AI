"""Provider-independent validation for Pleural thickening golden cases."""

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
    Path(__file__).parent / "golden_cases" / "pleural_thickening" / "cases.json"
)
CLASS_NAMES_PATH = Path(__file__).parents[1] / "class_names.json"
EXPECTED_CASE_IDS = {
    "isolated_cxr_pleural_thickening",
    "documented_asbestos_exposure",
    "ct_confirmed_calcified_pleural_plaque",
    "suspicious_ct_pleural_morphology",
    "pleural_thickening_with_pulmonary_fibrosis",
    "pleural_thickening_with_pleural_effusion",
    "score_semantics",
    "cxr_ai_ct_conflict",
}
ALLOWED_PROVENANCE = {
    "S1", "S2", "S3", "S4", "S5", "S6", "MEDVISION_SYSTEM_POLICY"
}
EXPECTATION_PROVENANCE = {
    "local_pleural_finding_preserved": {"S2"},
    "cross_sectional_morphology_unknown": {"S1", "S3"},
    "etiology_unknown": {"S3", "S4", "S5", "S6"},
    "documented_asbestos_exposure_preserved": {"S6"},
    "asbestos_related_pleural_disease_hypothesis_supported": {"S6"},
    "asbestosis_not_confirmed": {"S6"},
    "pleural_plaque_not_confirmed": {"S3", "S5", "S6"},
    "cxr_finding_preserved_separately": {"S1", "S2", "S3"},
    "explicit_ct_plaque_morphology_preserved": {"S3", "S5", "S6"},
    "explicit_pleural_calcification_localization_preserved": {"S3"},
    "explicit_suspicious_ct_morphology_preserved": {"S3", "S4"},
    "malignant_pleural_disease_concern": {"S3", "S4"},
    "pathology_status_separate": {"S3", "S4"},
    "both_upstream_labels_preserved": {"S2", "MEDVISION_SYSTEM_POLICY"},
    "pleural_and_parenchymal_evidence_separate": {"S3", "S6"},
    "etiology_remains_conditional": {"S3", "S6"},
    "fluid_reasoning_deferred_to_effusion_skill": {
        "S3", "S4", "MEDVISION_SYSTEM_POLICY"
    },
    "score_0_87_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "score_not_pleural_disease_probability": {"MEDVISION_SYSTEM_POLICY"},
    "evidence_conflict": {"MEDVISION_SYSTEM_POLICY"},
    "both_sources_preserved": {"MEDVISION_SYSTEM_POLICY"},
    "ct_more_specific_pleural_morphology": {"S1", "S3"},
    "ai_not_silently_erased": {"MEDVISION_SYSTEM_POLICY"},
    "doctor_review_required": {"MEDVISION_SYSTEM_POLICY"},
    "cxr_thickening_as_asbestos_or_asbestosis": {"S6"},
    "cxr_thickening_as_tb_or_malignancy": {"S3", "S4", "S5"},
    "cxr_thickening_as_pleural_plaque": {"S3", "S5", "S6"},
    "autonomous_ct_or_pet_order": {"MEDVISION_SYSTEM_POLICY"},
    "exposure_invented_from_imaging": {"S6"},
    "asbestosis_confirmed": {"S6"},
    "plaque_without_supplied_morphology": {"S3", "S5"},
    "invented_asbestos_exposure": {"S6"},
    "plaque_as_malignancy": {"S3", "S4"},
    "unlocalized_calcification_assumed_pleural": {"S1", "S3"},
    "mesothelioma_confirmed": {"S3", "S4"},
    "pleural_metastasis_confirmed": {"S3", "S4"},
    "suspicious_morphology_as_pathology": {"S3", "S4"},
    "autonomous_biopsy_or_thoracoscopy_order": {
        "MEDVISION_SYSTEM_POLICY"
    },
    "coexistence_as_asbestosis": {"S6"},
    "coexistence_as_occupational_exposure": {"S6"},
    "coexistence_as_mesothelioma": {"S3", "S4"},
    "coexistence_as_tb": {"S3", "S5"},
    "coexistence_as_empyema": {"S3", "S4"},
    "coexistence_as_malignancy": {"S3", "S4"},
    "score_as_mesothelioma_asbestos_tb_or_malignancy_probability": {
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

    assert findings[0]["name"] == "Pleural thickening"
    assert all(item["name"] in canonical_names for item in findings)
    assert selected.count("medvision-pleural-thickening") == 1
    assert "requires_doctor_review: true" in prompt
    assert FINDING_SKILL_MAP["Pleural thickening"] == (
        "medvision-pleural-thickening"
    )


def test_isolated_cxr_case_forbids_etiology_plaque_and_ct_morphology_promotion():
    case = _case("isolated_cxr_pleural_thickening")

    assert {
        "local_pleural_finding_preserved",
        "cross_sectional_morphology_unknown",
        "etiology_unknown",
    } <= set(case["semantic_expectations"])
    assert {
        "cxr_thickening_as_asbestos_or_asbestosis",
        "cxr_thickening_as_tb_or_malignancy",
        "cxr_thickening_as_pleural_plaque",
    } <= set(case["forbidden_interpretations"])
    assert "nodular" not in case["input"]["history"].lower()
    assert "circumferential" not in case["input"]["history"].lower()


def test_asbestos_hypothesis_requires_explicit_supplied_exposure():
    exposed = _case("documented_asbestos_exposure")
    isolated = _case("isolated_cxr_pleural_thickening")

    assert "xác nhận phơi nhiễm asbestos" in exposed["input"]["history"]
    assert "asbestos_related_pleural_disease_hypothesis_supported" in exposed[
        "semantic_expectations"
    ]
    assert "asbestosis_not_confirmed" in exposed["semantic_expectations"]
    assert "asbestos_related_pleural_disease_hypothesis_supported" not in isolated[
        "semantic_expectations"
    ]


def test_ct_plaque_and_calcification_are_preserved_only_when_localized():
    case = _case("ct_confirmed_calcified_pleural_plaque")

    assert "pleural plaque có vôi hóa" in case["input"]["history"]
    assert "explicit_ct_plaque_morphology_preserved" in case[
        "semantic_expectations"
    ]
    assert "explicit_pleural_calcification_localization_preserved" in case[
        "semantic_expectations"
    ]
    assert "unlocalized_calcification_assumed_pleural" in case[
        "forbidden_interpretations"
    ]


def test_suspicious_ct_morphology_raises_concern_without_pathology_diagnosis():
    case = _case("suspicious_ct_pleural_morphology")

    assert "dạng nốt" in case["input"]["history"]
    assert "bao quanh chu vi" in case["input"]["history"]
    assert "malignant_pleural_disease_concern" in case["semantic_expectations"]
    assert {
        "mesothelioma_confirmed",
        "pleural_metastasis_confirmed",
        "suspicious_morphology_as_pathology",
    } <= set(case["forbidden_interpretations"])


def test_pulmonary_fibrosis_coexistence_selects_both_without_asbestosis():
    case = _case("pleural_thickening_with_pulmonary_fibrosis")
    _, case_data = _case_data(case)
    selected = resolve_hermes_skills(case_data)

    assert selected.count("medvision-pleural-thickening") == 1
    assert selected.count("medvision-pulmonary-fibrosis") == 1
    assert "pleural_and_parenchymal_evidence_separate" in case[
        "semantic_expectations"
    ]
    assert "coexistence_as_asbestosis" in case["forbidden_interpretations"]
    assert "coexistence_as_occupational_exposure" in case[
        "forbidden_interpretations"
    ]


def test_pleural_effusion_coexistence_selects_both_without_etiology_inference():
    case = _case("pleural_thickening_with_pleural_effusion")
    _, case_data = _case_data(case)
    selected = resolve_hermes_skills(case_data)

    assert selected.count("medvision-pleural-thickening") == 1
    assert selected.count("medvision-pleural-effusion") == 1
    assert "fluid_reasoning_deferred_to_effusion_skill" in case[
        "semantic_expectations"
    ]
    assert {
        "coexistence_as_mesothelioma",
        "coexistence_as_tb",
        "coexistence_as_empyema",
        "coexistence_as_malignancy",
    } <= set(case["forbidden_interpretations"])


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
        "autonomous_ct_or_pet_order",
        "autonomous_biopsy_or_thoracoscopy_order",
    } <= forbidden


def test_score_is_preserved_without_disease_probability_semantics():
    case = _case("score_semantics")

    assert case["input"]["results"][0]["score"] == 0.87
    assert "score_not_pleural_disease_probability" in case[
        "semantic_expectations"
    ]
    assert not re.search(
        r"87\s*%\s*(mesothelioma|asbestos|tuberculosis|malignancy)",
        " ".join(case["semantic_expectations"]),
        re.I,
    )
