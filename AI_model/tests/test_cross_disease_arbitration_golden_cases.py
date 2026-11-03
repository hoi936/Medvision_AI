"""Provider-independent cross-disease arbitration v1 validation."""

import hashlib
import json
from pathlib import Path

import pytest

from cross_disease_arbitration_validator import (
    FORBIDDEN_ORDERING_KEYS,
    build_arbitration,
    relationship_states,
    validate_arbitration_output,
)
from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).parent / "golden_cases" / "cross_disease_arbitration" / "cases.json"
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = DISEASE_SKILL.parent / "references" / "cross_disease_arbitration"
EXPECTED_IDS = {f"AR{number:02d}" for number in range(1, 43)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3"}
SOURCE_SHA256 = {
    "CROSS_DISEASE_ARBITRATION_EVIDENCE.md": "83ff2eb4ee31d2487d2f8e3fbe119e84a43bd600bacd2d3664aa6145cad37c45",
    "CROSS_DISEASE_ARBITRATION_POLICY.md": "548c747c5ccfe04b6e41dcaee095eb980b99b2e20714bfb54dca51142db347db",
    "references.md": "307cbf1970e192c1304d9a1afcd0edaea9b0167722049f89269528789fcf64e0",
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def test_pack_has_forty_two_cases_with_complete_provenance():
    cases = _load_cases()

    assert len(cases) == 42
    assert {case["id"] for case in cases} == EXPECTED_IDS
    assert all(case["provenance"] for case in cases)
    assert all(set(case["provenance"]) <= ALLOWED_PROVENANCE for case in cases)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_builds_valid_non_numeric_arbitration_and_keeps_selector(case):
    output = build_arbitration(case)
    arbitration = output["arbitration"]
    states = relationship_states(output)
    prompt = build_report_prompt(**case["input"])
    data = json.loads(prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0])
    selected = resolve_hermes_skills(data)

    assert validate_arbitration_output(output) is True
    assert set(case["expected_states"]) <= states
    assert arbitration["review"]["highest_priority"] == case["expected_priority"]
    assert arbitration["review"]["doctor_review_required"] is True
    assert arbitration["synthesis"]["no_numeric_ranking"] is True
    assert selected[0] == "medvision-evidence-fusion"
    assert selected[-2:] == ["medvision-safety-check", "medvision-disease-analysis"]
    assert len(selected) == len(set(selected))
    assert "requires_doctor_review: true" in prompt


def test_progressive_loading_has_no_new_skill_mapping_or_frontmatter_change():
    content = DISEASE_SKILL.read_text(encoding="utf-8")
    frontmatter = content.split("---", 2)[1]

    assert len(FINDING_SKILL_MAP) == 14
    assert "Cross-disease arbitration" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-cross-disease-arbitration").exists()
    assert "references/cross_disease_arbitration/CROSS_DISEASE_ARBITRATION_POLICY.md" in content
    assert "references/cross_disease_arbitration/CROSS_DISEASE_ARBITRATION_EVIDENCE.md" in content
    assert "references/cross_disease_arbitration/references.md" in content
    assert "two or more disease modules emit nontrivial hypotheses" in content
    assert "one uncomplicated disease hypothesis" in content
    assert "name: medvision-disease-analysis" in frontmatter
    assert "arbitration" not in frontmatter.lower()


def test_source_files_match_supplied_inputs_and_all_labels_are_present():
    for filename, expected_digest in SOURCE_SHA256.items():
        assert hashlib.sha256((MODULE_ROOT / filename).read_bytes()).hexdigest() == expected_digest

    evidence = (MODULE_ROOT / "CROSS_DISEASE_ARBITRATION_EVIDENCE.md").read_text(encoding="utf-8")
    policy = (MODULE_ROOT / "CROSS_DISEASE_ARBITRATION_POLICY.md").read_text(encoding="utf-8")
    references = (MODULE_ROOT / "references.md").read_text(encoding="utf-8")
    labels = {
        "HYPOTHESIS_SUPPORTED", "HYPOTHESIS_POSSIBLE", "HYPOTHESIS_INDETERMINATE",
        "HYPOTHESIS_CONFLICTED", "HYPOTHESIS_NOT_ESTABLISHED",
        "COMPETING_HYPOTHESES_PRESENT", "COEXISTING_PROCESSES_POSSIBLE",
        "COEXISTING_PROCESSES_SUPPORTED", "MUTUAL_EXCLUSIVITY_NOT_ESTABLISHED",
        "SHARED_EVIDENCE_PRESENT", "DISTINCT_EVIDENCE_PRESENT",
        "EVIDENCE_ATTRIBUTION_UNRESOLVED", "DUPLICATE_EVIDENCE_DEDUPLICATED",
        "REVIEW_PRIORITY_ROUTINE", "REVIEW_PRIORITY_ELEVATED", "REVIEW_PRIORITY_HIGH",
    }
    assert all(label in evidence + policy + references for label in labels)
    assert all(f"## S{number}" in references for number in range(1, 4))


def test_evidence_ledger_is_unique_complete_and_referenced_by_ids():
    output = build_arbitration(_case("AR25"))["arbitration"]
    required = {"id", "type", "value", "source", "modality_or_test", "timestamp", "provenance", "uncertainty", "duplicate_count"}
    ids = [item["id"] for item in output["evidence_ledger"]]

    assert len(ids) == len(set(ids)) == 1
    assert all(required <= set(item) for item in output["evidence_ledger"])
    assert output["evidence_ledger"][0]["duplicate_count"] == 3
    assert all(item["evidence_id"] in ids for item in output["evidence_matrix"])
    assert all(ref in ids for hypothesis in output["hypotheses"] for ref in hypothesis["supporting_evidence"])


@pytest.mark.parametrize("field", sorted(FORBIDDEN_ORDERING_KEYS))
def test_output_schema_rejects_disease_ranking_probability_fields(field):
    output = build_arbitration(_case("AR01"))
    output["arbitration"]["synthesis"][field] = 1

    with pytest.raises(ValueError, match="forbidden disease-ordering fields"):
        validate_arbitration_output(output)


def test_shared_and_distinct_evidence_are_separate_without_count_scoring():
    output = build_arbitration(_case("AR02"))
    states = relationship_states(output)

    assert {"SHARED_EVIDENCE_PRESENT", "DISTINCT_EVIDENCE_PRESENT"} <= states
    assert len(output["arbitration"]["evidence_ledger"]) == 4
    assert not (FORBIDDEN_ORDERING_KEYS & set().union(*(set(item) for item in output["arbitration"]["hypotheses"])))


def test_duplicate_labels_are_preserved_in_provenance_but_count_once():
    for case_id, duplicate_count in (("AR23", 3), ("AR24", 2), ("AR25", 3)):
        output = build_arbitration(_case(case_id))
        assert "DUPLICATE_EVIDENCE_DEDUPLICATED" in relationship_states(output)
        assert output["arbitration"]["evidence_ledger"][0]["duplicate_count"] == duplicate_count
        assert len(output["arbitration"]["evidence_ledger"][0]["provenance"]) == duplicate_count


def test_competition_does_not_imply_exclusivity_and_supported_diseases_can_coexist():
    competing = relationship_states(build_arbitration(_case("AR04")))
    coexist = relationship_states(build_arbitration(_case("AR06")))

    assert {"COMPETING_HYPOTHESES_PRESENT", "MUTUAL_EXCLUSIVITY_NOT_ESTABLISHED"} <= competing
    assert "COEXISTING_PROCESSES_SUPPORTED" in coexist
    assert "COEXISTING_PROCESSES_POSSIBLE" in coexist


def test_missing_is_not_negative_and_no_finding_is_not_global_exclusion():
    ar21 = build_arbitration(_case("AR21"))["arbitration"]
    ar22 = build_arbitration(_case("AR22"))["arbitration"]

    assert ar21["missing_information"] == ["BNP"]
    assert ar21["hypotheses"][1]["contradicting_evidence"] == []
    assert ar22["missing_information"] == ["TB culture"]
    assert ar22["hypotheses"][0]["contradicting_evidence"] == []
    assert "global_disease_exclusion" in _case("AR20")["forbidden"]


def test_certainty_and_safety_priority_remain_independent():
    urgent = build_arbitration(_case("AR18"))["arbitration"]
    certain = build_arbitration(_case("AR19"))["arbitration"]
    mixed = build_arbitration(_case("AR37"))["arbitration"]

    assert urgent["hypotheses"][0]["support_state"] == "HYPOTHESIS_INDETERMINATE"
    assert urgent["review"]["highest_priority"] == "high"
    assert certain["hypotheses"][0]["support_state"] == "HYPOTHESIS_SUPPORTED"
    assert certain["review"]["highest_priority"] == "routine"
    assert mixed["review"]["highest_priority"] == "high"


def test_temporal_handoff_updates_current_state_without_erasing_history():
    for case_id in ("AR28", "AR29"):
        output = build_arbitration(_case(case_id))["arbitration"]
        assert len(output["evidence_ledger"]) == 2
        assert {item["timestamp"] for item in output["evidence_ledger"]} == {"earlier", "later"}
    assert "old_naat_erased" in _case("AR28")["forbidden"]
    assert "earlier_cxr_erased" in _case("AR29")["forbidden"]


def test_conflicts_preserve_both_directions_without_silent_override():
    for case_id in ("AR30", "AR42"):
        output = build_arbitration(_case(case_id))["arbitration"]
        hypothesis = output["hypotheses"][0]
        assert hypothesis["support_state"] == "HYPOTHESIS_CONFLICTED"
        assert hypothesis["supporting_evidence"]
        assert hypothesis["contradicting_evidence"]
        assert output["global_conflicts"]


def test_treatment_timing_never_establishes_causality_or_actions():
    output = build_arbitration(_case("AR41"))["arbitration"]
    evidence = (MODULE_ROOT / "CROSS_DISEASE_ARBITRATION_EVIDENCE.md").read_text(encoding="utf-8")

    assert len(output["evidence_ledger"]) == 3
    assert "treatment_causality" in _case("AR41")["forbidden"]
    assert "treatment/action engine" in evidence
    assert "Issue autonomous treatment/testing/procedure/disposition actions" in evidence


def test_all_seven_modules_remain_finite_deduplicated_and_unranked():
    output = build_arbitration(_case("AR38"))["arbitration"]

    assert len(output["hypotheses"]) == 7
    assert len(output["evidence_ledger"]) == 8
    assert output["review"]["highest_priority"] == "high"
    assert output["synthesis"]["no_numeric_ranking"] is True
    assert not (FORBIDDEN_ORDERING_KEYS & set(_flatten_keys(output)))


def _flatten_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _flatten_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _flatten_keys(child)
