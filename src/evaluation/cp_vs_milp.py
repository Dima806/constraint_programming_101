"""Head-to-head: solve the same problem with CP-SAT and with MILP, and compare.

The CP-vs-MILP guidance in the project rests on demonstration, not assertion: run
both solvers on shared problems and report objective and wall-clock time so the
reader can see where each is the natural fit.
"""

from dataclasses import dataclass

from src.milp.same_problems import solve_bin_packing_milp, solve_timetabling_milp
from src.models.assignment import ExamTimetabling, solve_timetabling
from src.models.bin_packing import BinPacking, solve_bin_packing


@dataclass(frozen=True)
class Comparison:
    """Side-by-side result for one problem solved both ways."""

    problem: str
    cp_status: str
    cp_objective: float | None
    cp_time: float
    milp_status: str
    milp_objective: float | None
    milp_time: float

    @property
    def objectives_agree(self) -> bool:
        """True when both solvers reach the same objective (or both found none)."""
        if self.cp_objective is None or self.milp_objective is None:
            return self.cp_objective is None and self.milp_objective is None
        return abs(self.cp_objective - self.milp_objective) < 1e-6


def compare_bin_packing(problem: BinPacking, *, time_limit: float = 10.0) -> Comparison:
    """Compare CP-SAT and MILP on a bin-packing instance."""
    cp = solve_bin_packing(problem, time_limit=time_limit)
    milp = solve_bin_packing_milp(problem, time_limit=time_limit)
    cp_objective = float(cp.num_bins_used) if cp.num_bins_used is not None else None
    return Comparison(
        problem="bin_packing",
        cp_status=cp.stats.status_name,
        cp_objective=cp_objective,
        cp_time=cp.stats.wall_time,
        milp_status=milp.status,
        milp_objective=milp.objective,
        milp_time=milp.wall_time,
    )


def compare_timetabling(problem: ExamTimetabling, *, time_limit: float = 10.0) -> Comparison:
    """Compare CP-SAT and MILP on a timetabling instance (pure feasibility)."""
    cp = solve_timetabling(problem, time_limit=time_limit)
    milp = solve_timetabling_milp(problem, time_limit=time_limit)
    cp_objective = 0.0 if cp.is_feasible else None
    return Comparison(
        problem="timetabling",
        cp_status=cp.stats.status_name,
        cp_objective=cp_objective,
        cp_time=cp.stats.wall_time,
        milp_status=milp.status,
        milp_objective=milp.objective,
        milp_time=milp.wall_time,
    )
