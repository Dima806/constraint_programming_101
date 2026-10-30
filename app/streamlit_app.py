"""Interactive CP-SAT demos: declare the rules, watch the solver search.

Four tabs mirror the notebooks:
  1. Sudoku solver          -- fill a board or report it unsolvable, with a uniqueness check
  2. Roster builder         -- set staff, shifts, and rules; get a valid roster or an infeasible verdict
  3. Job-shop Gantt         -- a collision-free schedule with its makespan
  4. Constraint stress test -- tighten a roster until it flips from feasible to provably infeasible
"""

import streamlit as st

from src.datasets import instances
from src.models.job_shop import solve_job_shop
from src.models.nurse_roster import RosterProblem, solve_roster
from src.models.sudoku import Grid, has_unique_solution, solve_sudoku
from src.visualisation import gantt_chart, roster_heatmap

TIME_LIMIT = 10.0


def board_to_plain(grid: Grid) -> str:
    """Render a board as nine rows of digits, '.' for a blank."""
    return "\n".join("".join(str(v) if v else "." for v in row) for row in grid)


def parse_board(text: str) -> Grid | None:
    """Parse nine rows of nine characters into a board, or return None if malformed."""
    rows = [line.strip() for line in text.splitlines() if line.strip()]
    if len(rows) != 9 or any(len(row) != 9 for row in rows):
        return None
    try:
        return [[0 if char in {".", "0"} else int(char) for char in row] for row in rows]
    except ValueError:
        return None


def sudoku_tab() -> None:
    st.subheader("Sudoku solver")
    st.caption("A Sudoku is just all-different on every row, column, and box.")
    text = st.text_area(
        "Board (9 rows of 9 characters; '.' or '0' for a blank)",
        value=board_to_plain(instances.valid_sudoku()),
        height=230,
    )
    if st.button("Solve", key="sudoku_solve"):
        board = parse_board(text)
        if board is None:
            st.error("Could not parse the board — need 9 rows of 9 characters.")
            return
        result = solve_sudoku(board, time_limit=TIME_LIMIT)
        if not result.is_feasible or result.solved is None:
            st.error(f"No solution: the board is {result.stats.status_name}.")
            return
        st.success(f"Solved in {result.stats.wall_time:.3f}s.")
        st.code(board_to_plain(result.solved))
        unique = has_unique_solution(board, time_limit=TIME_LIMIT)
        st.write("Unique solution" if unique else "Multiple solutions exist")


def _roster_from_controls(key: str) -> RosterProblem:
    num_nurses = st.slider("Nurses", 3, 12, 6, key=f"{key}_nurses")
    num_days = st.slider("Days", 3, 7, 7, key=f"{key}_days")
    demand = st.slider("Nurses required per shift", 1, 4, 1, key=f"{key}_demand")
    min_days_off = st.slider("Guaranteed days off", 0, 5, 2, key=f"{key}_off")
    seniors = tuple(range(min(2, num_nurses)))
    return RosterProblem(
        num_nurses=num_nurses,
        num_days=num_days,
        demand=(demand, demand, demand),
        min_days_off=min_days_off,
        senior_nurses=seniors,
    )


def roster_tab() -> None:
    st.subheader("Roster builder")
    st.caption("Coverage, rest, days off, and seniority — each one rule, each one constraint.")
    problem = _roster_from_controls("roster")
    if st.button("Build roster", key="roster_build"):
        result = solve_roster(problem, time_limit=TIME_LIMIT)
        if not result.is_feasible or result.assignment is None:
            st.error(f"No valid roster exists: {result.stats.status_name}.")
            return
        st.success(f"Valid roster found in {result.stats.wall_time:.3f}s.")
        st.pyplot(roster_heatmap(problem, result.assignment))


def job_shop_tab() -> None:
    st.subheader("Job-shop Gantt")
    st.caption("Interval variables plus no-overlap: jobs compete for machines, minimise makespan.")
    problem = instances.small_job_shop()
    if st.button("Schedule", key="jobshop_schedule"):
        result = solve_job_shop(problem, time_limit=TIME_LIMIT)
        if not result.is_feasible or result.starts is None:
            st.error(f"No schedule: {result.stats.status_name}.")
            return
        optimal = " (optimal)" if result.stats.is_optimal else ""
        st.success(f"Makespan = {result.makespan}{optimal}, in {result.stats.wall_time:.3f}s.")
        st.pyplot(gantt_chart(problem, result.starts))


def stress_test_tab() -> None:
    st.subheader("Constraint stress test")
    st.caption("Tighten the rules and watch the problem flip to *provably* infeasible.")
    problem = _roster_from_controls("stress")
    result = solve_roster(problem, time_limit=TIME_LIMIT)
    if result.is_feasible:
        st.success(f"Feasible ({result.stats.status_name}).")
    elif result.stats.is_infeasible:
        st.error("Provably INFEASIBLE — the solver proved no valid roster can exist.")
    else:
        st.warning(f"Solver returned {result.stats.status_name} within the time limit.")


def main() -> None:
    st.set_page_config(page_title="Constraint Programming 101", layout="wide")
    st.title("Constraint Programming 101")
    st.write("Stop writing schedulers, start writing down the rules.")
    tabs = st.tabs(["Sudoku", "Roster", "Job-shop", "Stress test"])
    with tabs[0]:
        sudoku_tab()
    with tabs[1]:
        roster_tab()
    with tabs[2]:
        job_shop_tab()
    with tabs[3]:
        stress_test_tab()


if __name__ == "__main__":
    main()
