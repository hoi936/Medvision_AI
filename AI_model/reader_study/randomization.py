"""Reproducible AB/BA allocation and label-agnostic case ordering."""

from __future__ import annotations

import hashlib
import random


def _unique(values, label):
    values = list(values)
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label} values are not allowed")
    if not values:
        raise ValueError(f"{label} values are required")
    return values


def assign_ab_ba(reader_ids, *, seed):
    reader_ids = _unique(reader_ids, "reader")
    shuffled = sorted(reader_ids)
    random.Random(seed).shuffle(shuffled)
    return {
        reader_id: ("AB" if index % 2 == 0 else "BA")
        for index, reader_id in enumerate(shuffled)
    }


def randomized_case_order(case_ids, *, reader_id, session_id, seed):
    case_ids = _unique(case_ids, "case")
    material = f"{seed}|{reader_id}|{session_id}".encode("utf-8")
    derived_seed = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    ordered = sorted(case_ids)
    random.Random(derived_seed).shuffle(ordered)
    return ordered


def build_randomization_plan(readers, case_ids, *, session_ids, seed):
    sequences = assign_ab_ba([reader["reader_id"] for reader in readers], seed=seed)
    orders = {
        f"{reader['reader_id']}:{session_id}": randomized_case_order(
            case_ids, reader_id=reader["reader_id"], session_id=session_id, seed=seed
        )
        for reader in readers
        for session_id in session_ids
    }
    return {"method": "AB_BA_COUNTERBALANCED", "seed": seed, "sequences": sequences, "case_orders": orders}
