"""Nurse roster: every rule holds in the returned roster, and a new rule is one line."""

from dataclasses import replace

from src.datasets import instances
from src.evaluation.correctness import roster_violations, verify_roster
from src.models.nurse_roster import solve_roster


def test_feasible_roster_satisfies_every_rule() -> None:
    problem = instances.feasible_roster()
    result = solve_roster(problem, time_limit=10.0)
    assert result.is_feasible
    assert result.assignment is not None
    # No rule is violated anywhere in the roster.
    assert roster_violations(problem, result.assignment) == []


def test_tight_roster_is_feasible() -> None:
    problem = instances.tight_roster()
    result = solve_roster(problem, time_limit=10.0)
    assert result.is_feasible
    assert result.assignment is not None
    assert verify_roster(problem, result.assignment)


def test_adding_a_rule_is_one_constraint_not_a_rewrite() -> None:
    # Tightening "days off" from 2 to 3 is a one-line change to the problem spec.
    stricter = replace(instances.feasible_roster(), min_days_off=3)
    result = solve_roster(stricter, time_limit=10.0)
    assert result.is_feasible
    assert result.assignment is not None
    assert verify_roster(stricter, result.assignment)


def test_preferences_are_optimised_among_feasible_rosters() -> None:
    problem = instances.preference_roster()
    result = solve_roster(problem, time_limit=10.0)
    assert result.is_feasible
    assert result.stats.is_optimal
    assert result.stats.objective == len(problem.preferences)
