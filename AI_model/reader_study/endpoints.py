"""Deterministic descriptive reader-study endpoints without a composite score."""

from __future__ import annotations

from .event_log import event_duration_seconds, validate_reader_event


def rate(numerator, denominator):
    return {
        "numerator": int(numerator),
        "denominator": int(denominator),
        "estimate": None if denominator == 0 else numerator / denominator,
    }


def descriptive_endpoints(events):
    validated = [validate_reader_event(event) for event in events]
    completed = [event for event in validated if event["completed"]]
    return {
        "reference_agreement": rate(sum(bool(event.get("reference_agreement")) for event in validated), len(validated)),
        "major_error": rate(sum(bool(event.get("major_error")) for event in validated), len(validated)),
        "unsafe_false_upgrade": rate(sum(bool(event.get("unsafe_false_upgrade")) for event in validated), len(validated)),
        "critical_miss": rate(sum(bool(event.get("critical_miss")) for event in validated), len(validated)),
        "completion": rate(len(completed), len(validated)),
        "reading_time_seconds": {
            "count": len(completed),
            "values": [event_duration_seconds(event) for event in completed],
            "mean": (
                sum(event_duration_seconds(event) for event in completed) / len(completed)
                if completed else None
            ),
        },
    }
