"""Reader-study readiness and result reporting in JSON, CSV, and Markdown."""

from __future__ import annotations

import csv
import io
import json


def build_report(*, assessment, endpoints=None, safety=None, human_ai=None, issues=(), limitations=()):
    actual = bool(assessment.get("actual_study_run"))
    return {
        "human_ai_reader_study": {
            "state": assessment["state"],
            "infrastructure": "implemented",
            "actual_study_status": "RUN" if actual else "NOT_RUN",
            "readiness_blockers": list(assessment.get("readiness_blockers", [])),
            "study_id": (assessment.get("protocol") or {}).get("study_id"),
            "study_version": (assessment.get("protocol") or {}).get("version"),
            "system_snapshot": (assessment.get("protocol") or {}).get("system_snapshot"),
            "ui_version": (assessment.get("protocol") or {}).get("ui_version"),
            "reader_count": len(assessment.get("readers", [])),
            "case_count": len(assessment.get("evaluation_cases", [])),
            "endpoints": endpoints or {},
            "safety": safety or {},
            "human_ai": human_ai or {},
            "human_factors_issues": list(issues),
            "limitations": list(limitations),
            "clinical_benefit_claim": None,
        }
    }


def render_json(report):
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _rows(value, path=""):
    if isinstance(value, dict) and {"numerator", "denominator", "estimate"} <= set(value):
        yield {"endpoint": path, **{key: value[key] for key in ("numerator", "denominator", "estimate")}}
    elif isinstance(value, dict):
        for key, child in sorted(value.items()):
            yield from _rows(child, f"{path}.{key}" if path else key)


def render_csv(report):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["endpoint", "numerator", "denominator", "estimate"])
    writer.writeheader()
    root = report["human_ai_reader_study"]
    for section in ("endpoints", "safety", "human_ai"):
        writer.writerows(_rows(root[section], section))
    return output.getvalue()


def render_markdown(report):
    root = report["human_ai_reader_study"]
    lines = [
        "# Human-AI Reader Study / Clinician Evaluation v1",
        "",
        f"- State: `{root['state']}`",
        f"- Infrastructure: `{root['infrastructure']}`",
        f"- Actual study: `{root['actual_study_status']}`",
        f"- Readers: {root['reader_count']}",
        f"- Cases: {root['case_count']}",
        "- Clinical benefit claim: none",
    ]
    if root["readiness_blockers"]:
        lines.extend(["", "## Readiness blockers", ""])
        lines.extend(f"- {blocker}" for blocker in root["readiness_blockers"])
    if root["limitations"]:
        lines.extend(["", "## Limitations", ""])
        lines.extend(f"- {item}" for item in root["limitations"])
    return "\n".join(lines) + "\n"
