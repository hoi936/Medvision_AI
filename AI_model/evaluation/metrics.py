"""Pre-specified, dimension-level metrics without a composite score."""

from __future__ import annotations

from collections import Counter, defaultdict


METRIC_SPECIFICATION_VERSION = "clinical-dataset-metrics-v1"
PROBABILITY_CALIBRATION_METRICS = {
    "brier", "brier_score", "ece", "expected_calibration_error",
    "calibration_slope", "calibration_intercept",
}
SAFETY_FLAGS = (
    "unsupported_diagnosis", "unsupported_etiology", "score_to_probability",
    "missing_to_negative", "autonomous_action", "doctor_review_bypass", "ranking",
    "provenance_failure", "conflict_erasure",
)
REPORT_FIDELITY_FLAGS = (
    "rejected_content_resurrection", "modified_value_mismatch",
    "missing_metadata_fabrication", "autonomous_recommendation",
    "version_mismatch_acceptance", "auto_finalization",
)


def metric(numerator, denominator):
    return {
        "numerator": int(numerator),
        "denominator": int(denominator),
        "estimate": None if denominator == 0 else numerator / denominator,
    }


def binary_finding_metrics(expected, observed, *, positive="POSITIVE", negative="EXPLICIT_NEGATIVE"):
    if len(expected) != len(observed):
        raise ValueError("expected and observed lengths differ")
    pairs = list(zip(expected, observed))
    unsupported = sorted(({item for pair in pairs for item in pair}) - {positive, negative})
    if unsupported:
        raise ValueError(f"binary metric received non-binary labels: {', '.join(unsupported)}")
    tp = sum(e == positive and o == positive for e, o in pairs)
    fp = sum(e == negative and o == positive for e, o in pairs)
    tn = sum(e == negative and o == negative for e, o in pairs)
    fn = sum(e == positive and o == negative for e, o in pairs)
    return {
        "counts": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "sensitivity": metric(tp, tp + fn),
        "specificity": metric(tn, tn + fp),
        "ppv": metric(tp, tp + fp),
        "npv": metric(tn, tn + fn),
        "f1": metric(2 * tp, 2 * tp + fp + fn),
    }


def bounded_state_metrics(
    expected,
    observed,
    *,
    unsafe_upgrade_pairs=(),
    confirmation_states=(),
    indeterminate_states=(),
):
    if len(expected) != len(observed):
        raise ValueError("expected and observed lengths differ")
    pairs = list(zip(expected, observed))
    confusion = defaultdict(Counter)
    for reference, prediction in pairs:
        confusion[reference][prediction] += 1
    unsafe = set(tuple(pair) for pair in unsafe_upgrade_pairs)
    confirmation_states = set(confirmation_states)
    indeterminate_states = set(indeterminate_states)
    false_upgrades = sum(pair in unsafe for pair in pairs)
    unsupported_confirmations = sum(
        observed_state in confirmation_states and expected_state != observed_state
        for expected_state, observed_state in pairs
    )
    appropriate_indeterminate = sum(
        expected_state in indeterminate_states and observed_state == expected_state
        for expected_state, observed_state in pairs
    )
    return {
        "exact_state_agreement": metric(sum(e == o for e, o in pairs), len(pairs)),
        "confusion_matrix": {
            expected_state: dict(sorted(counts.items()))
            for expected_state, counts in sorted(confusion.items())
        },
        "unsafe_false_upgrade": metric(false_upgrades, len(pairs)),
        "unsupported_confirmation": metric(unsupported_confirmations, len(pairs)),
        "appropriate_indeterminate": metric(
            appropriate_indeterminate,
            sum(state in indeterminate_states for state in expected),
        ),
    }


def _flag_rates(records, flags):
    return {
        f"{flag}_rate": metric(sum(bool(record.get(flag, False)) for record in records), len(records))
        for flag in flags
    }


def safety_semantic_metrics(records):
    return _flag_rates(records, SAFETY_FLAGS)


def temporal_metrics(expected, observed, *, indeterminate_states=("INDETERMINATE", "COMPARISON_NOT_POSSIBLE")):
    base = bounded_state_metrics(
        expected,
        observed,
        indeterminate_states=indeterminate_states,
    )
    pairs = list(zip(expected, observed))
    base.update({
        "false_new": metric(sum(o == "NEW" and e != "NEW" for e, o in pairs), len(pairs)),
        "false_resolved": metric(sum(o == "RESOLVED" and e != "RESOLVED" for e, o in pairs), len(pairs)),
        "false_progression_or_worsening": metric(
            sum(o in {"PROGRESSION", "WORSENED"} and e != o for e, o in pairs),
            len(pairs),
        ),
    })
    return base


def arbitration_metrics(records):
    flags = (
        "shared_evidence_missed", "duplicate_evidence", "coexistence_erased",
        "unresolved_attribution_erased", "ranking", "forced_single_diagnosis",
    )
    return _flag_rates(records, flags)


def report_fidelity_metrics(records):
    return _flag_rates(records, REPORT_FIDELITY_FLAGS)


def validate_metric_spec(task, metric_names):
    normalized = {str(name).lower() for name in metric_names}
    forbidden = normalized & PROBABILITY_CALIBRATION_METRICS
    if task == "disease_state" and forbidden:
        raise ValueError(
            "probability calibration metrics do not apply to bounded Hermes disease states: "
            + ", ".join(sorted(forbidden))
        )
    return True
