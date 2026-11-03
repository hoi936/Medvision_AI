"""Offline session plans and explicit-start state transitions."""

from __future__ import annotations


def condition_for_sequence(sequence, session_index):
    mapping = {
        "AB": ("UNAIDED", "HERMES_ASSISTED"),
        "BA": ("HERMES_ASSISTED", "UNAIDED"),
    }
    if sequence not in mapping or session_index not in {1, 2}:
        raise ValueError("invalid sequence/session index")
    return mapping[sequence][session_index - 1]


def build_session_plan(readers, randomization_plan, *, study_id, ui_version):
    plans = []
    for reader in readers:
        reader_id = reader["reader_id"]
        sequence = randomization_plan["sequences"][reader_id]
        for session_index in (1, 2):
            session_id = f"SESSION-{session_index}"
            plans.append({
                "study_id": study_id,
                "reader_id": reader_id,
                "session_id": session_id,
                "sequence": sequence,
                "condition": condition_for_sequence(sequence, session_index),
                "case_order": randomization_plan["case_orders"][f"{reader_id}:{session_id}"],
                "ui_version": ui_version,
                "status": "PLANNED",
            })
    return plans


def begin_session(session, *, explicit_start=False):
    if explicit_start is not True:
        raise PermissionError("reader-study sessions require an explicit authorized start")
    if session.get("status") != "PLANNED":
        raise ValueError("only planned sessions can start")
    return {**session, "status": "RUNNING"}
