"""Fail-closed readiness state machine for silent and prospective evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .data_source_contract import DataSourceContractError, validate_data_source_contract
from .prospective_protocol import validate_prospective_protocol
from .protocol_schema import ClinicalProtocolError, validate_silent_protocol
from .silent_isolation import SilentIsolationBreach


class ClinicalEvaluationState(str, Enum):
    CLINICAL_EVAL_SCAFFOLD_READY = "CLINICAL_EVAL_SCAFFOLD_READY"
    SILENT_PROTOCOL_INCOMPLETE = "SILENT_PROTOCOL_INCOMPLETE"
    SILENT_DATA_SOURCE_MISSING = "SILENT_DATA_SOURCE_MISSING"
    SILENT_PROVIDER_BLOCKED = "SILENT_PROVIDER_BLOCKED"
    SILENT_ETHICS_STATUS_UNRESOLVED = "SILENT_ETHICS_STATUS_UNRESOLVED"
    SILENT_SECURITY_STATUS_UNRESOLVED = "SILENT_SECURITY_STATUS_UNRESOLVED"
    SILENT_READY = "SILENT_READY"
    SILENT_RUNNING = "SILENT_RUNNING"
    SILENT_COMPLETE = "SILENT_COMPLETE"
    SILENT_FAILED = "SILENT_FAILED"
    INTERVENTIONAL_PROTOCOL_INCOMPLETE = "INTERVENTIONAL_PROTOCOL_INCOMPLETE"
    INTERVENTIONAL_READINESS_REVIEW_REQUIRED = "INTERVENTIONAL_READINESS_REVIEW_REQUIRED"
    INTERVENTIONAL_READY = "INTERVENTIONAL_READY"
    INTERVENTIONAL_RUNNING = "INTERVENTIONAL_RUNNING"
    INTERVENTIONAL_COMPLETE = "INTERVENTIONAL_COMPLETE"
    INTERVENTIONAL_FAILED = "INTERVENTIONAL_FAILED"


RESOLVED_GOVERNANCE_STATUSES = {"APPROVED", "RESOLVED", "NOT_REQUIRED_BY_INSTITUTION"}


@dataclass(frozen=True)
class ReadinessResult:
    state: ClinicalEvaluationState
    blockers: tuple[str, ...] = ()
    actual_run_started: bool = False
    incident_category: str | None = None

    def as_dict(self):
        return {
            "state": self.state.value,
            "blockers": list(self.blockers),
            "actual_run_started": self.actual_run_started,
            "incident_category": self.incident_category,
        }


def _resolved(record):
    return (
        isinstance(record, dict)
        and record.get("status") in RESOLVED_GOVERNANCE_STATUSES
        and isinstance(record.get("reference"), str)
        and bool(record["reference"].strip())
    )


class ClinicalEvaluationHarness:
    def scaffold_status(self):
        return ReadinessResult(ClinicalEvaluationState.CLINICAL_EVAL_SCAFFOLD_READY)

    def assess_silent(self, protocol=None, data_source_contracts=None, provider_evidence=None):
        if protocol is None:
            return ReadinessResult(
                ClinicalEvaluationState.SILENT_PROTOCOL_INCOMPLETE,
                (
                    "protocol not configured",
                    "data source not configured",
                    "provider/frozen Hermes output strategy not configured",
                    "ethics/privacy determination unresolved",
                    "security determination unresolved",
                ),
            )
        try:
            validate_silent_protocol(protocol)
        except SilentIsolationBreach as exc:
            return ReadinessResult(
                ClinicalEvaluationState.SILENT_FAILED,
                (str(exc),),
                incident_category="SILENT_ISOLATION_BREACH",
            )
        except ClinicalProtocolError as exc:
            return ReadinessResult(ClinicalEvaluationState.SILENT_PROTOCOL_INCOMPLETE, (str(exc),))

        contracts = data_source_contracts or []
        if not contracts:
            return ReadinessResult(
                ClinicalEvaluationState.SILENT_DATA_SOURCE_MISSING,
                ("data-source contract missing",),
            )
        try:
            for contract in contracts:
                validate_data_source_contract(contract)
        except DataSourceContractError as exc:
            return ReadinessResult(ClinicalEvaluationState.SILENT_DATA_SOURCE_MISSING, (str(exc),))
        configured = {item["source_id"] for item in contracts}
        requested = set(protocol["data_sources"])
        absent = sorted(requested - configured)
        if absent:
            return ReadinessResult(
                ClinicalEvaluationState.SILENT_DATA_SOURCE_MISSING,
                ("missing contracts: " + ", ".join(absent),),
            )

        strategy = protocol["provider_requirements"]["strategy"]
        evidence = provider_evidence or {}
        if strategy == "LIVE_PINNED_PROVIDER":
            valid_provider = (
                evidence.get("preflight_status") == "PASS"
                and evidence.get("run_hermes_real") is True
                and evidence.get("snapshot_hash") == protocol["system_snapshot"]["snapshot_hash"]
            )
            if not valid_provider:
                return ReadinessResult(
                    ClinicalEvaluationState.SILENT_PROVIDER_BLOCKED,
                    ("pinned live provider preflight unavailable or mismatched",),
                )
        else:
            valid_frozen = (
                evidence.get("frozen_outputs_ready") is True
                and isinstance(evidence.get("frozen_outputs_hash"), str)
                and bool(evidence["frozen_outputs_hash"].strip())
                and evidence.get("snapshot_hash") == protocol["system_snapshot"]["snapshot_hash"]
            )
            if not valid_frozen:
                return ReadinessResult(
                    ClinicalEvaluationState.SILENT_PROVIDER_BLOCKED,
                    ("version-bound frozen Hermes outputs are unavailable",),
                )

        if not _resolved(protocol["ethics"]) or not _resolved(protocol["privacy"]):
            return ReadinessResult(
                ClinicalEvaluationState.SILENT_ETHICS_STATUS_UNRESOLVED,
                ("ethics/privacy status or institutional reference unresolved",),
            )
        if not _resolved(protocol["security"]):
            return ReadinessResult(
                ClinicalEvaluationState.SILENT_SECURITY_STATUS_UNRESOLVED,
                ("security status or institutional reference unresolved",),
            )
        return ReadinessResult(ClinicalEvaluationState.SILENT_READY)

    def authorize_silent_start(self, readiness, protocol, event):
        return _authorize_start(
            readiness, protocol, event,
            ready=ClinicalEvaluationState.SILENT_READY,
            running=ClinicalEvaluationState.SILENT_RUNNING,
            event_type="AUTHORIZED_SILENT_START",
            failure=ClinicalEvaluationState.SILENT_FAILED,
        )

    def assess_interventional(self, protocol=None, governance_approval=None):
        if protocol is None:
            return ReadinessResult(
                ClinicalEvaluationState.INTERVENTIONAL_PROTOCOL_INCOMPLETE,
                ("prospective interventional protocol not configured",),
            )
        try:
            validate_prospective_protocol(protocol)
        except ClinicalProtocolError as exc:
            return ReadinessResult(
                ClinicalEvaluationState.INTERVENTIONAL_PROTOCOL_INCOMPLETE,
                (str(exc),),
            )
        approval = governance_approval or {}
        valid = (
            approval.get("status") == "APPROVED"
            and isinstance(approval.get("reference"), str)
            and bool(approval["reference"].strip())
            and isinstance(approval.get("approved_by_roles"), list)
            and bool(approval["approved_by_roles"])
            and approval.get("protocol_version") == protocol["version"]
            and approval.get("snapshot_hash") == protocol["system_snapshot"]["snapshot_hash"]
        )
        if not valid:
            return ReadinessResult(
                ClinicalEvaluationState.INTERVENTIONAL_READINESS_REVIEW_REQUIRED,
                ("explicit protocol- and snapshot-bound governance approval required",),
            )
        return ReadinessResult(ClinicalEvaluationState.INTERVENTIONAL_READY)

    def authorize_interventional_start(self, readiness, protocol, event):
        return _authorize_start(
            readiness, protocol, event,
            ready=ClinicalEvaluationState.INTERVENTIONAL_READY,
            running=ClinicalEvaluationState.INTERVENTIONAL_RUNNING,
            event_type="AUTHORIZED_INTERVENTIONAL_START",
            failure=ClinicalEvaluationState.INTERVENTIONAL_FAILED,
        )


def _authorize_start(readiness, protocol, event, *, ready, running, event_type, failure):
    if readiness.state != ready:
        return ReadinessResult(failure, (f"start requires {ready.value}",))
    required = {
        "event_type", "actor_role", "authorization_reference", "authorized_at",
        "protocol_version", "snapshot_hash",
    }
    if not isinstance(event, dict) or not required <= set(event):
        return ReadinessResult(failure, ("explicit authorized start event is incomplete",))
    if event["event_type"] != event_type:
        return ReadinessResult(failure, ("authorized start event type mismatch",))
    if event["protocol_version"] != protocol["version"]:
        return ReadinessResult(failure, ("authorized protocol version mismatch",))
    if event["snapshot_hash"] != protocol["system_snapshot"]["snapshot_hash"]:
        return ReadinessResult(failure, ("authorized deployment snapshot mismatch",))
    for field in ("actor_role", "authorization_reference", "authorized_at"):
        if not isinstance(event[field], str) or not event[field].strip():
            return ReadinessResult(failure, (f"authorized start {field} missing",))
    return ReadinessResult(running, actual_run_started=True)
