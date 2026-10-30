"""Job-shop scheduling, where interval reasoning shines.

Each job is a chain of operations that must run in order; each operation needs a
machine for a fixed duration; a machine runs one operation at a time. Modelled with
interval variables and the no-overlap global constraint, minimising the makespan.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from ortools.sat.python import cp_model

from src.cp.builder import add_no_overlap, new_model, solve
from src.cp.explain import SolveStats

# An operation is (machine, duration); a job is a sequence of operations.
Operation = tuple[int, int]
Job = Sequence[Operation]


@dataclass(frozen=True)
class JobShopProblem:
    jobs: tuple[Job, ...]
    num_machines: int


@dataclass(frozen=True)
class JobShopResult:
    # (job, operation) -> start time
    starts: dict[tuple[int, int], int] | None
    makespan: int | None
    stats: SolveStats

    @property
    def is_feasible(self) -> bool:
        return self.stats.is_feasible


def build_model(
    problem: JobShopProblem,
) -> tuple[cp_model.CpModel, dict[tuple[int, int], cp_model.IntVar], cp_model.IntVar]:
    """Build the job-shop model; returns model, start variables, and makespan var."""
    model = new_model()
    horizon = sum(duration for job in problem.jobs for _machine, duration in job)

    starts: dict[tuple[int, int], cp_model.IntVar] = {}
    ends: dict[tuple[int, int], cp_model.IntVar] = {}
    machine_intervals: dict[int, list[cp_model.IntervalVar]] = {}

    for job_id, job in enumerate(problem.jobs):
        for op_id, (machine, duration) in enumerate(job):
            start = model.new_int_var(0, horizon, f"start_{job_id}_{op_id}")
            end = model.new_int_var(0, horizon, f"end_{job_id}_{op_id}")
            interval = model.new_interval_var(start, duration, end, f"iv_{job_id}_{op_id}")
            starts[job_id, op_id] = start
            ends[job_id, op_id] = end
            machine_intervals.setdefault(machine, []).append(interval)
            # Precedence within a job: an operation starts after the previous one ends.
            if op_id > 0:
                model.add(start >= ends[job_id, op_id - 1])

    # No machine runs two operations at once.
    for intervals in machine_intervals.values():
        add_no_overlap(model, intervals)

    makespan = model.new_int_var(0, horizon, "makespan")
    last_ends = [ends[job_id, len(job) - 1] for job_id, job in enumerate(problem.jobs)]
    model.add_max_equality(makespan, last_ends)
    model.minimize(makespan)

    return model, starts, makespan


def solve_job_shop(
    problem: JobShopProblem,
    *,
    time_limit: float = 10.0,
    workers: int = 2,
    seed: int = 42,
) -> JobShopResult:
    """Produce a collision-free schedule minimising makespan, or report infeasible."""
    model, starts, makespan = build_model(problem)
    solver, stats = solve(
        model, time_limit=time_limit, workers=workers, seed=seed, has_objective=True
    )
    if not stats.is_feasible:
        return JobShopResult(starts=None, makespan=None, stats=stats)
    start_values = {key: int(solver.value(var)) for key, var in starts.items()}
    return JobShopResult(starts=start_values, makespan=int(solver.value(makespan)), stats=stats)
