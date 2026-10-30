"""Named, self-contained problem instances with *known* solvability.

The project's claims are about finding valid solutions and proving infeasibility,
both of which need instances whose answer is known in advance so every result is
checkable. No external data.
"""

from src.models.assignment import ExamTimetabling
from src.models.bin_packing import BinPacking
from src.models.job_shop import JobShopProblem
from src.models.nurse_roster import RosterProblem
from src.models.sudoku import Grid

# --------------------------------------------------------------------------- #
# Sudoku
# --------------------------------------------------------------------------- #

# A classic, uniquely solvable 9x9 puzzle (0 = blank).
VALID_SUDOKU: Grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

# The unique solution to VALID_SUDOKU.
VALID_SUDOKU_SOLUTION: Grid = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

# An over-specified board: two 5s in the first row make it provably unsolvable.
UNSOLVABLE_SUDOKU: Grid = [
    [5, 3, 5, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def valid_sudoku() -> Grid:
    """A uniquely solvable 9x9 board."""
    return [row[:] for row in VALID_SUDOKU]


def unsolvable_sudoku() -> Grid:
    """A board that is provably infeasible (a repeated digit in a row)."""
    return [row[:] for row in UNSOLVABLE_SUDOKU]


# --------------------------------------------------------------------------- #
# Nurse rostering
# --------------------------------------------------------------------------- #


def feasible_roster() -> RosterProblem:
    """Comfortably feasible: enough nurses to cover every shift with rest and days off."""
    return RosterProblem(
        num_nurses=6,
        num_days=7,
        demand=(1, 1, 1),
        min_days_off=2,
        senior_nurses=(0, 1),
    )


def tight_roster() -> RosterProblem:
    """Exactly feasible: fewer nurses, so the rules only just hold."""
    return RosterProblem(
        num_nurses=5,
        num_days=7,
        demand=(1, 1, 1),
        min_days_off=2,
        senior_nurses=(0, 1),
    )


def infeasible_roster() -> RosterProblem:
    """Over-constrained: demand exceeds what the nurses can possibly cover."""
    return RosterProblem(
        num_nurses=4,
        num_days=7,
        demand=(3, 3, 3),
        min_days_off=2,
        senior_nurses=(0, 1),
    )


def preference_roster() -> RosterProblem:
    """A feasible instance carrying preferences, turning it into an optimisation."""
    return RosterProblem(
        num_nurses=6,
        num_days=7,
        demand=(1, 1, 1),
        min_days_off=2,
        senior_nurses=(0, 1),
        preferences=(
            (2, 0, 0),
            (3, 1, 1),
            (4, 2, 0),
            (5, 3, 1),
        ),
    )


# --------------------------------------------------------------------------- #
# Job-shop scheduling
# --------------------------------------------------------------------------- #

# The canonical 3-job / 3-machine instance with a known optimal makespan of 11.
SMALL_JOB_SHOP_OPTIMUM = 11


def small_job_shop() -> JobShopProblem:
    """A 3-job, 3-machine instance whose optimal makespan is known to be 11."""
    jobs = (
        ((0, 3), (1, 2), (2, 2)),
        ((0, 2), (2, 1), (1, 4)),
        ((1, 4), (2, 3)),
    )
    return JobShopProblem(jobs=jobs, num_machines=3)


# --------------------------------------------------------------------------- #
# Exam timetabling
# --------------------------------------------------------------------------- #


def small_timetabling() -> ExamTimetabling:
    """Four exams into two rooms across two slots, with two conflict pairs."""
    return ExamTimetabling(
        num_exams=4,
        exam_sizes=(30, 20, 25, 15),
        room_caps=(30, 25),
        num_slots=2,
        conflicts=((0, 1), (2, 3)),
    )


# --------------------------------------------------------------------------- #
# Bin packing
# --------------------------------------------------------------------------- #

# Items of total size 18 into capacity-6 bins: optimum is 3 bins.
SMALL_BIN_PACKING_OPTIMUM = 3


def small_bin_packing() -> BinPacking:
    """Six items into capacity-6 bins; the optimum is 3 bins."""
    return BinPacking(item_sizes=(4, 4, 3, 3, 2, 2), bin_capacity=6)
