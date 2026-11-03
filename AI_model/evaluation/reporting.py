"""JSON, CSV, and Markdown output for dataset evaluation results."""

from __future__ import annotations

import csv
import io
import json

from .evaluation_runner import EvaluationState


def build_report(*, run_result, metrics=None, confidence_intervals=None, limitations=()):
    actual = bool(run_result.get("actual_dataset_run"))
    manifest = run_result.get("manifest") or {}
    cases = run_result.get("cases") or []
    return {
        "clinical_dataset_evaluation": {
            "state": run_result["state"],
            "execution": "actual_dataset_run" if actual else "scaffold_only",
            "reason": run_result.get("reason"),
            "dataset": {
                "dataset_id": manifest.get("dataset_id"),
                "dataset_version": manifest.get("dataset_version"),
                "case_count": len(cases),
                "patient_count": len({case.get("patient_group_id") for case in cases}),
                "study_count": sum(len(case.get("studies", [])) for case in cases),
            },
            "system_snapshot": run_result.get("system_snapshot"),
            "provider_status": (
                "blocked" if run_result["state"] == EvaluationState.PROVIDER_BLOCKED.value
                else "not_required" if not run_result.get("provider_required")
                else "ready"
            ),
            "metrics": metrics or {},
            "confidence_intervals": confidence_intervals or {},
            "limitations": list(limitations),
        }
    }


def render_json(report):
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _metric_rows(value, path=""):
    if isinstance(value, dict) and {"numerator", "denominator", "estimate"} <= set(value):
        yield {
            "metric": path,
            "numerator": value["numerator"],
            "denominator": value["denominator"],
            "estimate": value["estimate"],
        }
        return
    if isinstance(value, dict):
        for key, child in sorted(value.items()):
            yield from _metric_rows(child, f"{path}.{key}" if path else key)


def render_metrics_csv(report):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["metric", "numerator", "denominator", "estimate"])
    writer.writeheader()
    metrics = report["clinical_dataset_evaluation"]["metrics"]
    writer.writerows(_metric_rows(metrics))
    return output.getvalue()


def render_markdown(report):
    root = report["clinical_dataset_evaluation"]
    dataset = root["dataset"]
    lines = [
        "# Clinical Dataset Evaluation v1",
        "",
        f"- State: `{root['state']}`",
        f"- Execution: `{root['execution']}`",
        f"- Provider status: `{root['provider_status']}`",
        f"- Dataset: `{dataset['dataset_id'] or 'not configured'}`",
        f"- Cases: {dataset['case_count']}",
        f"- Patients: {dataset['patient_count']}",
        f"- Studies: {dataset['study_count']}",
    ]
    if root["reason"]:
        lines.extend(["", f"Reason: {root['reason']}"])
    if root["limitations"]:
        lines.extend(["", "## Limitations", ""])
        lines.extend(f"- {item}" for item in root["limitations"])
    return "\n".join(lines) + "\n"
