"""Frozen release-candidate snapshot schema."""

from __future__ import annotations


SNAPSHOT_FIELDS = {
    "repository_commit", "hermes_version", "hermes_commit", "python_version",
    "provider", "model", "provider_model_version", "skill_tree_hash", "config_hash",
    "ui_version", "evaluation_artifact_versions", "snapshot_hash",
}


class SystemSnapshotError(ValueError):
    pass


def validate_system_snapshot(snapshot):
    if not isinstance(snapshot, dict):
        raise SystemSnapshotError("system snapshot must be an object")
    missing = sorted(SNAPSHOT_FIELDS - set(snapshot))
    if missing:
        raise SystemSnapshotError("system snapshot missing fields: " + ", ".join(missing))
    required_values = SNAPSHOT_FIELDS - {"provider_model_version", "ui_version"}
    empty = sorted(field for field in required_values if not snapshot.get(field))
    if empty:
        raise SystemSnapshotError("system snapshot has empty fields: " + ", ".join(empty))
    if not isinstance(snapshot["evaluation_artifact_versions"], dict):
        raise SystemSnapshotError("evaluation_artifact_versions must be an object")
    return snapshot
