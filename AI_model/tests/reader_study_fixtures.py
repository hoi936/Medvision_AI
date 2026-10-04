"""Synthetic reader-study code fixtures; never actual study data."""

from __future__ import annotations

from copy import deepcopy

from evaluation_fixtures import evaluation_case
from reader_study.frozen_assistance import freeze_assistance


SYSTEM_SNAPSHOT = {
    "repo_commit": "synthetic-repo",
    "hermes_version": "0.21.4",
    "hermes_commit": "2552fb543bd12a326d23449f41a9c13c48eb4e9a",
    "skill_tree_hash": "synthetic-skills-hash",
    "snapshot_hash": "synthetic-system-snapshot",
}


def study_protocol(*, ethics_status="APPROVED", planned_count=2):
    return {
        "study_id": "SYNTHETIC-READER-STUDY",
        "version": "test-v1",
        "objective": "Test reader-study infrastructure only.",
        "design": "paired_mrmc",
        "conditions": ["UNAIDED", "HERMES_ASSISTED"],
        "assistance_mode": "DRAFT_REPORT_ASSIST",
        "primary_endpoint": "major_error_rate",
        "secondary_endpoints": ["reading_time", "incorrect_ai_acceptance"],
        "dataset_id": "SYNTHETIC-CODE-TEST-ONLY",
        "reference_standard_version": "test-reference-v1",
        "reader_plan": {
            "target_roles": ["radiologist"],
            "target_experience_range": "categorical bands",
            "planned_count": planned_count,
        },
        "sessions": {
            "count": 2,
            "washout": {
                "duration": "pre-specified synthetic interval",
                "rationale": "reduce memory effect in code fixture",
                "memory_mitigation": "counterbalanced order and separate sessions",
            },
            "counterbalanced": True,
            "interruption_policy": "retain raw time and flag interruptions",
            "outlier_policy": "pre-specified before actual study",
        },
        "randomization": {"method": "AB_BA_COUNTERBALANCED", "seed": 17},
        "training": {"required": True, "training_case_set_id": "SYNTHETIC-TRAINING"},
        "system_snapshot": deepcopy(SYSTEM_SNAPSHOT),
        "ui_version": "synthetic-ui-v1",
        "ui_snapshot_hash": "synthetic-ui-snapshot-hash",
        "data_storage": {
            "status": "APPROVED",
            "approval_reference": "SYNTHETIC-STORAGE-APPROVAL",
        },
        "ethics": {
            "status": ethics_status,
            "determination_reference": "INSTITUTIONAL-TEST-REFERENCE" if ethics_status != "UNRESOLVED" else None,
            "privacy_status": "RESOLVED" if ethics_status != "UNRESOLVED" else "UNRESOLVED",
            "data_use_status": "RESOLVED" if ethics_status != "UNRESOLVED" else "UNRESOLVED",
            "reader_participation_status": "RESOLVED" if ethics_status != "UNRESOLVED" else "UNRESOLVED",
        },
    }


def reader(reader_id="R1"):
    return {
        "reader_id": reader_id,
        "role": "radiologist",
        "specialty": "thoracic imaging",
        "experience_band": "5-10 years",
        "training_level": "attending",
        "prior_ai_experience": "some",
        "site": "synthetic-site",
        "assigned_sequence": "PENDING",
    }


def study_case(case_id="DS001", patient="P1", study="S1"):
    case = evaluation_case(case_id, patient, study, "evaluation")
    case["metadata"]["study_role"] = "evaluation"
    case["metadata"]["reader_visible_fields"] = ["imaging", "clinical", "labs"]
    case["metadata"]["case_stratum"] = "synthetic-stratum"
    case["metadata"]["randomization_id"] = f"RAND-{case_id}"
    return case


def training_case(case_id="TRAIN001", patient="TP1", study="TS1"):
    case = evaluation_case(case_id, patient, study, "training")
    case["metadata"]["study_role"] = "training"
    return case


def assistance(case_id="DS001", *, output="Synthetic validated Hermes draft."):
    return freeze_assistance(
        case_id=case_id,
        output=output,
        study_version="test-v1",
        system_snapshot=SYSTEM_SNAPSHOT,
        provider="synthetic-provider",
        model="synthetic-model",
        generated_at="2026-10-03T10:00:00+07:00",
        validation_state="VALIDATED",
        ui_version="synthetic-ui-v1",
    )


def reader_event(*, condition="HERMES_ASSISTED", completed=True, snapshot_id=None):
    if snapshot_id is None and condition == "HERMES_ASSISTED":
        snapshot_id = assistance()["assistance_snapshot_id"]
    return {
        "study_id": "SYNTHETIC-READER-STUDY",
        "session_id": "SESSION-1",
        "reader_id": "R1",
        "case_id": "DS001",
        "condition": condition,
        "case_order": 1,
        "started_at": "2026-10-03T10:00:00+07:00",
        "completed_at": "2026-10-03T10:02:00+07:00",
        "finding_decisions": [{"finding": "Pneumothorax", "decision": "POSITIVE"}],
        "hypothesis_decisions": [],
        "report_text": "Synthetic code-test report.",
        "high_priority_acknowledgements": ["HP1"],
        "confidence": None,
        "doctor_review_actions": [{"action": "ACCEPT"}],
        "hermes_snapshot_id": snapshot_id if condition == "HERMES_ASSISTED" else None,
        "ui_version": "synthetic-ui-v1",
        "ui_interactions": {
            "warning_seen": True,
            "warning_acknowledged": True,
            "conflict_viewed": True,
            "provenance_panel_viewed": True,
            "accept_count": 1,
            "modify_count": 0,
            "reject_count": 0,
        },
        "technical_status": "OK",
        "completed": completed,
        "reference": "POSITIVE",
        "reader_result": "POSITIVE",
        "reference_agreement": True,
        "major_error": False,
        "unsafe_false_upgrade": False,
        "critical_miss": False,
        "error_class": None,
        "ai_suggestions": [
            {"suggestion_id": "AI1", "ai_correct": True, "action": "ACCEPTED"},
        ] if condition == "HERMES_ASSISTED" else [],
        "high_priority_present": True,
        "high_priority_miss": False,
        "uncertainty_over_upgrade": False,
        "doctor_review_boundary_violation": False,
        "provenance_confusion": False,
        "unsupported_action_retained": False,
        "conflict_suppression": False,
    }
