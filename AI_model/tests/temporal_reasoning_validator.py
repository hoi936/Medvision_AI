"""Deterministic structured validator for temporal golden-case fixtures."""


CORRESPONDENCE_STATES = {
    "confirmed": "CORRESPONDENCE_CONFIRMED",
    "probable": "CORRESPONDENCE_PROBABLE",
    "uncertain": "CORRESPONDENCE_UNCERTAIN",
    "not_same": "CORRESPONDENCE_NOT_SAME",
    "unknown": "CORRESPONDENCE_UNKNOWN",
}
COMPARABILITY_STATES = {
    "comparable": "COMPARABLE",
    "limited": "LIMITED_COMPARABILITY",
    "not_comparable": "NOT_COMPARABLE",
    "unknown": "COMPARABILITY_UNKNOWN",
}
CHANGE_STATES = {
    "new": "NEW",
    "resolved": "RESOLVED",
    "improved": "IMPROVED",
    "worsened": "WORSENED",
    "stable": "STABLE",
}


def evaluate_temporal_case(case):
    """Classify supplied structured facts without inventing missing evidence."""
    facts = case["temporal"]
    correspondence = CORRESPONDENCE_STATES[facts["correspondence"]]
    comparability = COMPARABILITY_STATES[facts["comparability"]]

    if facts.get("conflict"):
        state = "TEMPORAL_CONFLICT"
    elif facts.get("prior") == "missing":
        state = "PRIOR_DATA_MISSING"
    elif facts.get("order", "known") != "known":
        state = "INTERVAL_CHANGE_INDETERMINATE"
    elif facts["correspondence"] == "not_same":
        state = "COMPARISON_NOT_POSSIBLE"
    elif facts["comparability"] == "not_comparable":
        state = "COMPARISON_NOT_POSSIBLE"
    elif facts.get("ai_only") or facts.get("omission_only"):
        state = "INTERVAL_CHANGE_INDETERMINATE"
    elif facts["correspondence"] in {"uncertain", "unknown"}:
        state = "INTERVAL_CHANGE_INDETERMINATE"
    elif facts["comparability"] in {"limited", "unknown"}:
        state = "INTERVAL_CHANGE_INDETERMINATE"
    elif (
        facts.get("prior") == "present"
        and facts.get("interval_absent")
        and facts.get("current") == "present"
    ):
        state = "RECURRENT"
    elif facts.get("change_evidence"):
        state = CHANGE_STATES[facts["change_evidence"]]
    elif facts.get("repeated_presence"):
        state = "PERSISTENT"
    else:
        state = "INTERVAL_CHANGE_INDETERMINATE"

    return {
        "state": state,
        "correspondence": correspondence,
        "comparability": comparability,
        "causal_attribution": (
            "established"
            if facts.get("causal_attribution_explicit")
            else "not_established"
        ),
    }
