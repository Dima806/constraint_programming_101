"""Turn a raw CP-SAT solve into a human-readable status and solve statistics.

The whole project rests on trusting the solver's verdict, so we always decode the
status explicitly (OPTIMAL / FEASIBLE / INFEASIBLE / ...) rather than assuming a
solution exists.
"""

from dataclasses import dataclass

from ortools.sat.python import cp_model

Status = cp_model.CpSolverStatus

_STATUS_NAMES: dict[Status, str] = {
    cp_model.OPTIMAL: "OPTIMAL",
    cp_model.FEASIBLE: "FEASIBLE",
    cp_model.INFEASIBLE: "INFEASIBLE",
    cp_model.MODEL_INVALID: "MODEL_INVALID",
    cp_model.UNKNOWN: "UNKNOWN",
}


def status_name(status: Status) -> str:
    """Return a stable human-readable name for a CP-SAT status code."""
    return _STATUS_NAMES.get(status, f"STATUS_{int(status)}")


@dataclass(frozen=True)
class SolveStats:
    """A snapshot of a single CP-SAT solve, independent of the model's variables."""

    status: Status
    objective: float | None
    best_bound: float | None
    wall_time: float
    num_branches: int
    num_conflicts: int

    @property
    def status_name(self) -> str:
        return status_name(self.status)

    @property
    def is_feasible(self) -> bool:
        """True when the solver returned a usable assignment (optimal or feasible)."""
        return self.status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    @property
    def is_optimal(self) -> bool:
        return self.status == cp_model.OPTIMAL

    @property
    def is_infeasible(self) -> bool:
        """True when the solver *proved* no assignment can satisfy the constraints."""
        return self.status == cp_model.INFEASIBLE

    def summary(self) -> str:
        parts = [f"status={self.status_name}", f"time={self.wall_time:.3f}s"]
        if self.objective is not None:
            parts.append(f"objective={self.objective:g}")
        if self.best_bound is not None:
            parts.append(f"bound={self.best_bound:g}")
        parts.append(f"branches={self.num_branches}")
        return " ".join(parts)


def collect_stats(solver: cp_model.CpSolver, status: Status, *, has_objective: bool) -> SolveStats:
    """Read solve statistics off a solver that has just run.

    Objective/bound are only reported for a feasible solve of a model that actually
    had an objective, so a pure feasibility problem reports ``None`` there.
    """
    feasible = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    objective = solver.objective_value if has_objective and feasible else None
    best_bound = solver.best_objective_bound if has_objective and feasible else None
    return SolveStats(
        status=status,
        objective=objective,
        best_bound=best_bound,
        wall_time=solver.wall_time,
        num_branches=solver.num_branches,
        num_conflicts=solver.num_conflicts,
    )
