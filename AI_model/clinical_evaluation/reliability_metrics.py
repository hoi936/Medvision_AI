"""Descriptive technical reliability and latency metrics without an overall score."""

from __future__ import annotations

import math


def rate(numerator, denominator):
    return {
        "numerator": int(numerator),
        "denominator": int(denominator),
        "estimate": None if denominator == 0 else numerator / denominator,
    }


def percentile(values, probability):
    if not 0 <= probability <= 1:
        raise ValueError("probability must be between zero and one")
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def reliability_metrics(records):
    count = len(records)
    flags = {
        "ingestion_success": "ingestion_success",
        "normalization_success": "normalization_success",
        "invocation_success": "invocation_success",
        "parse_success": "parse_success",
        "trace_completion": "trace_complete",
        "provider_transient_failure": "provider_transient_failure",
        "provider_configuration_failure": "provider_configuration_failure",
        "final_candidate_generation_success": "final_candidate_generated",
        "end_to_end_availability": "end_to_end_available",
    }
    output = {
        name: rate(sum(bool(record.get(field, False)) for record in records), count)
        for name, field in flags.items()
    }
    latencies = [record["latency_ms"] for record in records if record.get("latency_ms") is not None]
    output["latency_ms"] = {
        "count": len(latencies),
        "p50": percentile(latencies, 0.50),
        "p90": percentile(latencies, 0.90),
        "p95": percentile(latencies, 0.95),
        "p99": percentile(latencies, 0.99),
        "raw_values": list(latencies),
    }
    return output
