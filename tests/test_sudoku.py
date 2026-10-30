"""Sudoku: solve valid boards, prove uniqueness, report unsolvable boards infeasible."""

from src.datasets import instances
from src.evaluation.correctness import verify_sudoku
from src.models.sudoku import count_solutions, has_unique_solution, solve_sudoku


def test_solves_valid_board() -> None:
    board = instances.valid_sudoku()
    result = solve_sudoku(board, time_limit=10.0)
    assert result.is_feasible
    assert result.solved is not None
    assert verify_sudoku(board, result.solved)


def test_matches_known_solution() -> None:
    board = instances.valid_sudoku()
    result = solve_sudoku(board, time_limit=10.0)
    assert result.solved == instances.VALID_SUDOKU_SOLUTION


def test_board_has_a_unique_solution() -> None:
    board = instances.valid_sudoku()
    assert has_unique_solution(board, time_limit=10.0)
    assert count_solutions(board, limit=2, time_limit=10.0) == 1


def test_unsolvable_board_is_infeasible() -> None:
    board = instances.unsolvable_sudoku()
    result = solve_sudoku(board, time_limit=10.0)
    assert result.stats.is_infeasible
    assert result.solved is None
