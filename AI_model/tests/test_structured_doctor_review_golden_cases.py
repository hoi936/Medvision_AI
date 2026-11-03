"""Provider-independent Structured Doctor Review v1 validation."""

import hashlib
import json
from pathlib import Path

import pytest

from doctor_review_validator import (
    DoctorReviewValidationError,
    build_review_case,
)
from hermes_report import FINDING_SKILL_MAP, build_report_prompt, resolve_hermes_skills


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).parent / "golden_cases" / "structured_doctor_review" / "cases.json"
SKILL_ROOT = PROJECT_ROOT / ".hermes" / "skills"
DISEASE_SKILL = SKILL_ROOT / "medvision-disease-analysis" / "SKILL.md"
MODULE_ROOT = DISEASE_SKILL.parent / "references" / "doctor_review"
EXPECTED_IDS = {f"DR{number:02d}" for number in range(1, 45)}
ALLOWED_PROVENANCE = {"S1", "S2", "S3", "S4", "S5"}
SOURCE_SHA256 = {
    "STRUCTURED_DOCTOR_REVIEW_EVIDENCE.md": "58f8de0f6d5a595b756b2dd2d8599f7ebfc7129cdacc0b43f95e56f64fd46f6e",
    "STRUCTURED_DOCTOR_REVIEW_POLICY.md": "41ee37e76482bfd6ad2f5fc36f0e756c61516ae20085f79557ddc786807286bb",
    "references.md": "9ae0e8bcfeffe19a3ed05ee75a5dd0ab02d4670cba81e7d37b99e3a8b4e38ea7",
}


def _load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case(case_id):
    return next(case for case in _load_cases() if case["id"] == case_id)


def test_pack_has_forty_four_cases_with_complete_provenance():
    cases = _load_cases()

    assert len(cases) == 44
    assert {case["id"] for case in cases} == EXPECTED_IDS
    assert all(case["provenance"] for case in cases)
    assert all(set(case["provenance"]) <= ALLOWED_PROVENANCE for case in cases)


@pytest.mark.parametrize("case", _load_cases(), ids=lambda case: case["id"])
def test_each_case_validates_expected_workflow_and_preserves_selector(case):
    prompt = build_report_prompt(**case["input"])
    data = json.loads(prompt.split("CASE_DATA\n", 1)[1].split("\nEND_CASE_DATA", 1)[0])
    selected = resolve_hermes_skills(data)

    assert selected[0] == "medvision-evidence-fusion"
    assert selected[-2:] == ["medvision-safety-check", "medvision-disease-analysis"]
    assert len(selected) == len(set(selected))
    assert "requires_doctor_review: true" in prompt

    if not case["expected_valid"]:
        with pytest.raises(DoctorReviewValidationError, match=case["expected_error"]):
            build_review_case(case)
        return

    result = build_review_case(case)
    review = result["doctor_review"]
    assert set(case["expected_states"]) <= set(result["states"])
    assert set(case.get("forbidden_states", [])) .isdisjoint(result["states"])
    assert set(case["expected_blockers"]) <= set(review["finalization"]["blocking_reasons"])
    assert result["source_fingerprints_before"] == result["source_fingerprints_after"]
    if "expected_event_count" in case:
        assert len(review["audit"]["review_events"]) == case["expected_event_count"]


def test_progressive_loading_has_no_new_skill_mapping_or_frontmatter_change():
    content = DISEASE_SKILL.read_text(encoding="utf-8")
    frontmatter = content.split("---", 2)[1]

    assert len(FINDING_SKILL_MAP) == 14
    assert "Doctor review" not in FINDING_SKILL_MAP
    assert not (SKILL_ROOT / "medvision-doctor-review").exists()
    assert "references/doctor_review/STRUCTURED_DOCTOR_REVIEW_POLICY.md" in content
    assert "references/doctor_review/STRUCTURED_DOCTOR_REVIEW_EVIDENCE.md" in content
    assert "references/doctor_review/references.md" in content
    assert "Hermes cannot act as" in content and "reviewer, acknowledge" in content
    assert "name: medvision-disease-analysis" in frontmatter
    assert "doctor_review" not in frontmatter.lower()


def test_source_files_match_inputs_and_all_required_states_are_present():
    for filename, digest in SOURCE_SHA256.items():
        assert hashlib.sha256((MODULE_ROOT / filename).read_bytes()).hexdigest() == digest

    text = "\n".join(
        (MODULE_ROOT / filename).read_text(encoding="utf-8")
        for filename in SOURCE_SHA256
    )
    states = {
        "DOCTOR_REVIEW_PENDING", "DOCTOR_REVIEW_IN_PROGRESS", "DOCTOR_REVIEW_COMPLETED",
        "DOCTOR_REVIEW_REOPENED", "FINDING_ACCEPTED", "FINDING_MODIFIED",
        "FINDING_REJECTED", "FINDING_DEFERRED", "FINDING_UNREVIEWED",
        "HYPOTHESIS_ACCEPTED", "HYPOTHESIS_MODIFIED", "HYPOTHESIS_REJECTED",
        "HYPOTHESIS_DEFERRED", "HYPOTHESIS_UNREVIEWED", "REPORT_NOT_FINAL",
        "REPORT_READY_FOR_FINALIZATION", "REPORT_FINALIZED_BY_DOCTOR",
        "REVIEW_ACKNOWLEDGED_HIGH_PRIORITY_ITEM", "REVIEW_UNRESOLVED_ITEM",
        "REVIEW_CONFLICT_PRESERVED", "REVIEW_NEW_EVIDENCE_AFTER_FINALIZATION",
    }
    assert all(state in text for state in states)
    assert all(f"## S{number}" in text for number in range(1, 6))


def test_structured_review_object_matches_required_contract():
    review = build_review_case(_case("DR29"))["doctor_review"]
    assert set(review) == {
        "review_id", "status", "version", "reviewer", "timestamps",
        "finding_reviews", "doctor_added_findings", "hypothesis_reviews",
        "conflict_reviews", "priority_item_reviews", "report_review",
        "unresolved_items", "audit", "finalization",
    }
    assert set(review["finalization"]) == {
        "readiness", "blocking_reasons", "finalized", "finalized_by", "finalized_at"
    }
    assert review["finalization"]["readiness"] == "ready"
    assert review["finalization"]["finalized"] is False


def test_review_actions_do_not_mutate_any_upstream_snapshot():
    for case_id in ("DR04", "DR05", "DR11", "DR21", "DR30", "DR34", "DR39"):
        result = build_review_case(_case(case_id))
        assert result["source_fingerprints_before"] == result["source_fingerprints_after"]
    rejected = build_review_case(_case("DR04"))
    assert rejected["source_snapshots"]["ai"]["findings"][0]["decision"] == "POSITIVE"
    assert rejected["doctor_review"]["finding_reviews"][0]["state"] == "FINDING_REJECTED"


def test_doctor_modifications_and_added_findings_remain_clinician_authored():
    modified = build_review_case(_case("DR05"))
    added = build_review_case(_case("DR09"))

    finding = modified["doctor_review"]["finding_reviews"][0]
    assert finding["ai_state"] == "Pleural effusion POSITIVE"
    assert finding["doctor_value"] == "small right pleural effusion"
    assert finding["doctor_value_provenance"] == "clinician"
    assert added["doctor_review"]["doctor_added_findings"][0]["source"] == "DOCTOR_REVIEW"
    assert added["source_snapshots"]["ai"]["findings"] == [{"name": "Nodule/Mass", "decision": "POSITIVE"}]


def test_finding_and_hypothesis_decisions_remain_independent():
    review = build_review_case(_case("DR15"))["doctor_review"]
    assert review["finding_reviews"][0]["state"] == "FINDING_ACCEPTED"
    assert review["hypothesis_reviews"][0]["state"] == "HYPOTHESIS_REJECTED"
    distinct = build_review_case(_case("DR16"))["doctor_review"]
    assert distinct["finding_reviews"][0]["state"] == "FINDING_REJECTED"
    assert distinct["hypothesis_reviews"][0]["state"] == "HYPOTHESIS_ACCEPTED"


def test_acceptance_never_manufactures_disease_confirmation():
    pneumonia = build_review_case(_case("DR10"))["doctor_review"]["hypothesis_reviews"][0]
    tb = build_review_case(_case("DR36"))["doctor_review"]["hypothesis_reviews"][0]
    malignancy = build_review_case(_case("DR37"))["doctor_review"]["hypothesis_reviews"][0]

    assert pneumonia["hermes_state"] == "PNEUMONIA_HYPOTHESIS_SUPPORTED"
    assert tb["hermes_state"] == "PULMONARY_TB_CONCERN_SUPPORTED"
    assert malignancy["hermes_state"] == "PULMONARY_MALIGNANCY_CONCERN_SUPPORTED"
    assert all(item["state"] == "HYPOTHESIS_ACCEPTED" for item in (pneumonia, tb, malignancy))
    assert all("CONFIRMED" not in item["hermes_state"] for item in (pneumonia, tb, malignancy))


def test_high_priority_acknowledgement_is_explicit_and_not_acceptance():
    blocked = build_review_case(_case("DR17"))["doctor_review"]
    deferred = build_review_case(_case("DR18"))

    assert "high_priority_item_unacknowledged" in blocked["finalization"]["blocking_reasons"]
    assert "REVIEW_ACKNOWLEDGED_HIGH_PRIORITY_ITEM" in deferred["states"]
    assert deferred["doctor_review"]["priority_item_reviews"][0]["decision"] == "defer"
    assert deferred["doctor_review"]["hypothesis_reviews"][0]["state"] == "HYPOTHESIS_DEFERRED"


def test_conflict_can_be_preserved_or_resolved_without_history_erasure():
    preserved = build_review_case(_case("DR20"))
    resolved = build_review_case(_case("DR21"))

    assert "REVIEW_CONFLICT_PRESERVED" in preserved["states"]
    assert "REVIEW_UNRESOLVED_ITEM" in preserved["states"]
    assert resolved["doctor_review"]["conflict_reviews"][0]["decision"] == "resolve"
    assert resolved["doctor_review"]["audit"]["review_events"][0]["before"] == "unresolved"


def test_readiness_and_finalization_are_distinct_external_transitions():
    ready = build_review_case(_case("DR29"))
    finalized = build_review_case(_case("DR30"))

    assert "REPORT_READY_FOR_FINALIZATION" in ready["states"]
    assert "REPORT_FINALIZED_BY_DOCTOR" not in ready["states"]
    assert "REPORT_FINALIZED_BY_DOCTOR" in finalized["states"]
    assert finalized["doctor_review"]["finalization"]["finalized_by"] == "DOC-1"
    for case_id in ("DR27", "DR31", "DR32"):
        case = _case(case_id)
        with pytest.raises(DoctorReviewValidationError, match=case["expected_error"]):
            build_review_case(case)


def test_reopen_and_post_finalization_new_evidence_preserve_old_record():
    before = build_review_case(_case("DR33"))
    after = build_review_case(_case("DR34"))

    assert "DOCTOR_REVIEW_REOPENED" in before["states"]
    assert "REPORT_NOT_FINAL" in before["states"]
    assert "REPORT_FINALIZED_BY_DOCTOR" in after["states"]
    assert "REVIEW_NEW_EVIDENCE_AFTER_FINALIZATION" in after["states"]
    assert after["source_fingerprints_before"] == after["source_fingerprints_after"]


def test_audit_events_are_append_only_ordered_and_retain_before_after():
    review = build_review_case(_case("DR39"))["doctor_review"]
    events = review["audit"]["review_events"]

    assert [item["event_id"] for item in events] == ["R1", "R2"]
    assert events[1]["before"] == "accepted"
    assert events[1]["after"] == "small right pleural effusion"
    version_two = build_review_case(_case("DR40"))["doctor_review"]
    assert version_two["version"] == 2
    assert [item["event_id"] for item in version_two["audit"]["review_events"]] == ["V1-R1", "V2-R1"]


def test_missing_snapshot_reference_is_flagged_without_fabrication():
    result = build_review_case(_case("DR41"))
    assert result["doctor_review"]["audit"]["ai_snapshot_id"] is None
    assert "source_snapshot_reference_missing" in result["doctor_review"]["finalization"]["blocking_reasons"]


def test_raw_ai_cannot_skip_review_or_promote_directly_to_final_report():
    result = build_review_case(_case("DR42"))
    assert "DOCTOR_REVIEW_PENDING" in result["states"]
    assert "REPORT_NOT_FINAL" in result["states"]
    assert result["doctor_review"]["finalization"]["finalized"] is False


def test_all_frozen_module_handoffs_are_represented_without_semantic_rewrite():
    cases = _load_cases()
    combined = " ".join(case["input"]["history"] for case in cases).lower()
    for term in (
        "pneumonia", "hf", "malignancy", "aas", "pathology", "pleural",
        "tb", "uncertainty", "conflict",
    ):
        assert term in combined
