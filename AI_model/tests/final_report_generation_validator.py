"""Deterministic Final Report Generation v1 boundary validator.

This test helper validates rendering contracts. It deliberately does not
perform clinical inference, issue actions, or finalize a report.
"""

from copy import deepcopy
import hashlib
import json


class FinalReportValidationError(ValueError):
    """Fail-closed final-report contract error."""


ALLOWED_RECOMMENDATION_SOURCES = {
    "doctor_authored",
    "external_clinician_approved",
}


def fingerprint(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _blank_candidate():
    return {
        "report_status": "candidate",
        "source_review_id": None,
        "source_review_version": None,
        "patient_study": {
            "patient_id": None,
            "study_id": None,
            "exam": None,
            "exam_datetime": None,
        },
        "clinical_information": {"indication": None},
        "technique": {"text": None},
        "comparison": {"text": None},
        "findings": {"text": None, "structured_items": []},
        "impression": {"text": None, "structured_items": []},
        "recommendations": {"text": None, "source": None},
        "limitations": [],
        "unresolved_items": [],
        "provenance": {
            "ai_snapshot_id": None,
            "hermes_snapshot_id": None,
            "draft_report_snapshot_id": None,
            "doctor_review_id": None,
            "doctor_review_version": None,
        },
        "finalization": {
            "finalized": False,
            "finalized_by": None,
            "finalized_at": None,
        },
    }


def _blocked(status, reasons):
    return {"states": [status], "blocking_reasons": reasons, "final_report_candidate": None}


def _normalize_review(review):
    """Accept the native Structured Doctor Review v1 object without mutating it."""
    if "finalization" not in review:
        return deepcopy(review)
    report_review = review.get("report_review", {})
    return {
        "id": review.get("review_id"),
        "version": review.get("version"),
        "status": review.get("status"),
        "readiness": review.get("finalization", {}).get("readiness"),
        "blocking_reasons": deepcopy(review.get("finalization", {}).get("blocking_reasons", [])),
        "reviewer_id": review.get("reviewer", {}).get("id"),
        "completed_at": review.get("timestamps", {}).get("completed_at"),
        "doctor_owned_report_text": any(
            report_review.get(key)
            for key in ("doctor_impression", "doctor_findings_text", "doctor_comment")
        ),
        "doctor_findings_text": report_review.get("doctor_findings_text"),
        "doctor_impression": report_review.get("doctor_impression"),
        "findings": [
            {
                "id": item["finding_id"], "decision": item["decision"],
                "reviewed_value": item.get("ai_state"),
                "doctor_value": item.get("doctor_value"),
                "required": item.get("required", True),
            }
            for item in review.get("finding_reviews", [])
        ],
        "hypotheses": [
            {
                "id": item["hypothesis_id"], "decision": item["decision"],
                "reviewed_value": item.get("hermes_state"),
                "doctor_value": item.get("doctor_assessment"),
                "required": item.get("required", True),
            }
            for item in review.get("hypothesis_reviews", [])
        ],
        "doctor_added_findings": [
            {"id": f"doctor-added-{index}", "text": item.get("finding"), "reviewed": True}
            for index, item in enumerate(review.get("doctor_added_findings", []), start=1)
        ],
        "priority_items": deepcopy(review.get("priority_item_reviews", [])),
        "unresolved_items": [item.get("item_id") for item in review.get("unresolved_items", [])],
        "limitations": [],
    }


def _render_reviewed_items(items, kind):
    rendered = []
    for item in items:
        decision = item.get("decision", "unreviewed")
        if decision == "unreviewed" and item.get("required", True):
            raise FinalReportValidationError(f"REQUIRED_{kind.upper()}_UNREVIEWED")
        if decision == "reject":
            continue
        if decision == "defer":
            if item.get("retained_uncertainty"):
                rendered.append({
                    "id": item["id"],
                    "text": item["retained_uncertainty"],
                    "decision": "defer",
                    "source": "doctor_review",
                })
            continue
        if decision == "modify":
            text = item.get("doctor_value")
            if not text:
                raise FinalReportValidationError(f"MODIFIED_{kind.upper()}_VALUE_MISSING")
            source = "doctor_authored"
        elif decision == "accept":
            text = item.get("reviewed_value")
            source = "doctor_accepted_upstream"
        else:
            continue
        rendered.append({"id": item["id"], "text": text, "decision": decision, "source": source})
    return rendered


def render_final_report(config):
    """Render a candidate strictly from an explicit completed review contract."""
    raw_review = config.get("doctor_review")
    audit = raw_review.get("audit", {}) if isinstance(raw_review, dict) else {}
    source = deepcopy(config.get("source") or {
        "ai_snapshot_id": audit.get("ai_snapshot_id"),
        "hermes_snapshot_id": audit.get("hermes_snapshot_id"),
        "draft_report_snapshot_id": audit.get("draft_report_snapshot_id"),
    })
    source_before = fingerprint(source)

    if config.get("request_source") in {"raw_ai", "unreviewed_hermes", "draft_report"}:
        return _blocked("FINAL_REPORT_NOT_GENERATABLE", ["structured_doctor_review_required"])

    if not raw_review:
        return _blocked("FINAL_REPORT_NOT_GENERATABLE", ["doctor_review_missing"])
    review = _normalize_review(raw_review)

    review_blockers = list(review.get("blocking_reasons", []))
    if review.get("status") != "completed":
        review_blockers.append("review_status_not_completed")
    if review.get("readiness") != "ready":
        review_blockers.append("review_readiness_not_ready")
    if not review.get("reviewer_id"):
        review_blockers.append("reviewer_id_missing")
    if not review.get("completed_at"):
        review_blockers.append("completion_timestamp_missing")
    if not review.get("doctor_owned_report_text"):
        review_blockers.append("doctor_owned_report_text_missing")
    if any(
        item.get("priority") == "high" and not item.get("acknowledged")
        for item in review.get("priority_items", [])
    ):
        review_blockers.append("high_priority_item_unacknowledged")
    if review_blockers:
        return _blocked("FINAL_REPORT_BLOCKED_BY_REVIEW", list(dict.fromkeys(review_blockers)))

    candidate_binding = config.get("candidate_binding", {})
    if candidate_binding.get("review_version") not in (None, review.get("version")):
        return _blocked("FINAL_REPORT_VERSION_MISMATCH", ["source_review_version_changed"])

    required_snapshot_keys = ("ai_snapshot_id", "hermes_snapshot_id", "draft_report_snapshot_id")
    if not review.get("id") or review.get("version") is None:
        return _blocked("FINAL_REPORT_SOURCE_MISMATCH", ["source_review_reference_missing"])
    if any(not source.get(key) for key in required_snapshot_keys):
        return _blocked("FINAL_REPORT_SOURCE_MISMATCH", ["source_snapshot_reference_missing"])
    for key in required_snapshot_keys:
        bound = candidate_binding.get(key)
        if bound is not None and bound != source[key]:
            return _blocked("FINAL_REPORT_SOURCE_MISMATCH", [f"{key}_mismatch"])

    try:
        findings = _render_reviewed_items(review.get("findings", []), "finding")
        hypotheses = _render_reviewed_items(review.get("hypotheses", []), "hypothesis")
    except FinalReportValidationError as exc:
        return _blocked("FINAL_REPORT_BLOCKED_BY_REVIEW", [str(exc)])

    for item in review.get("doctor_added_findings", []):
        if not item.get("reviewed", False):
            return _blocked("FINAL_REPORT_BLOCKED_BY_REVIEW", ["doctor_added_finding_unreviewed"])
        findings.append({
            "id": item["id"], "text": item["text"],
            "decision": "doctor_added", "source": "doctor_authored",
        })

    recommendation = review.get("recommendation") or {}
    if recommendation.get("text") and recommendation.get("source") not in ALLOWED_RECOMMENDATION_SOURCES:
        raise FinalReportValidationError("AUTONOMOUS_RECOMMENDATION_FORBIDDEN")

    temporal = review.get("temporal") or {}
    if temporal.get("text") and not temporal.get("reviewed"):
        raise FinalReportValidationError("UNREVIEWED_TEMPORAL_STATE_FORBIDDEN")
    communication = review.get("communication_event") or {}
    if communication and not communication.get("host_supplied"):
        raise FinalReportValidationError("FABRICATED_COMMUNICATION_EVENT_FORBIDDEN")

    candidate = _blank_candidate()
    candidate["source_review_id"] = review["id"]
    candidate["source_review_version"] = review["version"]
    metadata = config.get("verified_metadata", {})
    for key in candidate["patient_study"]:
        candidate["patient_study"][key] = metadata.get(key)
    candidate["clinical_information"]["indication"] = metadata.get("indication")
    candidate["technique"]["text"] = metadata.get("technique")
    candidate["comparison"]["text"] = temporal.get("text")
    candidate["findings"]["structured_items"] = findings
    candidate["findings"]["text"] = review.get("doctor_findings_text")
    candidate["impression"]["structured_items"] = hypotheses
    candidate["impression"]["text"] = review.get("doctor_impression")
    candidate["recommendations"] = {
        "text": recommendation.get("text"), "source": recommendation.get("source")
    }
    candidate["limitations"] = deepcopy(review.get("limitations", []))
    candidate["unresolved_items"] = deepcopy(review.get("unresolved_items", []))
    candidate["provenance"] = {
        **{key: source[key] for key in required_snapshot_keys},
        "doctor_review_id": review["id"],
        "doctor_review_version": review["version"],
    }

    states = ["FINAL_REPORT_CANDIDATE_READY", "FINAL_REPORT_RENDERED_FROM_REVIEW"]
    external_finalization = config.get("external_finalization")
    if external_finalization:
        if external_finalization.get("source") != "authenticated_doctor":
            raise FinalReportValidationError("HERMES_AUTO_FINALIZATION_FORBIDDEN")
        if not external_finalization.get("finalized_by"):
            raise FinalReportValidationError("FINALIZED_BY_MISSING")
        if not external_finalization.get("finalized_at"):
            raise FinalReportValidationError("FINALIZED_AT_MISSING")
        if external_finalization.get("review_version") != review["version"]:
            return _blocked("FINAL_REPORT_VERSION_MISMATCH", ["finalization_review_version_mismatch"])
        candidate["report_status"] = "final"
        candidate["finalization"] = {
            "finalized": True,
            "finalized_by": external_finalization["finalized_by"],
            "finalized_at": external_finalization["finalized_at"],
        }
        states = ["FINAL_REPORT_FINALIZED_BY_DOCTOR"]

    history = deepcopy(config.get("report_history", []))
    if config.get("new_evidence_after_finalization"):
        states.append("FINAL_REPORT_AMENDMENT_REQUIRED")
    if config.get("replacement_report_id"):
        if not history:
            raise FinalReportValidationError("SUPERSEDED_REPORT_HISTORY_MISSING")
        states.append("FINAL_REPORT_SUPERSEDED")

    if fingerprint(source) != source_before:
        raise FinalReportValidationError("SOURCE_SNAPSHOT_MUTATED")
    return {
        "states": states,
        "blocking_reasons": [],
        "final_report_candidate": candidate,
        "source_fingerprint_before": source_before,
        "source_fingerprint_after": fingerprint(source),
        "report_history": history,
        "communication_event": deepcopy(communication) or None,
    }
