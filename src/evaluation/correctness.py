"""Independent verification: re-check that every constraint holds in a returned solution.

Verify, don't trust. A CP model is only as good as its encoding, so each solver
result is re-checked here against the rules stated from scratch. A mis-modelled rule
shows up as a failing verification.
"""

from src.models.assignment import ExamTimetabling, Placement
from src.models.bin_packing import BinAssignment, BinPacking
from src.models.job_shop import JobShopProblem
from src.models.nurse_roster import Assignment, RosterProblem
from src.models.sudoku import Grid


def sudoku_violations(board: Grid, solved: Grid) -> list[str]:
    """Return a list of rule violations in a solved board (empty means valid)."""
    side = len(board)
    problems: list[str] = []

    # Givens preserved.
    for row in range(side):
        for col in range(side):
            given = board[row][col]
            if given != 0 and solved[row][col] != given:
                problems.append(f"given at ({row},{col}) changed from {given}")

    # Values in range.
    for row in range(side):
        for col in range(side):
            if not 1 <= solved[row][col] <= side:
                problems.append(f"value {solved[row][col]} at ({row},{col}) out of range")

    expected = set(range(1, side + 1))

    # Rows and columns all-different.
    for row in range(side):
        if {solved[row][col] for col in range(side)} != expected:
            problems.append(f"row {row} is not a permutation of 1..{side}")
    for col in range(side):
        if {solved[row][col] for row in range(side)} != expected:
            problems.append(f"col {col} is not a permutation of 1..{side}")

    # Boxes all-different.
    box = 0
    while box * box < side:
        box += 1
    for box_row in range(0, side, box):
        for box_col in range(0, side, box):
            values = {solved[box_row + i][box_col + j] for i in range(box) for j in range(box)}
            if values != expected:
                problems.append(f"box at ({box_row},{box_col}) is not a permutation")

    return problems


def verify_sudoku(board: Grid, solved: Grid) -> bool:
    """True iff ``solved`` is a valid completion of ``board``."""
    return not sudoku_violations(board, solved)


def roster_violations(problem: RosterProblem, assignment: Assignment) -> list[str]:
    """Return every rostering rule violated by an assignment (empty means valid)."""
    problems: list[str] = []
    num_nurses = problem.num_nurses
    num_days = problem.num_days
    num_shifts = problem.num_shifts

    def worked(nurse: int, day: int, shift: int) -> int:
        return assignment.get((nurse, day, shift), 0)

    # Coverage.
    for day in range(num_days):
        for shift in range(num_shifts):
            total = sum(worked(nurse, day, shift) for nurse in range(num_nurses))
            if total < problem.demand[shift]:
                problems.append(
                    f"day {day} shift {shift}: {total} nurses < demand {problem.demand[shift]}"
                )

    # At most one shift per nurse per day.
    for nurse in range(num_nurses):
        for day in range(num_days):
            if sum(worked(nurse, day, shift) for shift in range(num_shifts)) > 1:
                problems.append(f"nurse {nurse} works >1 shift on day {day}")

    # Days off.
    max_worked = num_days - problem.min_days_off
    for nurse in range(num_nurses):
        total = sum(
            worked(nurse, day, shift) for day in range(num_days) for shift in range(num_shifts)
        )
        if total > max_worked:
            problems.append(f"nurse {nurse} works {total} days, exceeding {max_worked}")

    # Rest: no night then next morning.
    if problem.no_back_to_back and num_shifts >= 1:
        night = num_shifts - 1
        morning = 0
        for nurse in range(num_nurses):
            for day in range(num_days - 1):
                if worked(nurse, day, night) and worked(nurse, day + 1, morning):
                    problems.append(f"nurse {nurse} works night {day} then morning {day + 1}")

    # Seniority on nights.
    if problem.night_requires_senior and problem.senior_nurses:
        night = num_shifts - 1
        senior = set(problem.senior_nurses)
        for nurse in range(num_nurses):
            if nurse not in senior:
                for day in range(num_days):
                    if worked(nurse, day, night):
                        problems.append(f"non-senior nurse {nurse} works night {day}")

    return problems


def verify_roster(problem: RosterProblem, assignment: Assignment) -> bool:
    """True iff every rostering rule holds in the assignment."""
    return not roster_violations(problem, assignment)


def job_shop_violations(
    problem: JobShopProblem, starts: dict[tuple[int, int], int], makespan: int
) -> list[str]:
    """Return scheduling violations: precedence, machine overlap, or wrong makespan."""
    problems: list[str] = []
    ends: dict[tuple[int, int], int] = {}
    machine_ops: dict[int, list[tuple[int, int, int]]] = {}

    for job_id, job in enumerate(problem.jobs):
        prev_end = 0
        for op_id, (machine, duration) in enumerate(job):
            start = starts[job_id, op_id]
            end = start + duration
            ends[job_id, op_id] = end
            if start < prev_end:
                problems.append(f"job {job_id} op {op_id} starts before previous op ends")
            prev_end = end
            machine_ops.setdefault(machine, []).append((start, end, job_id))

    # No two operations overlap on a machine.
    for machine, ops in machine_ops.items():
        ordered = sorted(ops)
        for (s1, e1, j1), (s2, _e2, j2) in zip(ordered, ordered[1:], strict=False):
            if s2 < e1:
                problems.append(
                    f"machine {machine}: job {j1} [{s1},{e1}] overlaps job {j2} start {s2}"
                )

    expected = max(ends.values()) if ends else 0
    if makespan != expected:
        problems.append(f"makespan {makespan} != actual completion {expected}")

    return problems


def verify_job_shop(
    problem: JobShopProblem, starts: dict[tuple[int, int], int], makespan: int
) -> bool:
    """True iff the schedule respects precedence, no-overlap, and the makespan."""
    return not job_shop_violations(problem, starts, makespan)


def timetabling_violations(problem: ExamTimetabling, placement: Placement) -> list[str]:
    """Return timetabling violations: unplaced exams, capacity, clashes, conflicts."""
    problems: list[str] = []

    if set(placement) != set(range(problem.num_exams)):
        problems.append("not every exam is placed exactly once")

    for exam, (room, _slot) in placement.items():
        if problem.exam_sizes[exam] > problem.room_caps[room]:
            problems.append(f"exam {exam} exceeds capacity of room {room}")

    seen: dict[tuple[int, int], int] = {}
    for exam, slot_room in placement.items():
        if slot_room in seen:
            problems.append(f"exams {seen[slot_room]} and {exam} share room/slot {slot_room}")
        seen[slot_room] = exam

    for first, second in problem.conflicts:
        if (
            first in placement
            and second in placement
            and placement[first][1] == placement[second][1]
        ):
            problems.append(f"conflicting exams {first} and {second} share a slot")

    return problems


def verify_timetabling(problem: ExamTimetabling, placement: Placement) -> bool:
    """True iff every exam is placed within capacity and conflict rules."""
    return not timetabling_violations(problem, placement)


def bin_packing_violations(problem: BinPacking, assignment: BinAssignment) -> list[str]:
    """Return bin-packing violations: unassigned items or over-capacity bins."""
    problems: list[str] = []

    if set(assignment) != set(range(len(problem.item_sizes))):
        problems.append("not every item is assigned to exactly one bin")

    loads: dict[int, int] = {}
    for item, b in assignment.items():
        loads[b] = loads.get(b, 0) + problem.item_sizes[item]
    for b, load in loads.items():
        if load > problem.bin_capacity:
            problems.append(f"bin {b} load {load} exceeds capacity {problem.bin_capacity}")

    return problems


def verify_bin_packing(problem: BinPacking, assignment: BinAssignment) -> bool:
    """True iff every item is packed and no bin exceeds capacity."""
    return not bin_packing_violations(problem, assignment)
