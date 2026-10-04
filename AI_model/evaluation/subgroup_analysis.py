"""Declared-metadata subgroup analysis with small-sample warnings."""

from __future__ import annotations


def analyze_subgroups(records, subgroup_key, metric_fn, *, minimum_size=5):
    groups = {}
    for record in records:
        value = record.get("metadata", {}).get(subgroup_key)
        if value is not None:
            groups.setdefault(str(value), []).append(record)
    return {
        name: {
            "count": len(items),
            "metrics": metric_fn(items),
            "limitations": (
                [f"subgroup count {len(items)} is below pre-specified minimum {minimum_size}"]
                if len(items) < minimum_size else []
            ),
        }
        for name, items in sorted(groups.items())
    }
