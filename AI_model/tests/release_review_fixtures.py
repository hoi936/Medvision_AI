"""Synthetic/project-state fixtures for Release Review v1 unit tests."""

from __future__ import annotations

from copy import deepcopy

from release_review.risk_register import seed_core_risk_templates


SNAPSHOT = {
    "repository_commit": "5f8e5843284f4811e9d359d41ff480261c10e2b2",
    "hermes_version": "0.21.4",
    "hermes_commit": "2552fb543bd12a326d23449f41a9c13c48eb4e9a",
    "python_version": "3.11.15",
    "provider": "UNCONFIGURED",
    "model": "UNCONFIGURED",
    "provider_model_version": None,
    "skill_tree_hash": "frozen-17-skill-synthetic-fixture",
    "config_hash": "frozen-config-synthetic-fixture",
    "ui_version": None,
    "evaluation_artifact_versions": {
        "regression": "997-passed-365-skipped",
        "clinical_evaluation": "43-passed",
        "cross_layer": "190-passed",
        "runtime_provider_units": "15-passed",
    },
    "snapshot_hash": "synthetic-current-baseline-snapshot",
}

INTENDED_USE = {
    "intended_users": ["MedVision internal research team"],
    "setting": "internal, non-clinical research environment",
    "inputs": ["approved synthetic or governed evaluation inputs"],
    "outputs": ["advisory research-only candidate output"],
    "clinical_role": "research evaluation only; no clinical action",
    "doctor_control_statement": "A doctor remains the decision-maker and finalizer in any future governed clinical workflow.",
    "prohibited_uses": ["autonomous diagnosis, treatment, procedure, alert, or finalization"],
    "known_limitations": ["no real-provider or real-world clinical validation has run"],
    "workflow_position": "outside live clinical workflow",
    "reviewer_role": "authorized project reviewer",
    "finalizer_role": "authenticated doctor in a future separately approved workflow",
    "escalation_owner": "project governance assignment required",
}


def artifact(evidence_id, category, status, maturity, dependency_family, limitation):
    return {
        "evidence_id": evidence_id,
        "category": category,
        "artifact_type": "test_or_harness_result",
        "path_or_reference": f"synthetic-reference:{evidence_id}",
        "version": "baseline-v1",
        "system_snapshot": SNAPSHOT["snapshot_hash"],
        "status": status,
        "maturity": maturity,
        "summary": "Project-state metadata fixture; artifact existence alone does not imply PASS.",
        "limitations": [limitation],
        "owner": "project test fixture",
        "dependency_family": dependency_family,
    }


BASELINE_EVIDENCE = [
    artifact("EV-REGRESSION", "PROVIDER_INDEPENDENT_REGRESSION", "PASS", "LEVEL_1_SYNTHETIC_OR_UNIT", "schema_unit", "Regression breadth is not clinical performance."),
    artifact("EV-E2E", "E2E_DETERMINISTIC", "PASS", "LEVEL_1_SYNTHETIC_OR_UNIT", "e2e", "Provider-independent deterministic fixtures only."),
    artifact("EV-RUNTIME", "RUNTIME_TOOL_WRITE_GATES", "PASS", "LEVEL_1_SYNTHETIC_OR_UNIT", "runtime", "Confirms pinned local runtime gates only."),
    artifact("EV-PROVIDER", "PROVIDER_BACKED_VALIDATION", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "provider_backed", "Provider/model unset; real behavior not run."),
    artifact("EV-DATASET-SCAFFOLD", "DATASET_EVALUATION_SCAFFOLD", "PASS", "LEVEL_1_SYNTHETIC_OR_UNIT", "dataset", "Evaluation harness implemented; actual dataset evaluation not run."),
    artifact("EV-DATASET-ACTUAL", "INDEPENDENT_DATASET_EVALUATION", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "dataset_model", "Independent dataset/reference standard absent."),
    artifact("EV-READER-SCAFFOLD", "READER_STUDY_SCAFFOLD", "PASS", "LEVEL_1_SYNTHETIC_OR_UNIT", "reader", "Reader-study harness implemented; study not run."),
    artifact("EV-READER-ACTUAL", "HUMAN_AI_READER_STUDY", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "reader_assistance", "Actual reader study not run."),
    artifact("EV-SILENT-SCAFFOLD", "SILENT_EVALUATION_SCAFFOLD", "PASS", "LEVEL_1_SYNTHETIC_OR_UNIT", "silent", "Silent evaluation harness implemented; study not run."),
    artifact("EV-SILENT-PROTOCOL", "SILENT_EVALUATION_PROTOCOL", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "silent", "Actual protocol and approved data source absent."),
    artifact("EV-SILENT-ACTUAL", "SILENT_EVALUATION_ACTUAL", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "silent", "Silent prospective evaluation not run."),
    artifact("EV-INTERVENTIONAL-PROTOCOL", "INTERVENTIONAL_PROTOCOL", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "interventional", "Actual interventional protocol absent."),
    artifact("EV-INTERVENTIONAL-ACTUAL", "INTERVENTIONAL_EVALUATION_ACTUAL", "NOT_AVAILABLE", "LEVEL_0_NOT_AVAILABLE", "interventional", "Prospective interventional evaluation not run."),
]

SAFETY_CLAIMS = [{
    "claim_id": "CLAIM-NO-AUTO-FINALIZATION",
    "statement": "The frozen deterministic path does not auto-finalize a clinical report.",
    "evidence_ids": ["EV-REGRESSION", "EV-E2E"],
    "assumptions": ["frozen project snapshot"],
    "limitations": ["real provider behavior and clinical workflow have not been validated"],
    "residual_risks": ["provider and integration behavior remain untested"],
    "owner": "project governance assignment required",
    "required_maturity": "LEVEL_1_SYNTHETIC_OR_UNIT",
}]


def current_baseline_review(target_stage="INTERNAL_RESEARCH"):
    return {
        "review_id": "REVIEW-SYNTHETIC-CURRENT-BASELINE",
        "target_stage": target_stage,
        "system_snapshot": deepcopy(SNAPSHOT),
        "intended_use": deepcopy(INTENDED_USE),
        "evidence_inventory": deepcopy(BASELINE_EVIDENCE),
        "risk_register": seed_core_risk_templates(),
        "safety_claims": deepcopy(SAFETY_CLAIMS),
        "security": {"status": "NOT_ASSESSED", "reference": "", "limitations": ["host determination absent"]},
        "privacy": {"status": "NOT_ASSESSED", "reference": "", "limitations": ["host determination absent"]},
        "provider": {
            "status": "NOT_ASSESSED", "reference": "", "limitations": ["provider/model unset"],
            "configured": False, "provider": "UNCONFIGURED", "model": "UNCONFIGURED",
            "outage_behavior": "fail closed", "drift_strategy": "revalidation required",
            "deprecation_plan": "not configured", "fallback_policy": "NO_SILENT_FALLBACK",
        },
        "monitoring_plan": None,
        "rollback_plan": None,
        "incident_response": None,
        "version_freeze": False,
        "governance_approval": {
            "status": "PENDING", "approved_by": "", "role": "", "approved_at": "", "scope": "",
        },
        "limitations": [
            "provider-backed real validation not run",
            "independent dataset evaluation not run",
            "reader, silent, and interventional studies not run",
            "test counts do not establish clinical performance or patient benefit",
        ],
    }


def resolved_provider(review):
    review["system_snapshot"]["provider"] = "sanitized-provider"
    review["system_snapshot"]["model"] = "sanitized-model"
    review["system_snapshot"]["provider_model_version"] = "frozen-version"
    review["provider"].update({
        "status": "RESOLVED", "reference": "SYNTHETIC-PROVIDER-REVIEW",
        "configured": True, "provider": "sanitized-provider", "model": "sanitized-model",
        "deprecation_plan": "synthetic pre-specified plan",
    })
    return review


def live_plans(review):
    review["monitoring_plan"] = {
        "metrics": ["semantic invariant failures"], "metric_owners": ["synthetic monitor owner"],
        "cadence": "pre-specified", "escalation": "pause and governance review",
        "pause_criteria": ["critical semantic failure"], "version_stratification": "required",
        "auto_adaptation": False,
    }
    review["rollback_plan"] = {
        "triggers": ["critical incident"], "owner": "synthetic rollback owner",
        "last_known_good_version": "synthetic-version", "data_compatibility": "pre-reviewed",
        "communication_path": "synthetic governance channel",
    }
    review["incident_response"] = {
        "category_owners": {"SEMANTIC_SAFETY_INCIDENT": "synthetic owner"},
        "severity_rules": ["pre-specified"], "acknowledgement": "required",
        "containment": "pause affected path", "root_cause_review": "required",
        "corrective_action": "governed change control", "evidence_preservation": "immutable record",
    }
    review["version_freeze"] = True
    return review


def external_approval(review):
    review["governance_approval"] = {
        "status": "APPROVED", "approved_by": "synthetic external governance fixture",
        "role": "study governance", "approved_at": "2026-01-01T00:00:00Z",
        "scope": review["target_stage"],
    }
    return review


def mark_category_pass(review, category, maturity="LEVEL_1_SYNTHETIC_OR_UNIT"):
    for item in review["evidence_inventory"]:
        if item["category"] == category:
            item["status"] = "PASS"
            item["maturity"] = maturity
    return review
