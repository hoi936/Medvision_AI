"""Machine-readable and human-readable summaries for evaluation readiness."""

from __future__ import annotations

import csv
import io
import json


NO_BENEFIT_CLAIM = "No clinical benefit, outcome improvement, or deployment readiness is claimed."


def build_evaluation_report(*, silent_readiness, interventional_readiness, synthetic_fixture_results):
    return {
        "harness_status": "SILENT / PROSPECTIVE CLINICAL EVALUATION HARNESS: IMPLEMENTED",
        "silent_clinical_evaluation": "NOT RUN",
        "prospective_interventional_evaluation": "NOT RUN",
        "silent_readiness": silent_readiness.as_dict(),
        "interventional_readiness": interventional_readiness.as_dict(),
        "blockers": {
            "silent": list(silent_readiness.blockers),
            "interventional": list(interventional_readiness.blockers),
        },
        "synthetic_fixture_results": dict(synthetic_fixture_results),
        "synthetic_results_are_clinical_results": False,
        "clinical_benefit_claim": None,
        "disclaimer": NO_BENEFIT_CLAIM,
    }


def render_json(report):
    return json.dumps(report, sort_keys=True, indent=2)


def render_csv(report):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=("section", "status", "blockers"))
    writer.writeheader()
    writer.writerow({
        "section": "silent_clinical_evaluation",
        "status": report["silent_clinical_evaluation"],
        "blockers": " | ".join(report["blockers"]["silent"]),
    })
    writer.writerow({
        "section": "prospective_interventional_evaluation",
        "status": report["prospective_interventional_evaluation"],
        "blockers": " | ".join(report["blockers"]["interventional"]),
    })
    writer.writerow({
        "section": "synthetic_fixture_results",
        "status": json.dumps(report["synthetic_fixture_results"], sort_keys=True),
        "blockers": "synthetic only; not clinical results",
    })
    return stream.getvalue()


def render_markdown(report):
    silent_blockers = report["blockers"]["silent"] or ["none"]
    interventional_blockers = report["blockers"]["interventional"] or ["none"]
    return "\n".join([
        f"# {report['harness_status']}",
        "",
        f"- SILENT CLINICAL EVALUATION: {report['silent_clinical_evaluation']}",
        f"- PROSPECTIVE INTERVENTIONAL EVALUATION: {report['prospective_interventional_evaluation']}",
        "",
        "## Blockers",
        "",
        "Silent: " + "; ".join(silent_blockers),
        "",
        "Interventional: " + "; ".join(interventional_blockers),
        "",
        "## Synthetic fixture results",
        "",
        json.dumps(report["synthetic_fixture_results"], sort_keys=True),
        "",
        "Synthetic fixture results are not clinical results.",
        "",
        NO_BENEFIT_CLAIM,
        "",
    ])
