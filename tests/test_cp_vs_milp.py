"""CP vs MILP: the two encodings agree on the shared problems."""

from src.datasets import instances
from src.evaluation.cp_vs_milp import compare_bin_packing, compare_timetabling


def test_cp_and_milp_agree_on_bin_packing() -> None:
    comparison = compare_bin_packing(instances.small_bin_packing(), time_limit=10.0)
    assert comparison.cp_objective == instances.SMALL_BIN_PACKING_OPTIMUM
    assert comparison.milp_objective == instances.SMALL_BIN_PACKING_OPTIMUM
    assert comparison.objectives_agree


def test_cp_and_milp_agree_on_timetabling() -> None:
    comparison = compare_timetabling(instances.small_timetabling(), time_limit=10.0)
    assert comparison.cp_status in ("OPTIMAL", "FEASIBLE")
    assert comparison.milp_status == "Optimal"
    assert comparison.objectives_agree
