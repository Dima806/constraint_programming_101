"""Thin, typed helpers over CP-SAT.

The point of the project is that scheduling-style rules are *declared*, not coded,
so these helpers deliberately stay thin: they create variables, expose the global
constraints as first-class building blocks (all-different, no-overlap, at-most/
exactly-one), and run a time-limited solve. No search logic lives here.
"""

from collections.abc import Hashable, Iterable
from typing import TypeVar

from ortools.sat.python import cp_model

from src.cp.explain import SolveStats, collect_stats

K = TypeVar("K", bound=Hashable)

# Sensible CP-SAT defaults for a 2-CPU Codespace; every solve is time-limited.
DEFAULT_TIME_LIMIT = 10.0
DEFAULT_WORKERS = 2
DEFAULT_SEED = 42


def new_model() -> cp_model.CpModel:
    """Create an empty CP-SAT model."""
    return cp_model.CpModel()


def bool_var_dict(
    model: cp_model.CpModel, keys: Iterable[K], prefix: str = "x"
) -> dict[K, cp_model.IntVar]:
    """Create one boolean (0/1) variable per key, returned as a dict keyed by key."""
    return {key: model.new_bool_var(f"{prefix}_{key}") for key in keys}


def int_var_dict(
    model: cp_model.CpModel,
    keys: Iterable[K],
    lower: int,
    upper: int,
    prefix: str = "v",
) -> dict[K, cp_model.IntVar]:
    """Create one bounded integer variable per key."""
    return {key: model.new_int_var(lower, upper, f"{prefix}_{key}") for key in keys}


def add_all_different(model: cp_model.CpModel, variables: Iterable[cp_model.LinearExprT]) -> None:
    """'These must all take different values' as a single global constraint."""
    model.add_all_different(variables)


def add_exactly_one(model: cp_model.CpModel, literals: Iterable[cp_model.LiteralT]) -> None:
    """Exactly one of the booleans is true."""
    model.add_exactly_one(literals)


def add_at_most_one(model: cp_model.CpModel, literals: Iterable[cp_model.LiteralT]) -> None:
    """At most one of the booleans is true."""
    model.add_at_most_one(literals)


def add_at_least_one(model: cp_model.CpModel, literals: Iterable[cp_model.LiteralT]) -> None:
    """At least one of the booleans is true."""
    model.add_bool_or(literals)


def add_no_overlap(model: cp_model.CpModel, intervals: Iterable[cp_model.IntervalVar]) -> None:
    """'These intervals must not overlap in time' as a single global constraint."""
    model.add_no_overlap(intervals)


def solve(
    model: cp_model.CpModel,
    *,
    time_limit: float = DEFAULT_TIME_LIMIT,
    workers: int = DEFAULT_WORKERS,
    seed: int = DEFAULT_SEED,
    has_objective: bool = False,
    log: bool = False,
) -> tuple[cp_model.CpSolver, SolveStats]:
    """Run a bounded CP-SAT solve and return the solver plus decoded statistics."""
    solver = cp_model.CpSolver()
    params = solver.parameters
    params.max_time_in_seconds = time_limit
    params.num_search_workers = workers
    params.random_seed = seed
    params.log_search_progress = log
    status = solver.solve(model)
    return solver, collect_stats(solver, status, has_objective=has_objective)
