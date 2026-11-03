from release_review.evidence_invalidation import invalidate_evidence
from release_review_fixtures import current_baseline_review


def test_invalidation_returns_exact_affected_ids_and_required_retests():
    result = invalidate_evidence(
        current_baseline_review()["evidence_inventory"],
        "MODEL_PROVIDER_IMPACT",
    )
    assert set(result["invalidated_evidence_ids"]) == {
        "EV-PROVIDER", "EV-DATASET-ACTUAL", "EV-READER-ACTUAL",
        "EV-SILENT-SCAFFOLD", "EV-SILENT-PROTOCOL", "EV-SILENT-ACTUAL",
    }
    assert "provider_preflight" in result["required_retests"]


def test_nonclinical_low_impact_does_not_invalidate_provider_evidence():
    result = invalidate_evidence(
        current_baseline_review()["evidence_inventory"],
        "NON_CLINICAL_LOW_IMPACT",
    )
    assert result["invalidated_evidence_ids"] == ["EV-REGRESSION"]
    provider = next(item for item in result["artifacts"] if item["evidence_id"] == "EV-PROVIDER")
    assert provider["status"] == "NOT_AVAILABLE"
