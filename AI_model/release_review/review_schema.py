"""Top-level release review request schema."""

from __future__ import annotations

from .evidence_inventory import validate_evidence_artifact
from .intended_use import validate_intended_use
from .privacy_readiness import validate_privacy_readiness
from .provider_readiness import validate_provider_readiness
from .risk_register import validate_risk
from .security_readiness import validate_security_readiness
from .system_snapshot import validate_system_snapshot


TARGET_STAGES = {
    "INTERNAL_RESEARCH", "OFFLINE_DATASET_EVALUATION", "READER_STUDY",
    "SILENT_EVALUATION", "INTERVENTIONAL_STUDY", "PRODUCTION_CLINICAL_USE",
}
GOVERNANCE_STATUSES = {"PENDING", "APPROVED", "REJECTED"}


class ReleaseReviewSchemaError(ValueError):
    pass


def validate_governance_approval(approval):
    required = {"status", "approved_by", "role", "approved_at", "scope"}
    if not isinstance(approval, dict) or not required <= set(approval):
        raise ReleaseReviewSchemaError("governance approval object is incomplete")
    if approval["status"] not in GOVERNANCE_STATUSES:
        raise ReleaseReviewSchemaError("invalid governance approval status")
    if approval["status"] == "APPROVED":
        for field in required - {"status"}:
            if not isinstance(approval[field], str) or not approval[field].strip():
                raise ReleaseReviewSchemaError("APPROVED governance requires external identity, time, role, and scope")
    return approval


def validate_review(review):
    required = {
        "review_id", "target_stage", "system_snapshot", "intended_use",
        "evidence_inventory", "risk_register", "safety_claims", "security",
        "privacy", "provider", "monitoring_plan", "rollback_plan",
        "incident_response", "version_freeze", "governance_approval", "limitations",
    }
    if not isinstance(review, dict):
        raise ReleaseReviewSchemaError("release review must be an object")
    missing = sorted(required - set(review))
    if missing:
        raise ReleaseReviewSchemaError("release review missing fields: " + ", ".join(missing))
    if review["target_stage"] not in TARGET_STAGES:
        raise ReleaseReviewSchemaError("unsupported target stage")
    if not isinstance(review["review_id"], str) or not review["review_id"].strip():
        raise ReleaseReviewSchemaError("review_id must be explicit")
    validate_system_snapshot(review["system_snapshot"])
    validate_intended_use(review["intended_use"])
    if not isinstance(review["evidence_inventory"], list):
        raise ReleaseReviewSchemaError("evidence inventory must be a list")
    for artifact in review["evidence_inventory"]:
        validate_evidence_artifact(artifact)
    if not isinstance(review["risk_register"], list):
        raise ReleaseReviewSchemaError("risk register must be a list")
    for risk in review["risk_register"]:
        validate_risk(risk)
    if not isinstance(review["safety_claims"], list):
        raise ReleaseReviewSchemaError("safety claims must be a list")
    validate_security_readiness(review["security"])
    validate_privacy_readiness(review["privacy"])
    validate_provider_readiness(review["provider"])
    validate_governance_approval(review["governance_approval"])
    if not isinstance(review["version_freeze"], bool):
        raise ReleaseReviewSchemaError("version_freeze must be boolean")
    if not isinstance(review["limitations"], list):
        raise ReleaseReviewSchemaError("limitations must be a list")
    return review
