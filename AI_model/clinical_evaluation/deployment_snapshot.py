"""Version-bound deployment strata for silent evaluation."""

from __future__ import annotations

import hashlib
import json


DEPLOYMENT_FIELDS = {
    "repo_commit", "hermes_version", "hermes_commit", "python_version",
    "skill_tree_hash", "config_hash", "provider", "model", "protocol_version",
}


class DeploymentVersionMismatch(ValueError):
    def __init__(self, fields, new_stratum_id):
        self.fields = list(fields)
        self.new_stratum_id = new_stratum_id
        super().__init__(
            f"deployment version mismatch: {','.join(self.fields)}; "
            f"new stratum required: {new_stratum_id}"
        )


def build_deployment_snapshot(system_snapshot, *, protocol_version, provider_model_version=None):
    snapshot = {
        "repo_commit": system_snapshot.get("repo_commit"),
        "hermes_version": system_snapshot.get("hermes_version"),
        "hermes_commit": system_snapshot.get("hermes_commit"),
        "python_version": system_snapshot.get("python_version"),
        "skill_tree_hash": system_snapshot.get("skill_tree_hash"),
        "config_hash": system_snapshot.get("config_hash"),
        "provider": system_snapshot.get("provider"),
        "model": system_snapshot.get("model"),
        "provider_model_version": provider_model_version,
        "protocol_version": protocol_version,
        "ui_version": None,
    }
    missing = sorted(field for field in DEPLOYMENT_FIELDS if not snapshot.get(field))
    if missing:
        raise ValueError("deployment snapshot incomplete: " + ", ".join(missing))
    digest = hashlib.sha256(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    snapshot["deployment_version"] = f"DEPLOY-{digest[:16]}"
    snapshot["snapshot_hash"] = digest
    return snapshot


def validate_deployment_match(expected, observed):
    compared = DEPLOYMENT_FIELDS | {"provider_model_version"}
    mismatches = sorted(field for field in compared if expected.get(field) != observed.get(field))
    if mismatches:
        material = json.dumps(observed, sort_keys=True, separators=(",", ":")).encode("utf-8")
        raise DeploymentVersionMismatch(
            mismatches,
            f"DEPLOY-{hashlib.sha256(material).hexdigest()[:16]}",
        )
    return True
