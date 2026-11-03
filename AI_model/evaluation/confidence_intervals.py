"""Wilson proportion intervals and patient-level bootstrap helpers."""

from __future__ import annotations

import math
import random


def wilson_interval(numerator, denominator, *, z=1.959963984540054):
    if denominator < 0 or numerator < 0 or numerator > denominator:
        raise ValueError("invalid binomial numerator/denominator")
    if denominator == 0:
        return {"method": "wilson", "level": 0.95, "lower": None, "upper": None}
    proportion = numerator / denominator
    z2 = z * z
    denominator_term = 1 + z2 / denominator
    center = (proportion + z2 / (2 * denominator)) / denominator_term
    margin = z * math.sqrt(
        proportion * (1 - proportion) / denominator + z2 / (4 * denominator * denominator)
    ) / denominator_term
    return {
        "method": "wilson",
        "level": 0.95,
        "lower": max(0.0, center - margin),
        "upper": min(1.0, center + margin),
    }


def _percentile(values, probability):
    ordered = sorted(values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def patient_level_bootstrap(records, metric_fn, *, iterations=1000, seed=None, patient_key="patient_group_id"):
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    grouped = {}
    for record in records:
        patient_id = record.get(patient_key)
        if not patient_id:
            raise ValueError("every bootstrap record requires patient_group_id")
        grouped.setdefault(patient_id, []).append(record)
    patient_ids = sorted(grouped)
    if not patient_ids:
        return {"method": "patient_level_bootstrap", "iterations": iterations, "lower": None, "upper": None}
    rng = random.Random(seed)
    estimates = []
    for _ in range(iterations):
        sampled_ids = [rng.choice(patient_ids) for _ in patient_ids]
        sampled_records = [record for patient_id in sampled_ids for record in grouped[patient_id]]
        estimate = metric_fn(sampled_records)
        if estimate is not None:
            estimates.append(float(estimate))
    return {
        "method": "patient_level_bootstrap",
        "unit": "patient",
        "iterations": iterations,
        "patient_count": len(patient_ids),
        "lower": _percentile(estimates, 0.025),
        "upper": _percentile(estimates, 0.975),
    }
