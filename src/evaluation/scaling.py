"""Solve time versus problem size.

Not a benchmark of scale -- the point is the modelling paradigm -- but a small,
bounded study showing how CP-SAT solve time grows as a job-shop instance gets
bigger, with every solve capped by an explicit time limit.
"""

import random
from collections.abc import Sequence
from dataclasses import dataclass

from src.models.job_shop import JobShopProblem, solve_job_shop


@dataclass(frozen=True)
class ScalingPoint:
    size: int
    status: str
    wall_time: float
    makespan: int | None


def random_job_shop(
    num_jobs: int,
    num_machines: int,
    *,
    seed: int = 42,
    max_duration: int = 9,
) -> JobShopProblem:
    """Build a deterministic random job-shop instance of a given size."""
    rng = random.Random(seed)
    jobs: list[tuple[tuple[int, int], ...]] = []
    for _ in range(num_jobs):
        machines = list(range(num_machines))
        rng.shuffle(machines)
        jobs.append(tuple((machine, rng.randint(1, max_duration)) for machine in machines))
    return JobShopProblem(jobs=tuple(jobs), num_machines=num_machines)


def job_shop_scaling(
    sizes: Sequence[int],
    *,
    num_machines: int = 3,
    time_limit: float = 5.0,
    seed: int = 42,
) -> list[ScalingPoint]:
    """Solve a random job-shop at each size and record status, time, and makespan."""
    points: list[ScalingPoint] = []
    for num_jobs in sizes:
        problem = random_job_shop(num_jobs, num_machines, seed=seed)
        result = solve_job_shop(problem, time_limit=time_limit, seed=seed)
        points.append(
            ScalingPoint(
                size=num_jobs,
                status=result.stats.status_name,
                wall_time=result.stats.wall_time,
                makespan=result.makespan,
            )
        )
    return points
