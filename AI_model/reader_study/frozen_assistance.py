"""Immutable, one-output-per-case Hermes assistance snapshots."""

from __future__ import annotations

import hashlib


VALIDATION_STATES = {"VALIDATED", "REJECTED"}


class FrozenAssistanceError(ValueError):
    pass


def assistance_hash(output):
    if not isinstance(output, str) or not output.strip():
        raise FrozenAssistanceError("Hermes output must be non-empty text")
    return hashlib.sha256(output.encode("utf-8")).hexdigest()


def freeze_assistance(
    *, case_id, output, study_version, system_snapshot, provider, model,
    generated_at, validation_state, ui_version,
):
    if validation_state not in VALIDATION_STATES:
        raise FrozenAssistanceError("invalid assistance validation state")
    required_snapshot = {"repo_commit", "hermes_version", "hermes_commit", "skill_tree_hash", "snapshot_hash"}
    if not isinstance(system_snapshot, dict) or any(not system_snapshot.get(key) for key in required_snapshot):
        raise FrozenAssistanceError("system snapshot is incomplete")
    if not provider or not model or not ui_version:
        raise FrozenAssistanceError("provider, model, and UI version are required")
    digest = assistance_hash(output)
    return {
        "case_id": case_id,
        "study_version": study_version,
        "assistance_snapshot_id": f"ASSIST-{study_version}-{case_id}-{digest[:12]}",
        "hermes_output": output,
        "hermes_output_hash": digest,
        "repo_commit": system_snapshot["repo_commit"],
        "hermes_version": system_snapshot["hermes_version"],
        "hermes_commit": system_snapshot["hermes_commit"],
        "skill_tree_hash": system_snapshot["skill_tree_hash"],
        "system_snapshot_hash": system_snapshot["snapshot_hash"],
        "provider": provider,
        "model": model,
        "generated_at": generated_at,
        "validation_state": validation_state,
        "ui_version": ui_version,
        "finalized": False,
    }


def validate_frozen_assistance(records, *, case_ids, study_version, ui_version=None):
    if not isinstance(records, list):
        raise FrozenAssistanceError("frozen assistance manifest must be a list")
    by_case = {}
    for record in records:
        required = {
            "case_id", "study_version", "assistance_snapshot_id", "hermes_output",
            "hermes_output_hash", "repo_commit", "hermes_version", "hermes_commit",
            "skill_tree_hash", "system_snapshot_hash", "provider", "model",
            "generated_at", "validation_state", "ui_version", "finalized",
        }
        missing = sorted(required - set(record))
        if missing or any(record.get(field) in (None, "") for field in required - {"finalized"}):
            raise FrozenAssistanceError(
                "frozen assistance metadata is incomplete"
                + (f": {', '.join(missing)}" if missing else "")
            )
        case_id = record.get("case_id")
        if case_id in by_case:
            raise FrozenAssistanceError(f"multiple assistance snapshots for case {case_id}")
        if record.get("study_version") != study_version:
            raise FrozenAssistanceError("assistance study version mismatch")
        if ui_version is not None and record.get("ui_version") != ui_version:
            raise FrozenAssistanceError("assistance UI version mismatch")
        if assistance_hash(record.get("hermes_output")) != record.get("hermes_output_hash"):
            raise FrozenAssistanceError(f"assistance hash mismatch for case {case_id}")
        if record.get("validation_state") != "VALIDATED":
            raise FrozenAssistanceError(f"assistance is not validated for case {case_id}")
        if record.get("finalized") is not False:
            raise FrozenAssistanceError("Hermes assistance cannot be presented as finalized")
        by_case[case_id] = record
    expected = set(case_ids)
    if set(by_case) != expected:
        missing = sorted(expected - set(by_case))
        extra = sorted(set(by_case) - expected)
        raise FrozenAssistanceError(f"assistance case mismatch; missing={missing}, extra={extra}")
    return by_case


def validate_event_assistance_bindings(events, assistance_by_case):
    observed = {}
    for event in events:
        if event.get("condition") != "HERMES_ASSISTED":
            continue
        case_id = event["case_id"]
        if case_id not in assistance_by_case:
            raise FrozenAssistanceError(f"no frozen assistance for case {case_id}")
        expected = assistance_by_case[case_id]["assistance_snapshot_id"]
        if event.get("hermes_snapshot_id") != expected:
            raise FrozenAssistanceError(f"assistance snapshot mismatch for case {case_id}")
        observed.setdefault(case_id, set()).add(event["hermes_snapshot_id"])
    if any(len(snapshot_ids) != 1 for snapshot_ids in observed.values()):
        raise FrozenAssistanceError("assisted readers received inconsistent snapshots")
    return True
