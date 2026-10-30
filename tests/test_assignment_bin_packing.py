"""Timetabling and bin packing: valid assignments, known optimum for packing."""

from src.datasets import instances
from src.evaluation.correctness import verify_bin_packing, verify_timetabling
from src.models.assignment import solve_timetabling
from src.models.bin_packing import solve_bin_packing


def test_timetabling_places_every_exam_within_the_rules() -> None:
    problem = instances.small_timetabling()
    result = solve_timetabling(problem, time_limit=10.0)
    assert result.is_feasible
    assert result.placement is not None
    assert verify_timetabling(problem, result.placement)


def test_bin_packing_reaches_known_optimum() -> None:
    problem = instances.small_bin_packing()
    result = solve_bin_packing(problem, time_limit=10.0)
    assert result.is_feasible
    assert result.stats.is_optimal
    assert result.num_bins_used == instances.SMALL_BIN_PACKING_OPTIMUM
    assert result.assignment is not None
    assert verify_bin_packing(problem, result.assignment)
