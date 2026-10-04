"""Fail-closed state machine for Clinical Dataset Evaluation v1."""

from __future__ import annotations

from enum import Enum
import os

from .dataset_loader import IndependentDatasetRequiredError, load_dataset
from .dataset_schema import DatasetSchemaError
from .metrics import validate_metric_spec
from .reference_standard import ReferenceStandardError, validate_reference_set
from .split_integrity import SplitIntegrityError, validate_split_integrity
from .system_snapshot import capture_system_snapshot


class EvaluationState(str, Enum):
    SCAFFOLD_READY = "EVALUATION_SCAFFOLD_READY"
    DATASET_MISSING = "EVALUATION_DATASET_MISSING"
    PROVIDER_BLOCKED = "EVALUATION_PROVIDER_BLOCKED"
    REFERENCE_INCOMPLETE = "EVALUATION_REFERENCE_INCOMPLETE"
    READY = "EVALUATION_READY"
    RUNNING = "EVALUATION_RUNNING"
    COMPLETE = "EVALUATION_COMPLETE"
    FAILED = "EVALUATION_FAILED"


class EvaluationProviderPreflightError(RuntimeError):
    classification = "INFRASTRUCTURE_CONFIGURATION"

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class EvaluationRunner:
    def __init__(
        self,
        *,
        provider_preflight=None,
        snapshot_fn=capture_system_snapshot,
        real_run_enabled_fn=None,
    ):
        self.provider_preflight = provider_preflight
        self.snapshot_fn = snapshot_fn
        self.real_run_enabled_fn = real_run_enabled_fn or (
            lambda: os.environ.get("RUN_HERMES_REAL") == "1"
        )

    @staticmethod
    def scaffold_status():
        return {
            "state": EvaluationState.SCAFFOLD_READY.value,
            "actual_dataset_run": False,
        }

    def _run_provider_preflight(self):
        if not self.real_run_enabled_fn():
            raise EvaluationProviderPreflightError(
                "RUN_HERMES_REAL=1 is required before provider-backed dataset evaluation"
            )
        if self.provider_preflight is not None:
            return self.provider_preflight()
        from hermes_real_runtime import run_provider_preflight
        return run_provider_preflight()

    def prepare(self, manifest_path, *, requested_tasks, provider_required):
        history = [EvaluationState.SCAFFOLD_READY.value]
        try:
            manifest, cases = load_dataset(manifest_path)
        except IndependentDatasetRequiredError as exc:
            return {
                "state": EvaluationState.DATASET_MISSING.value,
                "reason": str(exc), "actual_dataset_run": False, "state_history": history,
            }
        except (DatasetSchemaError, OSError, ValueError) as exc:
            return {
                "state": EvaluationState.FAILED.value,
                "reason": f"dataset schema validation failed: {exc}",
                "actual_dataset_run": False,
                "state_history": history + [EvaluationState.FAILED.value],
            }
        try:
            validate_split_integrity(manifest, cases)
        except SplitIntegrityError as exc:
            return {
                "state": EvaluationState.FAILED.value,
                "reason": "dataset split integrity failed",
                "violations": exc.violations,
                "actual_dataset_run": False,
                "state_history": history + [EvaluationState.FAILED.value],
            }
        try:
            validate_reference_set(cases, requested_tasks)
        except ReferenceStandardError as exc:
            return {
                "state": EvaluationState.REFERENCE_INCOMPLETE.value,
                "reason": str(exc), "actual_dataset_run": False,
                "state_history": history + [EvaluationState.REFERENCE_INCOMPLETE.value],
            }
        metric_spec = manifest.get("metric_specification")
        if not isinstance(metric_spec, dict):
            return {
                "state": EvaluationState.FAILED.value,
                "reason": "metric specification is not pre-specified",
                "actual_dataset_run": False,
                "state_history": history + [EvaluationState.FAILED.value],
            }
        try:
            for task in requested_tasks:
                names = metric_spec.get(task)
                if not isinstance(names, list) or not names:
                    raise ValueError(f"metrics are not pre-specified for task: {task}")
                validate_metric_spec(task, names)
        except ValueError as exc:
            return {
                "state": EvaluationState.FAILED.value,
                "reason": str(exc), "actual_dataset_run": False,
                "state_history": history + [EvaluationState.FAILED.value],
            }
        provider_metadata = None
        if provider_required:
            try:
                provider_metadata = self._run_provider_preflight()
            except Exception as exc:
                classification = getattr(exc, "classification", None)
                reason = getattr(exc, "reason", str(exc))
                if classification not in {
                    "INFRASTRUCTURE_CONFIGURATION", "INFRASTRUCTURE_TRANSIENT",
                }:
                    return {
                        "state": EvaluationState.FAILED.value,
                        "reason": f"provider preflight failed unexpectedly: {reason}",
                        "actual_dataset_run": False,
                        "state_history": history + [EvaluationState.FAILED.value],
                    }
                return {
                    "state": EvaluationState.PROVIDER_BLOCKED.value,
                    "reason": reason,
                    "infrastructure_class": classification,
                    "actual_dataset_run": False,
                    "state_history": history + [EvaluationState.PROVIDER_BLOCKED.value],
                }
        snapshot = self.snapshot_fn(
            manifest["dataset_version"],
            provider=(provider_metadata or {}).get("provider"),
            model=(provider_metadata or {}).get("model"),
        )
        required_snapshot_fields = {
            "repo_commit", "hermes_version", "hermes_commit", "python_version",
            "config_hash", "skill_tree_hash", "dataset_version",
            "metric_specification_version", "snapshot_hash",
        }
        unavailable = sorted(
            field for field in required_snapshot_fields if not snapshot.get(field)
        )
        if unavailable:
            return {
                "state": EvaluationState.FAILED.value,
                "reason": "system snapshot incomplete: " + ", ".join(unavailable),
                "actual_dataset_run": False,
                "state_history": history + [EvaluationState.FAILED.value],
            }
        return {
            "state": EvaluationState.READY.value,
            "manifest": manifest,
            "cases": cases,
            "system_snapshot": snapshot,
            "provider_required": bool(provider_required),
            "provider_trial_policy": {
                "mode": "REAL_GATE", "trials_per_case": 1,
                "semantic_retries": 0, "cherry_pick": False,
            } if provider_required else None,
            "actual_dataset_run": False,
            "state_history": history + [EvaluationState.READY.value],
        }

    def run(self, manifest_path, *, requested_tasks, provider_required=False, evaluator=None):
        prepared = self.prepare(
            manifest_path,
            requested_tasks=requested_tasks,
            provider_required=provider_required,
        )
        if prepared["state"] != EvaluationState.READY.value or evaluator is None:
            return prepared
        prepared["state_history"].append(EvaluationState.RUNNING.value)
        try:
            outputs = evaluator(prepared["manifest"], prepared["cases"], prepared["system_snapshot"])
        except Exception as exc:
            prepared.update({
                "state": EvaluationState.FAILED.value,
                "reason": str(exc),
                "actual_dataset_run": True,
            })
            prepared["state_history"].append(EvaluationState.FAILED.value)
            return prepared
        output_error = self._validate_outputs(
            outputs,
            prepared["manifest"],
            prepared["cases"],
            requested_tasks,
        )
        if output_error:
            prepared.update({
                "state": EvaluationState.FAILED.value,
                "reason": output_error,
                "actual_dataset_run": True,
            })
            prepared["state_history"].append(EvaluationState.FAILED.value)
            return prepared
        prepared.update({
            "state": EvaluationState.COMPLETE.value,
            "results": outputs,
            "actual_dataset_run": True,
        })
        prepared["state_history"].append(EvaluationState.COMPLETE.value)
        return prepared

    @staticmethod
    def _validate_outputs(outputs, manifest, cases, requested_tasks):
        if not isinstance(outputs, dict):
            return "evaluation output must be a machine-readable object"
        required = {"dataset_version", "case_results", "metrics", "confidence_intervals", "limitations"}
        missing = sorted(required - set(outputs))
        if missing:
            return "evaluation output missing fields: " + ", ".join(missing)
        if outputs["dataset_version"] != manifest["dataset_version"]:
            return "evaluation output dataset version mismatch"
        if not isinstance(outputs["case_results"], list) or len(outputs["case_results"]) != len(cases):
            return "evaluation output must retain one result for every dataset case"
        if not isinstance(outputs["metrics"], dict) or any(
            task not in outputs["metrics"] for task in requested_tasks
        ):
            return "evaluation output does not report every pre-specified task"
        if not isinstance(outputs["confidence_intervals"], dict):
            return "evaluation confidence intervals must be an object"
        if not isinstance(outputs["limitations"], list):
            return "evaluation limitations must be a list"
        return None
