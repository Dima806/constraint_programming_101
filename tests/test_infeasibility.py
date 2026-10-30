"""Infeasibility: over-constrained instances are *proven* infeasible, not looped on."""

from src.datasets import instances
from src.models.nurse_roster import solve_roster
from src.models.sudoku import solve_sudoku


def test_overconstrained_roster_is_proven_infeasible() -> None:
    result = solve_roster(instances.infeasible_roster(), time_limit=10.0)
    assert result.stats.is_infeasible
    assert result.assignment is None


def test_overspecified_sudoku_is_infeasible() -> None:
    result = solve_sudoku(instances.unsolvable_sudoku(), time_limit=10.0)
    assert result.stats.is_infeasible
    assert result.solved is None
