"""Exam timetabling: the everyday assignment-under-constraints problem.

Assign each exam to a (room, time-slot) so that rooms are big enough, no room holds
two exams at once, and exams that share students never land in the same slot. The
same modelling pattern as rostering, on a different surface.
"""

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from src.cp.builder import add_at_most_one, add_exactly_one, new_model, solve
from src.cp.explain import SolveStats

# exam -> (room, slot)
Placement = dict[int, tuple[int, int]]


@dataclass(frozen=True)
class ExamTimetabling:
    num_exams: int
    exam_sizes: tuple[int, ...]
    room_caps: tuple[int, ...]
    num_slots: int
    # Pairs of exams that share students and so cannot share a time slot.
    conflicts: tuple[tuple[int, int], ...] = field(default_factory=tuple)

    @property
    def num_rooms(self) -> int:
        return len(self.room_caps)


@dataclass(frozen=True)
class TimetableResult:
    placement: Placement | None
    stats: SolveStats

    @property
    def is_feasible(self) -> bool:
        return self.stats.is_feasible


def build_model(
    problem: ExamTimetabling,
) -> tuple[cp_model.CpModel, dict[tuple[int, int, int], cp_model.IntVar]]:
    """Build the timetabling model; returns model and the y[exam, room, slot] vars."""
    model = new_model()
    num_exams = problem.num_exams
    num_rooms = problem.num_rooms
    num_slots = problem.num_slots

    placed = {
        (exam, room, slot): model.new_bool_var(f"y_{exam}_{room}_{slot}")
        for exam in range(num_exams)
        for room in range(num_rooms)
        for slot in range(num_slots)
    }

    # Capacity: forbid placing an exam in a room too small for it.
    for exam, room, slot in placed:
        if problem.exam_sizes[exam] > problem.room_caps[room]:
            model.add(placed[exam, room, slot] == 0)

    # Each exam is placed exactly once.
    for exam in range(num_exams):
        add_exactly_one(
            model,
            [placed[exam, room, slot] for room in range(num_rooms) for slot in range(num_slots)],
        )

    # A room holds at most one exam per slot.
    for room in range(num_rooms):
        for slot in range(num_slots):
            add_at_most_one(model, [placed[exam, room, slot] for exam in range(num_exams)])

    # Conflicting exams never share a slot.
    for first, second in problem.conflicts:
        for slot in range(num_slots):
            same_slot = [placed[first, room, slot] for room in range(num_rooms)]
            same_slot += [placed[second, room, slot] for room in range(num_rooms)]
            add_at_most_one(model, same_slot)

    return model, placed


def solve_timetabling(
    problem: ExamTimetabling,
    *,
    time_limit: float = 10.0,
    workers: int = 2,
    seed: int = 42,
) -> TimetableResult:
    """Place every exam respecting capacity and conflicts, or report infeasible."""
    model, placed = build_model(problem)
    solver, stats = solve(model, time_limit=time_limit, workers=workers, seed=seed)
    placement: Placement | None = None
    if stats.is_feasible:
        placement = {}
        for (exam, room, slot), var in placed.items():
            if solver.value(var) == 1:
                placement[exam] = (room, slot)
    return TimetableResult(placement=placement, stats=stats)
