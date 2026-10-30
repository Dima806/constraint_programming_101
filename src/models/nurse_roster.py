"""Nurse rostering: the showpiece.

Every rule a manager would recognise becomes one constraint over yes/no assignment
variables:

* coverage      -- each shift each day needs at least ``demand`` nurses
* one-a-day     -- a nurse works at most one shift per day
* rest          -- no back-to-back (night then next morning)
* days off      -- each nurse gets at least ``min_days_off`` days off
* seniority     -- only senior nurses may cover the night shift

Adding a rule is adding a constraint, not rewriting a scheduler. An optional
preference list turns the feasibility problem into an optimisation (maximise
satisfied preferences) among valid rosters.
"""

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from src.cp.builder import add_at_most_one, new_model, solve
from src.cp.explain import SolveStats

# (nurse, day, shift) -> 0/1
Assignment = dict[tuple[int, int, int], int]


@dataclass(frozen=True)
class RosterProblem:
    """A rostering instance expressed entirely as rules."""

    num_nurses: int
    num_days: int
    shifts: tuple[str, ...] = ("morning", "evening", "night")
    demand: tuple[int, ...] = (1, 1, 1)
    min_days_off: int = 2
    senior_nurses: tuple[int, ...] = ()
    max_shifts_per_nurse: int | None = None
    no_back_to_back: bool = True
    night_requires_senior: bool = True
    # Each entry (nurse, day, shift) is a preferred assignment to reward.
    preferences: tuple[tuple[int, int, int], ...] = field(default_factory=tuple)

    @property
    def num_shifts(self) -> int:
        return len(self.shifts)


@dataclass(frozen=True)
class RosterResult:
    assignment: Assignment | None
    stats: SolveStats

    @property
    def is_feasible(self) -> bool:
        return self.stats.is_feasible


def build_model(
    problem: RosterProblem,
) -> tuple[cp_model.CpModel, dict[tuple[int, int, int], cp_model.IntVar], bool]:
    """Build the roster model; returns the model, the x variables, and has_objective."""
    model = new_model()
    num_nurses = problem.num_nurses
    num_days = problem.num_days
    num_shifts = problem.num_shifts

    works = {
        (nurse, day, shift): model.new_bool_var(f"w_{nurse}_{day}_{shift}")
        for nurse in range(num_nurses)
        for day in range(num_days)
        for shift in range(num_shifts)
    }

    # One shift a day: at most one shift per nurse per day.
    for nurse in range(num_nurses):
        for day in range(num_days):
            add_at_most_one(model, [works[nurse, day, shift] for shift in range(num_shifts)])

    # Coverage: at least demand[shift] nurses on every shift, every day.
    for day in range(num_days):
        for shift in range(num_shifts):
            model.add(
                sum(works[nurse, day, shift] for nurse in range(num_nurses))
                >= problem.demand[shift]
            )

    # Days off: a nurse works at most (num_days - min_days_off) days.
    max_worked = num_days - problem.min_days_off
    for nurse in range(num_nurses):
        worked = sum(
            works[nurse, day, shift] for day in range(num_days) for shift in range(num_shifts)
        )
        model.add(worked <= max_worked)
        if problem.max_shifts_per_nurse is not None:
            model.add(worked <= problem.max_shifts_per_nurse)

    # Rest: no night shift immediately followed by next-morning shift.
    if problem.no_back_to_back and num_shifts >= 1:
        night = num_shifts - 1
        morning = 0
        for nurse in range(num_nurses):
            for day in range(num_days - 1):
                model.add(works[nurse, day, night] + works[nurse, day + 1, morning] <= 1)

    # Seniority: only senior nurses may work the night shift.
    if problem.night_requires_senior and problem.senior_nurses:
        night = num_shifts - 1
        senior = set(problem.senior_nurses)
        for nurse in range(num_nurses):
            if nurse not in senior:
                for day in range(num_days):
                    model.add(works[nurse, day, night] == 0)

    # Optional objective: maximise satisfied shift preferences among valid rosters.
    has_objective = bool(problem.preferences)
    if has_objective:
        model.maximize(sum(works[key] for key in problem.preferences))

    return model, works, has_objective


def solve_roster(
    problem: RosterProblem,
    *,
    time_limit: float = 10.0,
    workers: int = 2,
    seed: int = 42,
) -> RosterResult:
    """Return a valid roster (optimising preferences if given) or an infeasible verdict."""
    model, works, has_objective = build_model(problem)
    solver, stats = solve(
        model,
        time_limit=time_limit,
        workers=workers,
        seed=seed,
        has_objective=has_objective,
    )
    assignment: Assignment | None = None
    if stats.is_feasible:
        assignment = {key: int(solver.value(var)) for key, var in works.items()}
    return RosterResult(assignment=assignment, stats=stats)
