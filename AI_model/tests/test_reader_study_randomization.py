"""Counterbalancing and case-order tests."""

from reader_study.randomization import assign_ab_ba, build_randomization_plan, randomized_case_order
from reader_study_fixtures import reader


def test_ab_ba_assignment_is_deterministic_and_balanced_within_one_reader():
    reader_ids = [f"R{i}" for i in range(1, 8)]
    first = assign_ab_ba(reader_ids, seed=17)
    second = assign_ab_ba(reader_ids, seed=17)
    assert first == second
    counts = {sequence: list(first.values()).count(sequence) for sequence in ("AB", "BA")}
    assert abs(counts["AB"] - counts["BA"]) <= 1


def test_case_order_is_reproducible_label_agnostic_and_complete():
    case_ids = ["C1", "C2", "C3", "C4", "C5"]
    first = randomized_case_order(case_ids, reader_id="R1", session_id="S1", seed=4)
    assert first == randomized_case_order(case_ids, reader_id="R1", session_id="S1", seed=4)
    assert first != randomized_case_order(case_ids, reader_id="R2", session_id="S1", seed=4)
    assert first != randomized_case_order(case_ids, reader_id="R1", session_id="S2", seed=4)
    assert sorted(first) == sorted(case_ids)


def test_randomization_plan_has_every_reader_session_and_no_case_loss():
    readers = [reader("R1"), reader("R2")]
    cases = ["C1", "C2", "C3"]
    plan = build_randomization_plan(readers, cases, session_ids=["SESSION-1", "SESSION-2"], seed=9)
    assert set(plan["sequences"].values()) == {"AB", "BA"}
    assert len(plan["case_orders"]) == 4
    assert all(sorted(order) == cases for order in plan["case_orders"].values())
