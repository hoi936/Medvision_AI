"""Delayed reference linkage without missing-to-negative coercion."""

from __future__ import annotations


REFERENCE_STATES = {
    "REFERENCE_PENDING", "REFERENCE_PARTIAL", "REFERENCE_COMPLETE", "REFERENCE_UNAVAILABLE",
}


class ReferenceLinkageError(ValueError):
    pass


def validate_reference_linkage(linkage):
    if not isinstance(linkage, dict):
        raise ReferenceLinkageError("reference linkage must be an object")
    required = {"case_id", "status", "source_type", "source_ids", "linked_at", "limitations", "label"}
    missing = sorted(required - set(linkage))
    if missing:
        raise ReferenceLinkageError("reference linkage missing fields: " + ", ".join(missing))
    if linkage["status"] not in REFERENCE_STATES:
        raise ReferenceLinkageError("invalid reference status")
    if not isinstance(linkage["source_ids"], list) or not isinstance(linkage["limitations"], list):
        raise ReferenceLinkageError("reference provenance and limitations must be lists")
    if linkage["status"] == "REFERENCE_COMPLETE":
        if not linkage["source_type"] or not linkage["source_ids"] or linkage["label"] is None:
            raise ReferenceLinkageError("complete reference requires provenance and label")
    elif linkage["label"] is False or linkage["label"] == "EXPLICIT_NEGATIVE":
        raise ReferenceLinkageError("pending/partial/unavailable reference cannot become negative")
    return linkage


def eligible_for_final_metrics(linkage, *, allow_partial=False):
    validate_reference_linkage(linkage)
    return linkage["status"] == "REFERENCE_COMPLETE" or (
        allow_partial and linkage["status"] == "REFERENCE_PARTIAL"
    )
