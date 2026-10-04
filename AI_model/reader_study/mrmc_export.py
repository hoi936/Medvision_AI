"""Tidy MRMC export only; inferential analysis belongs in an MRMC-aware tool."""

from __future__ import annotations

import csv
import io
import json

from .event_log import event_duration_seconds, validate_reader_event


MRMC_ANALYSIS_NOTE = (
    "Inferential analysis must account for both reader and case effects; "
    "do not treat interpretations as independent observations."
)
FIELDS = (
    "reader_id", "case_id", "condition", "reference", "reader_result",
    "score_if_protocol_has_one", "correct", "time_seconds", "error_class",
)


def tidy_rows(events):
    rows = []
    for event in events:
        validate_reader_event(event)
        rows.append({
            "reader_id": event["reader_id"],
            "case_id": event["case_id"],
            "condition": event["condition"],
            "reference": event.get("reference"),
            "reader_result": event.get("reader_result"),
            "score_if_protocol_has_one": event.get("protocol_score"),
            "correct": event.get("reference_agreement"),
            "time_seconds": event_duration_seconds(event),
            "error_class": event.get("error_class"),
        })
    return rows


def export_csv(events):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(tidy_rows(events))
    return output.getvalue()


def export_json(events):
    return json.dumps(
        {"analysis_note": MRMC_ANALYSIS_NOTE, "rows": tidy_rows(events)},
        ensure_ascii=False, sort_keys=True, indent=2,
    ) + "\n"
