"""Provider-independent validation for longitudinal/temporal reasoning v1."""

import hashlib
import json
from pathlib import Path

import pytest

from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills
from temporal_reasoning_validator import (
    CHANGE_STATES,
    COMPARABILITY_STATES,
    CORRESPONDENCE_STATES,
    evaluate_temporal_case,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).parent / "golden_cases" / "temporal_reasoning" / "cases.json"
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = DISEASE_SKILL.parent / "references" / "temporal_reasoning"
EXPECTED_IDS = {f"TR{number:02d}" for number in range(1, 41)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "POLICY"}
SOURCE_SHA256 = {
    "TEMPORAL_REASONING_EVIDENCE.md": "ebc1707f5fa421c5a176666b6c06b2d1666d28dac6d690c01d14680a3e209e8f",
    "TEMPORAL_REASONING_POLICY.md": "0df8bcbbca07485dd914af853b33abe5381fb4ef1811419cf8315428bdebd3f7",
    "references.md": "1f5d79c2c8885a87ad61720e2790412966e577e6b3a448ec3a9bc00dc5c28bf9",
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def test_pack_has_forty_cases_with_complete_provenance_and_review_policy():
    cases = _load_cases()

    assert len(cases) == 40
    assert {case["id"] for case in cases} == EXPECTED_IDS
    assert all(set(case["provenance"]) <= ALLOWED_PROVENANCE for case in cases)
    assert all(case["provenance"] for case in cases)
    assert all(
        case["expected"]["causal_attribution"] == "not_established"
        for case in cases
    )


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_has_deterministic_temporal_result_and_frozen_selector(case):
    result = evaluate_temporal_case(case)
    expected = case["expected"]
    prompt = build_report_prompt(**case["input"])
    data = json.loads(
        prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0]
    )
    selected = resolve_hermes_skills(data)

    assert result == {
        "state": expected["state"],
        "correspondence": expected["correspondence"],
        "comparability": expected["comparability"],
        "causal_attribution": expected["causal_attribution"],
    }
    assert selected[0] == "medvision-evidence-fusion"
    assert selected[-2:] == ["medvision-safety-check", "medvision-disease-analysis"]
    assert len(selected) == len(set(selected))
    assert "requires_doctor_review: true" in prompt


def test_module_is_progressive_without_new_skill_mapping_or_frontmatter_change():
    content = DISEASE_SKILL.read_text(encoding="utf-8")
    frontmatter = content.split("---", 2)[1]

    assert len(FINDING_SKILL_MAP) == 14
    assert "Temporal reasoning" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-temporal-reasoning").exists()
    assert "references/temporal_reasoning/TEMPORAL_REASONING_POLICY.md" in content
    assert "references/temporal_reasoning/TEMPORAL_REASONING_EVIDENCE.md" in content
    assert "references/temporal_reasoning/references.md" in content
    assert "multiple clinically relevant timepoints" in content
    assert "merely because one observation uses the word `chronic`" in content
    assert "name: medvision-disease-analysis" in frontmatter
    assert "temporal" not in frontmatter.lower()


def test_source_files_are_byte_identical_and_states_are_complete():
    for filename, expected_digest in SOURCE_SHA256.items():
        installed = MODULE_ROOT / filename
        assert hashlib.sha256(installed.read_bytes()).hexdigest() == expected_digest

    evidence = (MODULE_ROOT / "TEMPORAL_REASONING_EVIDENCE.md").read_text(encoding="utf-8")
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    required = {
        *CHANGE_STATES.values(), "PERSISTENT", "RECURRENT",
        "INTERVAL_CHANGE_INDETERMINATE", "COMPARISON_NOT_POSSIBLE",
        "PRIOR_DATA_MISSING", "TEMPORAL_CONFLICT",
        *CORRESPONDENCE_STATES.values(), *COMPARABILITY_STATES.values(),
    }
    assert all(state in evidence for state in required)
    assert all(f"## S{number}" in references for number in range(1, 5))


def test_new_resolved_persistent_and_recurrent_boundaries():
    assert evaluate_temporal_case(_case("TR02"))["state"] == "NEW"
    assert evaluate_temporal_case(_case("TR12"))["state"] == "RESOLVED"
    assert evaluate_temporal_case(_case("TR14"))["state"] == "PERSISTENT"
    assert evaluate_temporal_case(_case("TR13"))["state"] == "RECURRENT"
    assert "NEW" in _case("TR01")["forbidden"]
    assert "RESOLVED" in _case("TR35")["forbidden"]
    assert "RECURRENT" in _case("TR14")["forbidden"]


def test_correspondence_blocks_false_growth_and_same_process_assumptions():
    assert _case("TR03")["expected"]["correspondence"] == "CORRESPONDENCE_NOT_SAME"
    assert _case("TR05")["expected"]["correspondence"] == "CORRESPONDENCE_UNCERTAIN"
    assert _case("TR33")["expected"]["correspondence"] == "CORRESPONDENCE_NOT_SAME"
    assert "true_lesion_growth" in _case("TR05")["forbidden"]
    assert "same_process_assumed" in _case("TR33")["forbidden"]


def test_modality_protocol_projection_unit_and_method_comparability_boundaries():
    assert _case("TR06")["expected"]["comparability"] == "LIMITED_COMPARABILITY"
    assert _case("TR07")["expected"]["comparability"] == "LIMITED_COMPARABILITY"
    assert _case("TR19")["expected"]["comparability"] == "NOT_COMPARABLE"
    assert _case("TR20")["expected"]["comparability"] == "LIMITED_COMPARABILITY"
    assert _case("TR25")["expected"]["comparability"] == "LIMITED_COMPARABILITY"
    assert _case("TR28")["expected"]["comparability"] == "NOT_COMPARABLE"


def test_missingness_conflict_date_precision_and_order_are_fail_closed():
    assert evaluate_temporal_case(_case("TR01"))["state"] == "PRIOR_DATA_MISSING"
    assert evaluate_temporal_case(_case("TR11"))["state"] == "INTERVAL_CHANGE_INDETERMINATE"
    assert evaluate_temporal_case(_case("TR32"))["state"] == "TEMPORAL_CONFLICT"
    assert "exact_interval_invented" in _case("TR36")["forbidden"]
    assert "test_order_invented" in _case("TR37")["forbidden"]


def test_nodule_and_ild_ppf_handoffs_preserve_module_ownership():
    assert all(_case(case_id)["expected"]["handoff"] == "pulmonary_malignancy" for case_id in ("TR02", "TR04", "TR05", "TR07"))
    assert all(_case(case_id)["expected"]["handoff"] == "ild_ppf" for case_id in ("TR15", "TR16", "TR18", "TR19", "TR20"))
    assert "malignancy_confirmed" in _case("TR04")["forbidden"]
    assert "ppf_confirmed_from_one_domain" in _case("TR16")["forbidden"]
    assert "ppf_confirmed_from_fvc_alone" in _case("TR18")["forbidden"]


def test_pneumonia_heart_failure_pleural_tb_and_aas_handoffs():
    expected = {
        "TR10": "pneumonia", "TR26": "heart_failure", "TR13": "pleural_disease",
        "TR21": "tb", "TR23": "tb", "TR24": "aas",
    }
    assert all(_case(case_id)["expected"]["handoff"] == owner for case_id, owner in expected.items())
    assert "active_tb_recurrence" in _case("TR21")["forbidden"]
    assert "earlier_cxr_erased" in _case("TR24")["forbidden"]


def test_source_supersession_preserves_older_provenance():
    for case_id in ("TR23", "TR24", "TR39"):
        assert _case(case_id)["temporal"]["source_supersession"] is True
    assert "old_negative_erased" in _case("TR23")["forbidden"]
    assert "earlier_imaging_erased" in _case("TR39")["forbidden"]


def test_treatment_sequence_never_establishes_causality_or_actions():
    for case_id in ("TR26", "TR27", "TR38"):
        case = _case(case_id)
        assert case["temporal"]["treatment_between"] is True
        assert evaluate_temporal_case(case)["causal_attribution"] == "not_established"
    evidence = (MODULE_ROOT / "TEMPORAL_REASONING_EVIDENCE.md").read_text(encoding="utf-8")
    assert "temporal association is not automatically causal" in evidence
    assert "Issue autonomous treatment/testing/procedure/disposition actions" in evidence


def test_ai_outputs_and_no_finding_do_not_manufacture_biologic_change():
    assert "WORSENED" in _case("TR05")["forbidden"]
    assert "RESOLVED" in _case("TR09")["forbidden"]
    assert "RESOLVED" in _case("TR35")["forbidden"]
    assert "IMPROVED" in _case("TR40")["forbidden"]
    assert _case("TR34")["expected"]["state"] == "NEW"
