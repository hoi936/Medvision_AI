"""Fail-closed readiness assessment for Human-AI Reader Study v1."""

from __future__ import annotations

from enum import Enum

from .case_manifest import CaseIsolationError, validate_case_isolation
from .frozen_assistance import FrozenAssistanceError, validate_frozen_assistance
from .randomization import build_randomization_plan
from .reader_manifest import validate_reader_manifest
from .study_schema import ETHICS_RESOLVED_STATUSES, StudySchemaError, validate_study_protocol


class ReaderStudyState(str, Enum):
    SCAFFOLD_READY = "READER_STUDY_SCAFFOLD_READY"
    PROTOCOL_INCOMPLETE = "READER_STUDY_PROTOCOL_INCOMPLETE"
    DATASET_MISSING = "READER_STUDY_DATASET_MISSING"
    PROVIDER_BLOCKED = "READER_STUDY_PROVIDER_BLOCKED"
    ETHICS_STATUS_UNRESOLVED = "READER_STUDY_ETHICS_STATUS_UNRESOLVED"
    READERS_MISSING = "READER_STUDY_READERS_MISSING"
    READY = "READER_STUDY_READY"
    RUNNING = "READER_STUDY_RUNNING"
    COMPLETE = "READER_STUDY_COMPLETE"
    FAILED = "READER_STUDY_FAILED"


class ReaderStudyHarness:
    @staticmethod
    def scaffold_status():
        return {"state": ReaderStudyState.SCAFFOLD_READY.value, "actual_study_run": False}

    def assess(self, *, protocol, readers, training_cases, evaluation_cases, frozen_assistance):
        blockers = []
        if protocol is None:
            blockers.extend([
                "protocol not configured", "independent dataset not configured",
                "readers not configured", "ethics/privacy determination unresolved",
                "provider/frozen assistance not configured",
            ])
            return self._blocked(ReaderStudyState.PROTOCOL_INCOMPLETE, blockers)
        try:
            validate_study_protocol(protocol)
        except StudySchemaError as exc:
            return self._blocked(ReaderStudyState.PROTOCOL_INCOMPLETE, [str(exc)])
        if not evaluation_cases:
            return self._blocked(ReaderStudyState.DATASET_MISSING, ["independent dataset not configured"])
        if not training_cases:
            return self._blocked(
                ReaderStudyState.PROTOCOL_INCOMPLETE,
                ["training set is required and must be isolated from evaluation cases"],
            )
        try:
            validate_case_isolation(training_cases or [], evaluation_cases)
        except CaseIsolationError as exc:
            return self._blocked(ReaderStudyState.FAILED, ["case isolation failed"], violations=exc.violations)
        ethics = protocol["ethics"]
        ethics_resolved = (
            ethics.get("status") in ETHICS_RESOLVED_STATUSES
            and bool(ethics.get("determination_reference"))
            and ethics.get("privacy_status") == "RESOLVED"
            and ethics.get("data_use_status") == "RESOLVED"
            and ethics.get("reader_participation_status") == "RESOLVED"
        )
        if not ethics_resolved:
            return self._blocked(
                ReaderStudyState.ETHICS_STATUS_UNRESOLVED,
                ["institutional ethics/privacy determination unresolved"],
            )
        try:
            validated_readers = validate_reader_manifest(
                readers,
                planned_count=protocol["reader_plan"]["planned_count"],
            )
        except (StudySchemaError, ValueError) as exc:
            return self._blocked(ReaderStudyState.READERS_MISSING, [str(exc)])
        case_ids = [case["case_id"] for case in evaluation_cases]
        try:
            assistance = validate_frozen_assistance(
                frozen_assistance,
                case_ids=case_ids,
                study_version=protocol["version"],
                ui_version=protocol["ui_version"],
            )
        except FrozenAssistanceError as exc:
            return self._blocked(ReaderStudyState.PROVIDER_BLOCKED, [str(exc)])
        session_ids = [f"SESSION-{index}" for index in range(1, protocol["sessions"]["count"] + 1)]
        randomization = build_randomization_plan(
            validated_readers,
            case_ids,
            session_ids=session_ids,
            seed=protocol["randomization"]["seed"],
        )
        validated_readers = [
            {**reader, "assigned_sequence": randomization["sequences"][reader["reader_id"]]}
            for reader in validated_readers
        ]
        return {
            "state": ReaderStudyState.READY.value,
            "readiness_blockers": [],
            "actual_study_run": False,
            "protocol": protocol,
            "readers": validated_readers,
            "evaluation_cases": evaluation_cases,
            "frozen_assistance": assistance,
            "randomization": randomization,
        }

    @staticmethod
    def _blocked(state, blockers, **extra):
        return {
            "state": state.value,
            "readiness_blockers": list(blockers),
            "actual_study_run": False,
            **extra,
        }
