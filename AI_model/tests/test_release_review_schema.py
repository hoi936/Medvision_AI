import pytest

from release_review.evidence_inventory import EvidenceInventory, EvidenceInventoryError
from release_review.readiness import ReleaseReviewHarness, ReleaseReviewState, TargetStage
from release_review.review_schema import validate_review
from release_review_fixtures import current_baseline_review


def test_current_baseline_fixture_is_valid_metadata_not_release_approval():
    review = validate_review(current_baseline_review())
    assert review["system_snapshot"]["evaluation_artifact_versions"]["regression"] == "997-passed-365-skipped"
    assert review["provider"]["configured"] is False
    assert review["governance_approval"]["status"] == "PENDING"


def test_all_target_stages_and_states_are_explicit():
    assert {item.value for item in TargetStage} == {
        "INTERNAL_RESEARCH", "OFFLINE_DATASET_EVALUATION", "READER_STUDY",
        "SILENT_EVALUATION", "INTERVENTIONAL_STUDY", "PRODUCTION_CLINICAL_USE",
    }
    assert {item.value for item in ReleaseReviewState} == {
        "RELEASE_REVIEW_SCAFFOLD_READY", "RELEASE_REVIEW_INCOMPLETE", "RELEASE_BLOCKED",
        "CONDITIONAL_REVIEW_REQUIRED", "READY_FOR_NEXT_GOVERNED_STAGE", "RELEASE_REVIEW_FAILED",
    }
    assert ReleaseReviewHarness().scaffold_status().state == ReleaseReviewState.RELEASE_REVIEW_SCAFFOLD_READY


def test_evidence_file_existence_does_not_infer_pass():
    artifact = current_baseline_review()["evidence_inventory"][3]
    assert artifact["path_or_reference"]
    assert EvidenceInventory([artifact]).passed_categories() == set()


def test_evidence_status_and_maturity_are_explicit():
    artifact = current_baseline_review()["evidence_inventory"][0]
    artifact["status"] = "UNKNOWN"
    with pytest.raises(EvidenceInventoryError, match="status"):
        EvidenceInventory([artifact])


def test_duplicate_evidence_id_fails_review_consistency_check():
    review = current_baseline_review()
    review["evidence_inventory"].append(dict(review["evidence_inventory"][0]))
    decision = ReleaseReviewHarness().assess(review)
    assert decision.state == ReleaseReviewState.RELEASE_REVIEW_FAILED
    assert "duplicate evidence_id" in decision.blockers[0]
