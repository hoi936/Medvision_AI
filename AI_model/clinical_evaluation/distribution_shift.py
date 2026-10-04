"""Descriptive stratification only; this module never adapts or retrains a model."""

from __future__ import annotations

from collections import Counter


def categorical_distribution(records, field):
    counts = Counter(record.get(field, "MISSING") for record in records)
    denominator = len(records)
    return {
        str(value): {
            "count": count,
            "fraction": None if denominator == 0 else count / denominator,
        }
        for value, count in sorted(counts.items(), key=lambda item: str(item[0]))
    }


def missingness_distribution(records, fields):
    return {
        field: {
            "missing": sum(record.get(field) is None for record in records),
            "denominator": len(records),
            "fraction": None if not records else sum(record.get(field) is None for record in records) / len(records),
        }
        for field in fields
    }


def positive_finding_frequency(records):
    counts = Counter(
        finding
        for record in records
        for finding in record.get("positive_findings", [])
    )
    return {
        finding: {"count": count, "case_fraction": count / len(records) if records else None}
        for finding, count in sorted(counts.items())
    }


def stratify_metadata(records):
    return {
        field: categorical_distribution(records, field)
        for field in ("site", "modality", "projection", "time_period", "protocol")
    }
