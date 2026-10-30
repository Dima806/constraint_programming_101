"""Bin packing: pack items into the fewest bins under a capacity limit.

A feasibility-and-optimisation problem with a clean CP formulation, and one half of
a CP-vs-MILP head-to-head.
"""

from dataclasses import dataclass

from ortools.sat.python import cp_model

from src.cp.builder import add_exactly_one, new_model, solve
from src.cp.explain import SolveStats

# item -> bin index
BinAssignment = dict[int, int]


@dataclass(frozen=True)
class BinPacking:
    item_sizes: tuple[int, ...]
    bin_capacity: int
    # Upper bound on the number of bins; defaults to one bin per item.
    num_bins: int | None = None

    @property
    def max_bins(self) -> int:
        return self.num_bins if self.num_bins is not None else len(self.item_sizes)


@dataclass(frozen=True)
class BinPackingResult:
    assignment: BinAssignment | None
    num_bins_used: int | None
    stats: SolveStats

    @property
    def is_feasible(self) -> bool:
        return self.stats.is_feasible


def build_model(
    problem: BinPacking,
) -> tuple[
    cp_model.CpModel,
    dict[tuple[int, int], cp_model.IntVar],
    list[cp_model.IntVar],
]:
    """Build the bin-packing model; returns model, x[item, bin] vars, and used[bin] vars."""
    model = new_model()
    num_items = len(problem.item_sizes)
    max_bins = problem.max_bins

    in_bin = {
        (item, b): model.new_bool_var(f"x_{item}_{b}")
        for item in range(num_items)
        for b in range(max_bins)
    }
    used = [model.new_bool_var(f"used_{b}") for b in range(max_bins)]

    # Each item goes in exactly one bin.
    for item in range(num_items):
        add_exactly_one(model, [in_bin[item, b] for b in range(max_bins)])

    # Capacity: a bin's load fits only if the bin is marked used.
    for b in range(max_bins):
        load = sum(problem.item_sizes[item] * in_bin[item, b] for item in range(num_items))
        model.add(load <= problem.bin_capacity * used[b])

    # Symmetry breaking: fill lower-numbered bins first.
    for b in range(max_bins - 1):
        model.add(used[b] >= used[b + 1])

    model.minimize(sum(used))
    return model, in_bin, used


def solve_bin_packing(
    problem: BinPacking,
    *,
    time_limit: float = 10.0,
    workers: int = 2,
    seed: int = 42,
) -> BinPackingResult:
    """Pack items into the fewest bins, or report infeasible."""
    model, in_bin, used = build_model(problem)
    solver, stats = solve(
        model, time_limit=time_limit, workers=workers, seed=seed, has_objective=True
    )
    if not stats.is_feasible:
        return BinPackingResult(assignment=None, num_bins_used=None, stats=stats)
    assignment: BinAssignment = {}
    num_items = len(problem.item_sizes)
    for item in range(num_items):
        for b in range(problem.max_bins):
            if solver.value(in_bin[item, b]) == 1:
                assignment[item] = b
                break
    num_bins_used = sum(int(solver.value(flag)) for flag in used)
    return BinPackingResult(assignment=assignment, num_bins_used=num_bins_used, stats=stats)
