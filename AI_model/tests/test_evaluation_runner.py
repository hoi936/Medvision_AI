"""Clinical Dataset Evaluation state-machine tests."""

from pathlib import Path

from evaluation.evaluation_runner import EvaluationRunner, EvaluationState
from evaluation.system_snapshot import PINNED_HERMES_COMMIT, capture_system_snapshot
from evaluation_fixtures import evaluation_case, reference, write_dataset


class BlockedProvider(RuntimeError):
    classification = "INFRASTRUCTURE_CONFIGURATION"
    reason = "RUN_HERMES_REAL=1 but no usable provider/model is configured"


def snapshot(dataset_version, *, provider=None, model=None):
    return {
        "repo_commit": "repo", "hermes_version": "0.21.4",
        "hermes_commit": PINNED_HERMES_COMMIT, "python_version": "3.11.15",
        "provider": provider, "model": model, "config_hash": "config",
        "skill_tree_hash": "skills", "dataset_version": dataset_version,
        "metric_specification_version": "clinical-dataset-metrics-v1",
        "unknown_fields": [], "snapshot_hash": "snapshot",
    }


def test_missing_dataset_returns_required_not_run_reason_without_fallback():
    result = EvaluationRunner(snapshot_fn=snapshot).run(
        None, requested_tasks=["finding"], provider_required=False
    )
    assert result["state"] == EvaluationState.DATASET_MISSING.value
    assert result["reason"] == "independent evaluation dataset not configured"
    assert result["actual_dataset_run"] is False


def test_runner_exposes_the_exact_frozen_state_vocabulary():
    assert {state.value for state in EvaluationState} == {
        "EVALUATION_SCAFFOLD_READY", "EVALUATION_DATASET_MISSING",
        "EVALUATION_PROVIDER_BLOCKED", "EVALUATION_REFERENCE_INCOMPLETE",
        "EVALUATION_READY", "EVALUATION_RUNNING", "EVALUATION_COMPLETE",
        "EVALUATION_FAILED",
    }


def test_valid_provider_independent_dataset_stops_at_ready_without_evaluator(tmp_path):
    path = write_dataset(tmp_path, [evaluation_case()])
    result = EvaluationRunner(snapshot_fn=snapshot).run(
        path, requested_tasks=["finding"], provider_required=False
    )
    assert result["state"] == EvaluationState.READY.value
    assert result["actual_dataset_run"] is False
    assert result["provider_trial_policy"] is None
    assert result["system_snapshot"]["dataset_version"] == "test-v1"


def test_incomplete_reference_blocks_before_evaluation(tmp_path):
    path = write_dataset(tmp_path, [evaluation_case(references=[reference("finding", "POSITIVE")])], tasks=("finding", "disease_state"))
    result = EvaluationRunner(snapshot_fn=snapshot).run(
        path, requested_tasks=["finding", "disease_state"], provider_required=False
    )
    assert result["state"] == EvaluationState.REFERENCE_INCOMPLETE.value
    assert result["actual_dataset_run"] is False


def test_provider_block_reuses_injected_preflight_and_never_calls_evaluator(tmp_path):
    calls = []
    path = write_dataset(tmp_path, [evaluation_case()])

    def blocked():
        calls.append("preflight")
        raise BlockedProvider()

    result = EvaluationRunner(
        provider_preflight=blocked,
        snapshot_fn=snapshot,
        real_run_enabled_fn=lambda: True,
    ).run(
        path,
        requested_tasks=["finding"],
        provider_required=True,
        evaluator=lambda *_: calls.append("evaluator"),
    )
    assert result["state"] == EvaluationState.PROVIDER_BLOCKED.value
    assert result["infrastructure_class"] == "INFRASTRUCTURE_CONFIGURATION"
    assert calls == ["preflight"]


def test_actual_run_has_explicit_running_complete_history_and_fixed_provider_policy(tmp_path):
    path = write_dataset(tmp_path, [evaluation_case()])
    runner = EvaluationRunner(
        provider_preflight=lambda: {"provider": "safe", "model": "model"},
        snapshot_fn=snapshot,
        real_run_enabled_fn=lambda: True,
    )
    result = runner.run(
        path,
        requested_tasks=["finding"],
        provider_required=True,
        evaluator=lambda manifest, cases, system: {
            "dataset_version": manifest["dataset_version"],
            "case_results": [{"case_id": case["case_id"]} for case in cases],
            "metrics": {"finding": {"exact_state_agreement": {"numerator": 1, "denominator": 1, "estimate": 1.0}}},
            "confidence_intervals": {},
            "limitations": ["synthetic code-test fixture; not an evaluation result"],
        },
    )
    assert result["state"] == EvaluationState.COMPLETE.value
    assert result["state_history"][-2:] == [
        EvaluationState.RUNNING.value, EvaluationState.COMPLETE.value,
    ]
    assert result["provider_trial_policy"] == {
        "mode": "REAL_GATE", "trials_per_case": 1,
        "semantic_retries": 0, "cherry_pick": False,
    }
    assert result["results"]["dataset_version"] == "test-v1"
    assert len(result["results"]["case_results"]) == 1


def test_provider_mode_requires_explicit_real_run_gate_before_preflight(tmp_path):
    calls = []
    path = write_dataset(tmp_path, [evaluation_case()])
    result = EvaluationRunner(
        provider_preflight=lambda: calls.append("preflight"),
        snapshot_fn=snapshot,
        real_run_enabled_fn=lambda: False,
    ).run(path, requested_tasks=["finding"], provider_required=True)
    assert result["state"] == EvaluationState.PROVIDER_BLOCKED.value
    assert result["infrastructure_class"] == "INFRASTRUCTURE_CONFIGURATION"
    assert calls == []


def test_incomplete_evaluator_output_cannot_be_marked_complete(tmp_path):
    path = write_dataset(tmp_path, [evaluation_case()])
    result = EvaluationRunner(snapshot_fn=snapshot).run(
        path,
        requested_tasks=["finding"],
        provider_required=False,
        evaluator=lambda *_: {"metrics": {}},
    )
    assert result["state"] == EvaluationState.FAILED.value
    assert result["actual_dataset_run"] is True
    assert "missing fields" in result["reason"]


def test_real_system_snapshot_records_versions_hashes_and_unknown_fields():
    result = capture_system_snapshot("dataset-v1", provider=None, model=None)
    assert result["repo_commit"]
    assert "0.21.4" in result["hermes_version"]
    assert result["hermes_commit"] == PINNED_HERMES_COMMIT
    assert result["python_version"] == "3.11.15"
    assert result["config_hash"]
    assert result["skill_tree_hash"]
    assert result["dataset_version"] == "dataset-v1"
    assert result["snapshot_hash"]
