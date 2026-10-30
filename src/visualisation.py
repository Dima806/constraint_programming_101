"""Figures for the notebooks and the Streamlit app: Sudoku, Gantt charts, rosters."""

import math

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from src.models.job_shop import JobShopProblem
from src.models.nurse_roster import Assignment, RosterProblem
from src.models.sudoku import Grid


def sudoku_to_text(grid: Grid) -> str:
    """Render a board as text with box separators ('.' for a blank)."""
    side = len(grid)
    box = math.isqrt(side)
    lines: list[str] = []
    for row in range(side):
        if row > 0 and row % box == 0:
            lines.append("-" * (2 * side + box - 1))
        cells: list[str] = []
        for col in range(side):
            if col > 0 and col % box == 0:
                cells.append("|")
            value = grid[row][col]
            cells.append(str(value) if value != 0 else ".")
        lines.append(" ".join(cells))
    return "\n".join(lines)


def sudoku_figure(grid: Grid, *, givens: Grid | None = None, title: str = "Sudoku") -> Figure:
    """Draw a board: given digits in bold black, solver-filled digits in blue."""
    side = len(grid)
    box = math.isqrt(side)
    fig, ax = plt.subplots(figsize=(side * 0.6, side * 0.6))
    ax.set_xlim(0, side)
    ax.set_ylim(0, side)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    for line in range(side + 1):
        width = 2.0 if line % box == 0 else 0.5
        ax.axhline(line, color="black", linewidth=width)
        ax.axvline(line, color="black", linewidth=width)
    for row in range(side):
        for col in range(side):
            value = grid[row][col]
            if value == 0:
                continue
            given = givens is None or givens[row][col] != 0
            ax.text(
                col + 0.5,
                side - row - 0.5,
                str(value),
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold" if given else "normal",
                color="black" if given else "tab:blue",
            )
    ax.set_title(title)
    fig.tight_layout()
    return fig


def gantt_chart(
    problem: JobShopProblem,
    starts: dict[tuple[int, int], int],
    *,
    title: str = "Job-shop schedule",
) -> Figure:
    """Draw a machine-by-time Gantt chart, one colour per job."""
    fig, ax = plt.subplots(figsize=(9, 1 + problem.num_machines))
    cmap = plt.get_cmap("tab10")
    for job_id, job in enumerate(problem.jobs):
        colour = cmap(job_id % 10)
        for op_id, (machine, duration) in enumerate(job):
            start = starts[job_id, op_id]
            ax.barh(
                machine,
                duration,
                left=start,
                height=0.6,
                color=colour,
                edgecolor="black",
            )
            ax.text(
                start + duration / 2,
                machine,
                f"J{job_id}",
                ha="center",
                va="center",
                color="white",
                fontsize=8,
            )
    ax.set_yticks(range(problem.num_machines))
    ax.set_yticklabels([f"machine {m}" for m in range(problem.num_machines)])
    ax.set_xlabel("time")
    ax.set_title(title)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig


def roster_heatmap(
    problem: RosterProblem,
    assignment: Assignment,
    *,
    title: str = "Nurse roster",
) -> Figure:
    """Draw a nurse-by-day heatmap: 0 = off, otherwise the shift index + 1."""
    num_nurses = problem.num_nurses
    num_days = problem.num_days
    matrix = np.zeros((num_nurses, num_days), dtype=int)
    for (nurse, day, shift), value in assignment.items():
        if value == 1:
            matrix[nurse, day] = shift + 1

    fig, ax = plt.subplots(figsize=(1 + num_days, 1 + num_nurses * 0.5))
    image = ax.imshow(matrix, aspect="auto", cmap="YlGnBu")
    ax.set_xticks(range(num_days))
    ax.set_xticklabels([f"day {d}" for d in range(num_days)], rotation=45, ha="right")
    ax.set_yticks(range(num_nurses))
    ax.set_yticklabels([f"nurse {n}" for n in range(num_nurses)])
    ax.set_title(title)
    colour_bar = fig.colorbar(image, ax=ax, ticks=range(problem.num_shifts + 1))
    colour_bar.set_label("0 = off, else shift index + 1")
    fig.tight_layout()
    return fig
