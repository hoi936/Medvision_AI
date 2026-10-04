"""Deterministic Structured Doctor Review v1 schema and boundary validator."""

from copy import deepcopy
import hashlib
import json


FINDING_STATES = {
    "accept": "FINDING_ACCEPTED",
    "modify": "FINDING_MODIFIED",
    "reject": "FINDING_REJECTED",
    "defer": "FINDING_DEFERRED",
    "unreviewed": "FINDING_UNREVIEWED",
}
HYPOTHESIS_STATES = {
    "accept": "HYPOTHESIS_ACCEPTED",
    "modify": "HYPOTHESIS_MODIFIED",
    "reject": "HYPOTHESIS_REJECTED",
    "defer": "HYPOTHESIS_DEFERRED",
    "unreviewed": "HYPOTHESIS_UNREVIEWED",
}
REVIEW_STATES = {
    "pending": "DOCTOR_REVIEW_PENDING",
    "in_progress": "DOCTOR_REVIEW_IN_PROGRESS",
    "completed": "DOCTOR_REVIEW_COMPLETED",
    "reopened": "DOCTOR_REVIEW_REOPENED",
}


class DoctorReviewValidationError(ValueError):
    """Fail-closed review-contract error."""


def fingerprint(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def source_snapshots(mode="complete"):
    """Return deterministic upstream fixtures supplied to the review validator."""
    snapshots = {
        "ai": {"id": "AI-SNAPSHOT-1", "findings": [{"name": "Nodule/Mass", "decision": "POSITIVE"}]},
        "hermes": {"id": "HERMES-SNAPSHOT-1", "states": ["HYPOTHESIS_POSSIBLE"]},
        "draft": {"id": "DRAFT-SNAPSHOT-1", "status": "DRAFT_REPORT", "text": "draft"},
    }
    if mode == "missing_ai":
        snapshots["ai"] = {"id": None, "findings": snapshots["ai"]["findings"]}
    elif mode == "missing_hermes":
        snapshots["hermes"] = {"id": None, "states": snapshots["hermes"]["states"]}
    elif mode == "missing_draft":
        snapshots["draft"] = {"id": None, "status": "DRAFT_REPORT", "text": "draft"}
    return snapshots


def _validate_events(events):
    ids = [event.get("event_id") for event in events]
    if None in ids or len(ids) != len(set(ids)):
        raise DoctorReviewValidationError("AUDIT_EVENT_IDS_NOT_UNIQUE")
    timestamps = [event.get("timestamp") for event in events if event.get("timestamp")]
    if timestamps != sorted(timestamps):
        raise DoctorReviewValidationError("AUDIT_EVENT_ORDER_INVALID")
    for event in events:
        if not event.get("actor_role") or not event.get("source"):
            raise DoctorReviewValidationError("AUDIT_ACTOR_OR_SOURCE_MISSING")
        if event.get("action") == "modify" and (
            "before" not in event or "after" not in event
        ):
            raise DoctorReviewValidationError("AUDIT_MODIFICATION_BEFORE_AFTER_MISSING")


def _readiness(review):
    blockers = []
    if review["status"] != "completed":
        blockers.append("review_status_not_completed")
    if not review["reviewer"]["id"]:
        blockers.append("reviewer_id_missing")
    if not review["timestamps"]["completed_at"]:
        blockers.append("completion_timestamp_missing")
    if any(item["required"] and item["decision"] == "unreviewed" for item in review["finding_reviews"]):
        blockers.append("required_finding_unreviewed")
    if any(item["required"] and item["decision"] == "unreviewed" for item in review["hypothesis_reviews"]):
        blockers.append("required_hypothesis_unreviewed")
    if any(item["priority"] == "high" and not item["acknowledged"] for item in review["priority_item_reviews"]):
        blockers.append("high_priority_item_unacknowledged")
    report_review = review["report_review"]
    if not any(report_review[key] for key in ("doctor_impression", "doctor_findings_text", "doctor_comment")):
        blockers.append("doctor_owned_report_text_missing")
    deferred_ids = {
        item["finding_id"] for item in review["finding_reviews"] if item["decision"] == "defer"
    } | {
        item["hypothesis_id"] for item in review["hypothesis_reviews"] if item["decision"] == "defer"
    }
    unresolved_ids = {item["item_id"] for item in review["unresolved_items"]}
    if deferred_ids - unresolved_ids:
        blockers.append("deferred_item_not_explicitly_unresolved")
    if any(item["decision"] is None for item in review["conflict_reviews"]):
        blockers.append("conflict_review_missing")
    if any(not review["audit"][key] for key in ("ai_snapshot_id", "hermes_snapshot_id", "draft_report_snapshot_id")):
        blockers.append("source_snapshot_reference_missing")
    return blockers


def validate_doctor_review(review, *, reviewer_source=None, finalizer_source=None):
    """Validate review ownership, audit history, readiness, and finalization."""
    if review["status"] not in REVIEW_STATES:
        raise DoctorReviewValidationError("INVALID_REVIEW_STATUS")
    if review["reviewer"]["id"] and reviewer_source != "authenticated_doctor":
        raise DoctorReviewValidationError("REVIEWER_IDENTITY_NOT_HOST_AUTHENTICATED")
    for item in review["priority_item_reviews"]:
        if item["acknowledged"] and item.get("acknowledged_by_source") != "authenticated_doctor":
            raise DoctorReviewValidationError("HIGH_PRIORITY_AUTO_ACKNOWLEDGEMENT_FORBIDDEN")
    _validate_events(review["audit"]["review_events"])

    blockers = _readiness(review)
    review["finalization"]["blocking_reasons"] = blockers
    review["finalization"]["readiness"] = "ready" if not blockers else "not_ready"
    report_state = "REPORT_READY_FOR_FINALIZATION" if not blockers else "REPORT_NOT_FINAL"

    finalized = review["finalization"]["finalized"]
    if finalized:
        if finalizer_source != "authenticated_doctor":
            raise DoctorReviewValidationError("HERMES_AUTO_FINALIZATION_FORBIDDEN")
        if blockers:
            raise DoctorReviewValidationError("FINALIZATION_NOT_READY")
        if not review["finalization"]["finalized_by"]:
            raise DoctorReviewValidationError("FINALIZED_BY_MISSING")
        if not review["finalization"]["finalized_at"]:
            raise DoctorReviewValidationError("FINALIZED_AT_MISSING")
        report_state = "REPORT_FINALIZED_BY_DOCTOR"
    elif review["finalization"].get("finalized_by") or review["finalization"].get("finalized_at"):
        raise DoctorReviewValidationError("FINALIZATION_METADATA_WITHOUT_FINALIZATION")

    states = [REVIEW_STATES[review["status"]], report_state]
    states.extend(item["state"] for item in review["finding_reviews"])
    states.extend(item["state"] for item in review["hypothesis_reviews"])
    if any(item["acknowledged"] and item["priority"] == "high" for item in review["priority_item_reviews"]):
        states.append("REVIEW_ACKNOWLEDGED_HIGH_PRIORITY_ITEM")
    if review["unresolved_items"]:
        states.append("REVIEW_UNRESOLVED_ITEM")
    if any(item["decision"] == "preserve" for item in review["conflict_reviews"]):
        states.append("REVIEW_CONFLICT_PRESERVED")
    return states


def build_review_case(case):
    """Build a full review object from explicit fixture facts without mutating sources."""
    cfg = case["review"]
    sources = source_snapshots(cfg.get("snapshot_mode", "complete"))
    before = {name: fingerprint(value) for name, value in sources.items()}

    finding_reviews = []
    for item in cfg.get("findings", []):
        decision = item.get("decision", "unreviewed")
        finding_reviews.append({
            "finding_id": item["id"],
            "ai_snapshot_ref": sources["ai"]["id"],
            "ai_state": item.get("ai_state"),
            "decision": decision,
            "state": FINDING_STATES[decision],
            "required": item.get("required", True),
            "doctor_value": item.get("doctor_value"),
            "doctor_value_provenance": "clinician" if item.get("doctor_value") is not None else None,
            "comment": item.get("comment"),
            "reviewed_at": item.get("reviewed_at"),
        })

    hypothesis_reviews = []
    for item in cfg.get("hypotheses", []):
        decision = item.get("decision", "unreviewed")
        hypothesis_reviews.append({
            "hypothesis_id": item["id"],
            "hermes_snapshot_ref": sources["hermes"]["id"],
            "hermes_state": item.get("hermes_state"),
            "decision": decision,
            "state": HYPOTHESIS_STATES[decision],
            "required": item.get("required", True),
            "doctor_assessment": item.get("doctor_assessment"),
            "doctor_assessment_provenance": "clinician" if item.get("doctor_assessment") is not None else None,
            "comment": item.get("comment"),
            "reviewed_at": item.get("reviewed_at"),
        })

    reviewer_id = cfg.get("reviewer_id")
    review = {
        "review_id": cfg.get("review_id"),
        "status": cfg.get("status", "pending"),
        "version": cfg.get("version", 1),
        "reviewer": {"id": reviewer_id, "role": "physician", "display_name": cfg.get("reviewer_name")},
        "timestamps": {"started_at": cfg.get("started_at"), "completed_at": cfg.get("completed_at")},
        "finding_reviews": finding_reviews,
        "doctor_added_findings": [
            {**item, "source": "DOCTOR_REVIEW", "provenance": "clinician"}
            for item in cfg.get("doctor_added_findings", [])
        ],
        "hypothesis_reviews": hypothesis_reviews,
        "conflict_reviews": [
            {"conflict_id": item["id"], "decision": item.get("decision"), "resolution": item.get("resolution")}
            for item in cfg.get("conflicts", [])
        ],
        "priority_item_reviews": [
            {
                "item_id": item["id"], "priority": item["priority"],
                "acknowledged": item.get("acknowledged", False),
                "acknowledged_by_source": item.get("acknowledged_by_source"),
                "decision": item.get("decision"),
            }
            for item in cfg.get("priority_items", [])
        ],
        "report_review": {
            "draft_snapshot_ref": sources["draft"]["id"],
            "doctor_impression": cfg.get("doctor_impression"),
            "doctor_findings_text": cfg.get("doctor_findings_text"),
            "doctor_comment": cfg.get("doctor_comment"),
        },
        "unresolved_items": [
            {"item_id": item_id} for item_id in cfg.get("unresolved_items", [])
        ],
        "audit": {
            "ai_snapshot_id": sources["ai"]["id"],
            "hermes_snapshot_id": sources["hermes"]["id"],
            "draft_report_snapshot_id": sources["draft"]["id"],
            "review_events": deepcopy(cfg.get("events", [])),
        },
        "finalization": {
            "readiness": "not_ready",
            "blocking_reasons": [],
            "finalized": cfg.get("finalized", False),
            "finalized_by": cfg.get("finalized_by"),
            "finalized_at": cfg.get("finalized_at"),
        },
    }

    new_evidence = cfg.get("new_evidence")
    extra_states = []
    if new_evidence == "before_finalization":
        review["status"] = "reopened"
        review["finalization"]["finalized"] = False
    elif new_evidence == "after_finalization":
        extra_states.append("REVIEW_NEW_EVIDENCE_AFTER_FINALIZATION")

    states = validate_doctor_review(
        review,
        reviewer_source=cfg.get("reviewer_source"),
        finalizer_source=cfg.get("finalizer_source"),
    )
    after = {name: fingerprint(value) for name, value in sources.items()}
    if before != after:
        raise DoctorReviewValidationError("SOURCE_SNAPSHOT_MUTATED")
    return {
        "doctor_review": review,
        "states": states + extra_states,
        "source_snapshots": sources,
        "source_fingerprints_before": before,
        "source_fingerprints_after": after,
    }
