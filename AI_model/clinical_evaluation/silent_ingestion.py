"""Pure intake normalization for supplied payloads; no external system connector."""

from __future__ import annotations

from datetime import datetime

from .data_source_contract import TIME_FIELDS, classify_payload_fields, validate_data_source_contract


class SilentIngestionError(ValueError):
    pass


def _parse_time(value, field):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise SilentIngestionError(f"invalid {field}") from exc


def normalize_silent_payload(contract, payload):
    validate_data_source_contract(contract)
    classification = classify_payload_fields(contract, payload)
    if classification["status"] != "ACCEPTED":
        return {"status": classification["status"], "field_classification": classification, "normalized": None}
    missing_times = sorted(TIME_FIELDS - set(payload))
    if missing_times:
        raise SilentIngestionError("event times missing: " + ", ".join(missing_times))
    parsed = {field: _parse_time(payload[field], field) for field in TIME_FIELDS}
    if parsed["ingestion_time"] < min(
        time for field, time in parsed.items() if field not in {"ingestion_time", "hermes_run_time"}
    ):
        raise SilentIngestionError("ingestion time precedes supplied clinical event times")
    if parsed["hermes_run_time"] < parsed["ingestion_time"]:
        raise SilentIngestionError("Hermes run time precedes ingestion time")
    normalized = dict(payload)
    normalized["source_id"] = contract["source_id"]
    normalized["temporal_reasoning_time"] = select_temporal_reasoning_time(
        normalized, source_type=contract["source_type"]
    )
    normalized["ingestion_status"] = "ACCEPTED"
    return {"status": "ACCEPTED", "field_classification": classification, "normalized": normalized}


def select_temporal_reasoning_time(payload, *, source_type):
    if source_type in {"CXR", "CT", "IMAGING"}:
        field = "acquisition_time"
    elif source_type in {"LAB", "MICROBIOLOGY", "PATHOLOGY"}:
        field = "sample_time"
    else:
        field = "result_time"
    value = payload.get(field)
    if not value:
        raise SilentIngestionError(f"clinical event time unavailable: {field}")
    if value == payload.get("ingestion_time"):
        raise SilentIngestionError("clinical event time must not be substituted with ingestion time")
    return value
