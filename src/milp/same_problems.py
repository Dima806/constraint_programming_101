"""The same problems in MILP (PuLP + open-source CBC), for the CP-vs-MILP comparison.

These intentionally mirror the CP-SAT models in ``src.models`` so the reader can set
the two encodings side by side and compare modelling effort and solve behaviour.
"""

import time
from dataclasses import dataclass

import pulp

from src.models.assignment import ExamTimetabling, Placement
from src.models.bin_packing import BinAssignment, BinPacking


@dataclass(frozen=True)
class MilpResult:
    status: str
    objective: float | None
    wall_time: float


@dataclass(frozen=True)
class MilpBinPackingResult(MilpResult):
    assignment: BinAssignment | None
    num_bins_used: int | None


@dataclass(frozen=True)
class MilpTimetableResult(MilpResult):
    placement: Placement | None


def solve_bin_packing_milp(
    problem: BinPacking, *, time_limit: float = 10.0
) -> MilpBinPackingResult:
    """Minimise the number of bins used, formulated as a MILP and solved with CBC."""
    start_time = time.perf_counter()
    num_items = len(problem.item_sizes)
    max_bins = problem.max_bins

    prob = pulp.LpProblem("bin_packing", pulp.LpMinimize)
    in_bin = {
        (item, b): pulp.LpVariable(f"x_{item}_{b}", cat="Binary")
        for item in range(num_items)
        for b in range(max_bins)
    }
    used = {b: pulp.LpVariable(f"used_{b}", cat="Binary") for b in range(max_bins)}

    prob += pulp.lpSum(used.values())
    for item in range(num_items):
        prob += pulp.lpSum(in_bin[item, b] for b in range(max_bins)) == 1
    for b in range(max_bins):
        prob += (
            pulp.lpSum(problem.item_sizes[item] * in_bin[item, b] for item in range(num_items))
            <= problem.bin_capacity * used[b]
        )
    for b in range(max_bins - 1):
        prob += used[b] >= used[b + 1]

    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit))
    elapsed = time.perf_counter() - start_time
    status = pulp.LpStatus[prob.status]

    if status != "Optimal":
        return MilpBinPackingResult(
            status=status,
            objective=None,
            wall_time=elapsed,
            assignment=None,
            num_bins_used=None,
        )

    assignment: BinAssignment = {}
    for item in range(num_items):
        for b in range(max_bins):
            if round(pulp.value(in_bin[item, b])) == 1:
                assignment[item] = b
                break
    num_bins_used = round(pulp.value(prob.objective))
    return MilpBinPackingResult(
        status=status,
        objective=float(num_bins_used),
        wall_time=elapsed,
        assignment=assignment,
        num_bins_used=num_bins_used,
    )


def solve_timetabling_milp(
    problem: ExamTimetabling, *, time_limit: float = 10.0
) -> MilpTimetableResult:
    """Feasibility timetabling as a MILP (minimise a constant), solved with CBC."""
    start_time = time.perf_counter()
    num_exams = problem.num_exams
    num_rooms = problem.num_rooms
    num_slots = problem.num_slots

    prob = pulp.LpProblem("timetabling", pulp.LpMinimize)
    placed = {
        (exam, room, slot): pulp.LpVariable(f"y_{exam}_{room}_{slot}", cat="Binary")
        for exam in range(num_exams)
        for room in range(num_rooms)
        for slot in range(num_slots)
    }

    prob += 0  # pure feasibility
    for exam, room, slot in placed:
        if problem.exam_sizes[exam] > problem.room_caps[room]:
            prob += placed[exam, room, slot] == 0
    for exam in range(num_exams):
        prob += (
            pulp.lpSum(
                placed[exam, room, slot] for room in range(num_rooms) for slot in range(num_slots)
            )
            == 1
        )
    for room in range(num_rooms):
        for slot in range(num_slots):
            prob += pulp.lpSum(placed[exam, room, slot] for exam in range(num_exams)) <= 1
    for first, second in problem.conflicts:
        for slot in range(num_slots):
            prob += (
                pulp.lpSum(placed[first, room, slot] for room in range(num_rooms))
                + pulp.lpSum(placed[second, room, slot] for room in range(num_rooms))
                <= 1
            )

    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit))
    elapsed = time.perf_counter() - start_time
    status = pulp.LpStatus[prob.status]

    if status != "Optimal":
        return MilpTimetableResult(
            status=status, objective=None, wall_time=elapsed, placement=None
        )

    placement: Placement = {}
    for (exam, room, slot), var in placed.items():
        if round(pulp.value(var)) == 1:
            placement[exam] = (room, slot)
    return MilpTimetableResult(
        status=status, objective=0.0, wall_time=elapsed, placement=placement
    )
