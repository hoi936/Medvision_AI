"""Stage-specific, fail-closed release-readiness decision engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .evidence_inventory import EvidenceInventory
from .incident_response import validate_incident_response
from .monitoring_plan import validate_monitoring_plan
from .review_schema import ReleaseReviewSchemaError, validate_review
from .risk_register import RiskRegister
from .rollback_plan import validate_rollback_plan
from .safety_case import evaluate_claim


class TargetStage(str, Enum):
    INTERNAL_RESEARCH = "INTERNAL_RESEARCH"
    OFFLINE_DATASET_EVALUATION = "OFFLINE_DATASET_EVALUATION"
    READER_STUDY = "READER_STUDY"
    SILENT_EVALUATION = "SILENT_EVALUATION"
    INTERVENTIONAL_STUDY = "INTERVENTIONAL_STUDY"
    PRODUCTION_CLINICAL_USE = "PRODUCTION_CLINICAL_USE"


class ReleaseReviewState(str, Enum):
    RELEASE_REVIEW_SCAFFOLD_READY = "RELEASE_REVIEW_SCAFFOLD_READY"
    RELEASE_REVIEW_INCOMPLETE = "RELEASE_REVIEW_INCOMPLETE"
    RELEASE_BLOCKED = "RELEASE_BLOCKED"
    CONDITIONAL_REVIEW_REQUIRED = "CONDITIONAL_REVIEW_REQUIRED"
    READY_FOR_NEXT_GOVERNED_STAGE = "READY_FOR_NEXT_GOVERNED_STAGE"
    RELEASE_REVIEW_FAILED = "RELEASE_REVIEW_FAILED"


REQUIRED_EVIDENCE = {
    TargetStage.INTERNAL_RESEARCH: {
        "PROVIDER_INDEPENDENT_REGRESSION", "E2E_DETERMINISTIC", "RUNTIME_TOOL_WRITE_GATES",
    },
    TargetStage.OFFLINE_DATASET_EVALUATION: {
        "PROVIDER_INDEPENDENT_REGRESSION", "E2E_DETERMINISTIC",
        "RUNTIME_TOOL_WRITE_GATES", "DATASET_EVALUATION_SCAFFOLD",
    },
    TargetStage.READER_STUDY: {
        "PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION", "READER_STUDY_SCAFFOLD",
    },
    TargetStage.SILENT_EVALUATION: {
        "PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION",
        "SILENT_EVALUATION_PROTOCOL", "RUNTIME_TOOL_WRITE_GATES",
    },
    TargetStage.INTERVENTIONAL_STUDY: {
        "PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION",
        "HUMAN_AI_READER_STUDY", "SILENT_EVALUATION_ACTUAL",
        "INTERVENTIONAL_PROTOCOL", "RUNTIME_TOOL_WRITE_GATES",
    },
    TargetStage.PRODUCTION_CLINICAL_USE: {
        "PROVIDER_BACKED_VALIDATION", "INDEPENDENT_DATASET_EVALUATION",
        "HUMAN_AI_READER_STUDY", "SILENT_EVALUATION_ACTUAL",
        "INTERVENTIONAL_EVALUATION_ACTUAL", "RUNTIME_TOOL_WRITE_GATES",
    },
}
LIVE_STAGES = {
    TargetStage.SILENT_EVALUATION,
    TargetStage.INTERVENTIONAL_STUDY,
    TargetStage.PRODUCTION_CLINICAL_USE,
}
HUMAN_OR_CLINICAL_STAGES = {
    TargetStage.READER_STUDY,
    TargetStage.SILENT_EVALUATION,
    TargetStage.INTERVENTIONAL_STUDY,
    TargetStage.PRODUCTION_CLINICAL_USE,
}


@dataclass(frozen=True)
class ReleaseDecision:
    state: ReleaseReviewState
    target_stage: str | None
    blockers: tuple[str, ...] = ()
    conditions: tuple[str, ...] = ()
    incomplete_evidence: tuple[str, ...] = ()
    residual_risks: tuple[str, ...] = ()
    governance_status: str = "PENDING"

    def as_dict(self):
        return {
            "state": self.state.value,
            "target_stage": self.target_stage,
            "blockers": list(self.blockers),
            "conditions": list(self.conditions),
            "incomplete_evidence": list(self.incomplete_evidence),
            "residual_risks": list(self.residual_risks),
            "governance_status": self.governance_status,
        }


class ReleaseReviewHarness:
    def scaffold_status(self):
        return ReleaseDecision(
            ReleaseReviewState.RELEASE_REVIEW_SCAFFOLD_READY,
            target_stage=None,
        )

    def assess(self, review):
        try:
            validate_review(review)
        except (ReleaseReviewSchemaError, ValueError) as exc:
            return ReleaseDecision(
                ReleaseReviewState.RELEASE_REVIEW_INCOMPLETE,
                target_stage=review.get("target_stage") if isinstance(review, dict) else None,
                blockers=(str(exc),),
            )

        stage = TargetStage(review["target_stage"])
        try:
            inventory = EvidenceInventory(review["evidence_inventory"])
            risk_register = RiskRegister(review["risk_register"])
            evidence_by_id = {item["evidence_id"]: item for item in review["evidence_inventory"]}
            claims = [evaluate_claim(claim, evidence_by_id) for claim in review["safety_claims"]]
        except ValueError as exc:
            return ReleaseDecision(
                ReleaseReviewState.RELEASE_REVIEW_FAILED,
                target_stage=stage.value,
                blockers=(f"release review internal consistency failure: {exc}",),
                governance_status=review["governance_approval"]["status"],
            )
        passed = inventory.passed_categories()
        missing_categories = sorted(REQUIRED_EVIDENCE[stage] - passed)
        incomplete = tuple(f"required evidence not PASS: {item}" for item in missing_categories)
        blockers = list(incomplete)
        conditions = []

        failed = [
            item["evidence_id"] for item in review["evidence_inventory"]
            if item["status"] in {"FAIL", "BLOCKED", "INVALIDATED"}
            and item["category"] in REQUIRED_EVIDENCE[stage]
        ]
        blockers.extend(f"required evidence failed/blocked: {item}" for item in failed)

        blocking_risks = risk_register.blocking()
        blockers.extend(f"unresolved {risk['residual_risk']} risk: {risk['risk_id']}" for risk in blocking_risks)
        residual_risks = tuple(
            f"{risk['risk_id']}:{risk['residual_risk']}:{risk['state']}"
            for risk in risk_register.risks()
            if risk["state"] != "CLOSED"
        )

        incomplete_claims = [claim["claim_id"] for claim in claims if claim["status"] != "SUPPORTED_WITH_LIMITATIONS"]
        if incomplete_claims:
            message = "incomplete safety claims: " + ", ".join(incomplete_claims)
            if stage in HUMAN_OR_CLINICAL_STAGES:
                blockers.append(message)
            else:
                conditions.append(message)

        if stage != TargetStage.INTERNAL_RESEARCH:
            provider = review["provider"]
            if provider["status"] != "RESOLVED" or provider["configured"] is not True:
                blockers.append("provider/model readiness unresolved or provider unavailable")
            elif (
                provider["provider"] != review["system_snapshot"]["provider"]
                or provider["model"] != review["system_snapshot"]["model"]
            ):
                blockers.append("provider/model readiness does not match frozen system snapshot")

        if stage in HUMAN_OR_CLINICAL_STAGES:
            for domain in ("privacy", "security"):
                status = review[domain]["status"]
                if status != "RESOLVED":
                    blockers.append(f"{domain} readiness unresolved: {status}")

        if stage in LIVE_STAGES:
            for label, validator, value in (
                ("monitoring plan missing or incomplete", validate_monitoring_plan, review["monitoring_plan"]),
                ("rollback plan missing or incomplete", validate_rollback_plan, review["rollback_plan"]),
                ("incident response plan missing or incomplete", validate_incident_response, review["incident_response"]),
            ):
                try:
                    validator(value)
                except ValueError:
                    blockers.append(label)
            if review["version_freeze"] is not True:
                blockers.append("release candidate version is not frozen")

        governance = review["governance_approval"]
        if governance["status"] == "REJECTED":
            blockers.append("external governance approval rejected")
        elif governance["status"] == "APPROVED" and governance["scope"] != stage.value:
            blockers.append("external governance approval scope does not match target stage")
        elif governance["status"] != "APPROVED":
            conditions.append("external governance approval required for stage transition")

        blockers = tuple(dict.fromkeys(blockers))
        conditions = tuple(dict.fromkeys(conditions))
        if blockers:
            state = ReleaseReviewState.RELEASE_BLOCKED
        elif conditions:
            state = ReleaseReviewState.CONDITIONAL_REVIEW_REQUIRED
        else:
            state = ReleaseReviewState.READY_FOR_NEXT_GOVERNED_STAGE
        return ReleaseDecision(
            state,
            target_stage=stage.value,
            blockers=blockers,
            conditions=conditions,
            incomplete_evidence=incomplete,
            residual_risks=residual_risks,
            governance_status=governance["status"],
        )
