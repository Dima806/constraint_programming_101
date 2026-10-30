"""Sudoku as a constraint-satisfaction problem.

The gentlest demonstration of the thesis: a Sudoku is just "every row, column, and
box holds all different digits". We declare that with the all-different global
constraint and let the solver fill the board, prove uniqueness, or report that an
over-specified board is impossible.
"""

import math
from dataclasses import dataclass

from ortools.sat.python import cp_model

from src.cp.builder import add_all_different, new_model, solve
from src.cp.explain import SolveStats

# A board is an n x n grid; 0 marks a blank cell.
Grid = list[list[int]]


@dataclass(frozen=True)
class SudokuResult:
    """Outcome of solving a board: the filled grid (if any) and solve statistics."""

    solved: Grid | None
    stats: SolveStats

    @property
    def is_feasible(self) -> bool:
        return self.stats.is_feasible


def _box_size(side: int) -> int:
    box = math.isqrt(side)
    if box * box != side:
        msg = f"board side {side} is not a perfect square"
        raise ValueError(msg)
    return box


def build_model(board: Grid) -> tuple[cp_model.CpModel, list[list[cp_model.IntVar]]]:
    """Build the CP-SAT model for a board, returning the model and its cell variables."""
    side = len(board)
    box = _box_size(side)
    model = new_model()

    cells = [
        [model.new_int_var(1, side, f"cell_{row}_{col}") for col in range(side)]
        for row in range(side)
    ]

    # Givens: pin the pre-filled cells.
    for row in range(side):
        for col in range(side):
            given = board[row][col]
            if given != 0:
                model.add(cells[row][col] == given)

    # Rules: all-different on every row, column, and box.
    for row in range(side):
        add_all_different(model, cells[row])
    for col in range(side):
        add_all_different(model, [cells[row][col] for row in range(side)])
    for box_row in range(0, side, box):
        for box_col in range(0, side, box):
            add_all_different(
                model,
                [cells[box_row + i][box_col + j] for i in range(box) for j in range(box)],
            )

    return model, cells


def solve_sudoku(board: Grid, *, time_limit: float = 10.0, seed: int = 42) -> SudokuResult:
    """Fill the board if possible; otherwise report it infeasible."""
    model, cells = build_model(board)
    solver, stats = solve(model, time_limit=time_limit, seed=seed)
    solved: Grid | None = None
    if stats.is_feasible:
        solved = [[int(solver.value(cell)) for cell in row] for row in cells]
    return SudokuResult(solved=solved, stats=stats)


class _SolutionCounter(cp_model.CpSolverSolutionCallback):
    """Counts solutions and stops once a given limit is reached."""

    def __init__(self, limit: int) -> None:
        super().__init__()
        self._limit = limit
        self.count = 0

    def on_solution_callback(self) -> None:
        self.count += 1
        if self.count >= self._limit:
            self.stop_search()


def count_solutions(board: Grid, *, limit: int = 2, time_limit: float = 10.0) -> int:
    """Count solutions up to ``limit`` (enough to tell unsolvable/unique/ambiguous apart)."""
    model, _cells = build_model(board)
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.max_time_in_seconds = time_limit
    # Solution enumeration must run single-threaded.
    solver.parameters.num_search_workers = 1
    counter = _SolutionCounter(limit)
    solver.solve(model, counter)
    return counter.count


def has_unique_solution(board: Grid, *, time_limit: float = 10.0) -> bool:
    """True iff the board has exactly one solution."""
    return count_solutions(board, limit=2, time_limit=time_limit) == 1
