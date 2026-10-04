"""Deterministic evidence-ledger builder for arbitration golden fixtures."""

from copy import deepcopy


HYPOTHESIS_STATES = {
    "HYPOTHESIS_SUPPORTED",
    "HYPOTHESIS_POSSIBLE",
    "HYPOTHESIS_INDETERMINATE",
    "HYPOTHESIS_CONFLICTED",
    "HYPOTHESIS_NOT_ESTABLISHED",
}
PRIORITIES = {"routine": 0, "elevated": 1, "high": 2}
FORBIDDEN_ORDERING_KEYS = {
    "rank", "ranking", "score", "probability", "percent", "top_diagnosis", "winner"
}


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def validate_arbitration_output(output):
    """Reject disease-ordering/probability fields and require the frozen schema."""
    found = FORBIDDEN_ORDERING_KEYS.intersection(_walk_keys(output))
    if found:
        raise ValueError(f"forbidden disease-ordering fields: {sorted(found)}")
    arbitration = output.get("arbitration")
    if not isinstance(arbitration, dict):
        raise ValueError("arbitration object is required")
    required = {
        "hypotheses", "evidence_ledger", "evidence_matrix", "relations",
        "global_conflicts", "missing_information", "review", "synthesis",
    }
    if set(arbitration) != required:
        raise ValueError("arbitration schema mismatch")
    relation_keys = {
        "competing_hypotheses", "possible_coexisting_processes",
        "supported_coexisting_processes", "shared_evidence_groups",
        "unresolved_attribution",
    }
    if set(arbitration["relations"]) != relation_keys:
        raise ValueError("arbitration relations schema mismatch")
    if arbitration["review"].get("doctor_review_required") is not True:
        raise ValueError("doctor review is required")
    if arbitration["synthesis"].get("no_numeric_ranking") is not True:
        raise ValueError("numeric ranking must be disabled")
    return True


def relationship_states(output):
    """Return the non-numeric relationship labels implied by an output."""
    arbitration = output["arbitration"]
    relations = arbitration["relations"]
    states = set()
    if relations["competing_hypotheses"]:
        states.add("COMPETING_HYPOTHESES_PRESENT")
    if relations["possible_coexisting_processes"]:
        states.update({"COEXISTING_PROCESSES_POSSIBLE", "MUTUAL_EXCLUSIVITY_NOT_ESTABLISHED"})
    if relations["supported_coexisting_processes"]:
        states.add("COEXISTING_PROCESSES_SUPPORTED")
    if relations["shared_evidence_groups"]:
        states.add("SHARED_EVIDENCE_PRESENT")
    if relations["unresolved_attribution"]:
        states.add("EVIDENCE_ATTRIBUTION_UNRESOLVED")
    if any(len(item["supports"]) == 1 for item in arbitration["evidence_matrix"]):
        states.add("DISTINCT_EVIDENCE_PRESENT")
    if any(item.get("duplicate_count", 1) > 1 for item in arbitration["evidence_ledger"]):
        states.add("DUPLICATE_EVIDENCE_DEDUPLICATED")
    return states


def build_arbitration(case):
    """Normalize and de-duplicate evidence, then derive non-numeric relations."""
    raw_hypotheses = case["arbitration"]["hypotheses"]
    raw_evidence = case["arbitration"]["evidence"]
    names = [item["name"] for item in raw_hypotheses]
    if len(names) != len(set(names)):
        raise ValueError("duplicate hypothesis names")

    hypotheses = []
    for index, item in enumerate(raw_hypotheses, 1):
        if item["state"] not in HYPOTHESIS_STATES:
            raise ValueError(f"invalid hypothesis state: {item['state']}")
        if item["priority"] not in PRIORITIES:
            raise ValueError(f"invalid review priority: {item['priority']}")
        hypotheses.append({
            "id": f"H{index}",
            "name": item["name"],
            "module": item.get("module", item["name"]),
            "support_state": item["state"],
            "evidence_completeness": item.get("completeness", "unknown"),
            "review_priority": item["priority"],
            "supporting_evidence": [],
            "distinct_supporting_evidence": [],
            "shared_supporting_evidence": [],
            "contradicting_evidence": [],
            "missing_evidence": list(item.get("missing", [])),
            "conflicts": list(item.get("conflicts", [])),
            "requires_doctor_review": True,
        })

    by_name = {item["name"]: item for item in hypotheses}
    normalized = {}
    for raw in raw_evidence:
        key = raw["key"]
        if key in normalized:
            normalized[key]["supports"].update(raw.get("supports", []))
            normalized[key]["contradicts"].update(raw.get("contradicts", []))
            normalized[key]["provenance"].add(raw.get("provenance", "unknown"))
            normalized[key]["duplicate_count"] += 1
            continue
        normalized[key] = {
            "type": raw.get("type", "unknown"),
            "value": raw.get("value", key),
            "source": raw.get("source", "unknown"),
            "modality_or_test": raw.get("modality_or_test", "unknown"),
            "timestamp": raw.get("timestamp", "unknown"),
            "provenance": {raw.get("provenance", "unknown")},
            "uncertainty": raw.get("uncertainty", "explicit_unknown"),
            "supports": set(raw.get("supports", [])),
            "contradicts": set(raw.get("contradicts", [])),
            "duplicate_count": 1,
        }

    ledger = []
    matrix = []
    for index, (key, item) in enumerate(normalized.items(), 1):
        evidence_id = f"E{index}"
        supports = sorted(item.pop("supports"))
        contradicts = sorted(item.pop("contradicts"))
        unknown_names = (set(supports) | set(contradicts)) - set(by_name)
        if unknown_names:
            raise ValueError(f"unknown hypothesis references: {sorted(unknown_names)}")
        item["provenance"] = sorted(item["provenance"])
        ledger.append({"id": evidence_id, **item})
        matrix.append({
            "evidence_id": evidence_id,
            "supports": supports,
            "contradicts": contradicts,
            "shared": len(supports) > 1,
        })
        for name in supports:
            hypothesis = by_name[name]
            hypothesis["supporting_evidence"].append(evidence_id)
            target = "shared_supporting_evidence" if len(supports) > 1 else "distinct_supporting_evidence"
            hypothesis[target].append(evidence_id)
        for name in contradicts:
            by_name[name]["contradicting_evidence"].append(evidence_id)

    shared = [item["evidence_id"] for item in matrix if item["shared"]]
    distinct = [item["evidence_id"] for item in matrix if len(item["supports"]) == 1]
    relations = {
        "competing_hypotheses": names if len(names) > 1 and shared else [],
        "possible_coexisting_processes": names if len(names) > 1 else [],
        "supported_coexisting_processes": [],
        "shared_evidence_groups": shared,
        "unresolved_attribution": shared if shared and not case["arbitration"].get("attribution_resolved") else [],
    }

    independently_supported = [
        item["name"] for item in hypotheses
        if item["support_state"] == "HYPOTHESIS_SUPPORTED"
        and item["distinct_supporting_evidence"]
    ]
    if len(independently_supported) > 1:
        relations["supported_coexisting_processes"] = independently_supported

    highest = max((item["priority"] for item in raw_hypotheses), key=PRIORITIES.get)
    output = {
        "arbitration": {
            "hypotheses": hypotheses,
            "evidence_ledger": ledger,
            "evidence_matrix": matrix,
            "relations": relations,
            "global_conflicts": deepcopy(case["arbitration"].get("conflicts", [])),
            "missing_information": deepcopy(case["arbitration"].get("missing", [])),
            "review": {
                "highest_priority": highest,
                "priority_drivers": [
                    item["name"] for item in raw_hypotheses if item["priority"] == highest
                ],
                "doctor_review_required": True,
            },
            "synthesis": {
                "summary": case["description"],
                "uncertainty": case["arbitration"].get("uncertainty", ""),
                "no_numeric_ranking": True,
            },
        }
    }
    validate_arbitration_output(output)
    return output
