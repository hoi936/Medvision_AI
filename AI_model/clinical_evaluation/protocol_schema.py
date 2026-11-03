"""Silent-shadow protocol schema with explicit governance fields."""

from __future__ import annotations

from .silent_isolation import validate_silent_isolation


class ClinicalProtocolError(ValueError):
    pass


def _mapping(value, label):
    if not isinstance(value, dict):
        raise ClinicalProtocolError(f"{label} must be an object")


def validate_silent_protocol(protocol):
    _mapping(protocol, "silent protocol")
    required = {
        "protocol_id", "version", "objective", "mode", "data_sources",
        "eligibility", "evaluation_window", "reference_linkage_rules",
        "system_snapshot", "provider_requirements", "isolation",
        "ethics", "privacy", "security",
    }
    missing = sorted(required - set(protocol))
    if missing:
        raise ClinicalProtocolError(f"silent protocol missing fields: {', '.join(missing)}")
    for field in ("protocol_id", "version", "objective"):
        if not isinstance(protocol[field], str) or not protocol[field].strip():
            raise ClinicalProtocolError(f"{field} must be non-empty")
    if protocol["mode"] != "SILENT_SHADOW":
        raise ClinicalProtocolError("silent protocol mode must be SILENT_SHADOW")
    if not isinstance(protocol["data_sources"], list) or not protocol["data_sources"]:
        raise ClinicalProtocolError("silent protocol requires explicit data sources")
    for field in (
        "eligibility", "evaluation_window", "reference_linkage_rules",
        "system_snapshot", "provider_requirements", "ethics", "privacy", "security",
    ):
        _mapping(protocol[field], field)
    if not protocol["eligibility"].get("criteria"):
        raise ClinicalProtocolError("eligibility criteria must be pre-specified")
    if not all(protocol["evaluation_window"].get(key) for key in ("start", "end")):
        raise ClinicalProtocolError("evaluation window must be pre-specified")
    if not protocol["reference_linkage_rules"].get("rules"):
        raise ClinicalProtocolError("reference linkage rules must be pre-specified")
    snapshot = protocol["system_snapshot"]
    required_snapshot = {
        "repo_commit", "hermes_version", "hermes_commit", "python_version",
        "skill_tree_hash", "config_hash", "provider", "model", "snapshot_hash",
    }
    if any(not snapshot.get(field) for field in required_snapshot):
        raise ClinicalProtocolError("deployment system snapshot is incomplete")
    provider = protocol["provider_requirements"]
    if provider.get("strategy") not in {"LIVE_PINNED_PROVIDER", "FROZEN_OUTPUTS"}:
        raise ClinicalProtocolError("provider strategy must be explicit")
    validate_silent_isolation(protocol["isolation"])
    for name in ("ethics", "privacy", "security"):
        if "status" not in protocol[name] or "reference" not in protocol[name]:
            raise ClinicalProtocolError(f"{name} status/reference is incomplete")
    return protocol
