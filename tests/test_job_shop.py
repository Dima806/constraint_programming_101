"""Job shop: no machine overlaps, and makespan matches the known optimum at small size."""

from src.datasets import instances
from src.evaluation.correctness import verify_job_shop
from src.models.job_shop import solve_job_shop


def test_schedule_is_collision_free_and_optimal() -> None:
    problem = instances.small_job_shop()
    result = solve_job_shop(problem, time_limit=10.0)
    assert result.is_feasible
    assert result.stats.is_optimal
    assert result.makespan == instances.SMALL_JOB_SHOP_OPTIMUM
    assert result.starts is not None
    # Precedence, no machine overlap, and makespan all verified independently.
    assert verify_job_shop(problem, result.starts, result.makespan)
