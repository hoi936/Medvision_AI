"""Deterministic summaries for provider-backed E2E trial results."""

from __future__ import annotations

from collections import Counter

from .provider_backed_result import FAILURE_CLASSES


def summarize_results(results, *, skipped=0, mode="REAL_GATE"):
    classes = Counter(
        result["provider_backed_result"]["failure"]["class"] for result in results
    )
    invariant_failures = Counter(
        invariant
        for result in results
        for invariant in result["provider_backed_result"]["invariants"]["failed"]
    )
    return {
        "mode": mode,
        "cases_attempted": len(results),
        "skipped": int(skipped),
        "outcomes": {name: classes[name] for name in sorted(FAILURE_CLASSES)},
        "invariant_failures": dict(sorted(invariant_failures.items())),
    }
