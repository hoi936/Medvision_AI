import pytest

from clinical_evaluation.reference_linkage import ReferenceLinkageError, eligible_for_final_metrics, validate_reference_linkage


def linkage(status, label=None):
    return {
        "case_id": "SYN-1", "status": status, "source_type": "synthetic",
        "source_ids": ["REF-SYN-1"] if status == "REFERENCE_COMPLETE" else [],
        "linked_at": "2026-01-02T00:00:00Z", "limitations": [], "label": label,
    }


@pytest.mark.parametrize("status", ["REFERENCE_PENDING", "REFERENCE_PARTIAL", "REFERENCE_UNAVAILABLE"])
def test_incomplete_reference_never_silently_becomes_negative(status):
    with pytest.raises(ReferenceLinkageError, match="cannot become negative"):
        validate_reference_linkage(linkage(status, False))


def test_only_complete_reference_enters_final_metrics_by_default():
    assert eligible_for_final_metrics(linkage("REFERENCE_PENDING")) is False
    assert eligible_for_final_metrics(linkage("REFERENCE_PARTIAL", "uncertain")) is False
    assert eligible_for_final_metrics(linkage("REFERENCE_COMPLETE", True)) is True
    assert eligible_for_final_metrics(linkage("REFERENCE_PARTIAL", "uncertain"), allow_partial=True) is True
