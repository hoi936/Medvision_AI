"""Invalidate only evidence families affected by an explicit change class."""

from __future__ import annotations

from copy import deepcopy

from .change_impact import classify_change


def invalidate_evidence(artifacts, impact_class):
    impact = classify_change(impact_class)
    affected_families = set(impact["evidence_families"])
    output = []
    invalidated_ids = []
    for source in artifacts:
        artifact = deepcopy(source)
        if artifact.get("dependency_family") in affected_families:
            artifact["status_before_invalidation"] = artifact["status"]
            artifact["status"] = "INVALIDATED"
            artifact["invalidation_reason"] = impact_class
            invalidated_ids.append(artifact["evidence_id"])
        output.append(artifact)
    return {
        "artifacts": output,
        "invalidated_evidence_ids": invalidated_ids,
        "required_retests": impact["required_retests"],
    }
