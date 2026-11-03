"""Release review reports with no composite score or certification claim."""

from __future__ import annotations

import csv
import io
import json


DISCLAIMER = (
    "This governance scaffold does not claim regulatory compliance, clinical validation, "
    "clinical safety, patient benefit, or approval for clinical deployment."
)


def build_report(review, decision):
    return {
        "harness_status": "RELEASE-READINESS & SAFETY REVIEW HARNESS: IMPLEMENTED",
        "target_stage": review["target_stage"],
        "system_snapshot": review["system_snapshot"],
        "evidence_inventory": review["evidence_inventory"],
        "blockers": list(decision.blockers),
        "conditions": list(decision.conditions),
        "incomplete_evidence": list(decision.incomplete_evidence),
        "residual_risks": list(decision.residual_risks),
        "monitoring_plan": review["monitoring_plan"],
        "rollback_plan": review["rollback_plan"],
        "governance_status": decision.governance_status,
        "decision": decision.state.value,
        "limitations": list(review["limitations"]),
        "disclaimer": DISCLAIMER,
    }


def render_json(report):
    return json.dumps(report, sort_keys=True, indent=2)


def render_evidence_csv(report):
    stream = io.StringIO()
    fields = ("evidence_id", "category", "status", "maturity", "version", "path_or_reference", "limitations")
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for item in report["evidence_inventory"]:
        row = {field: item.get(field) for field in fields}
        row["limitations"] = " | ".join(item.get("limitations", []))
        writer.writerow(row)
    return stream.getvalue()


def render_markdown(report):
    blockers = report["blockers"] or ["none"]
    limitations = report["limitations"] or ["none"]
    return "\n".join([
        f"# {report['harness_status']}",
        "",
        f"Target stage: {report['target_stage']}",
        f"Decision: {report['decision']}",
        f"Governance status: {report['governance_status']}",
        "",
        "## Blockers",
        "",
        *[f"- {item}" for item in blockers],
        "",
        "## Residual risks",
        "",
        *[f"- {item}" for item in (report["residual_risks"] or ["none"])],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in limitations],
        "",
        DISCLAIMER,
        "",
    ])
