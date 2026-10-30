# constraint_programming_101

**Stop writing schedulers, start writing down the rules.**

A hands-on introduction to **constraint programming** — the branch of optimization built for
problems that are all rules and no arithmetic — on CPU with [OR-Tools
CP-SAT](https://developers.google.com/optimization/cp). Scheduling shifts, assigning rooms,
sequencing a factory, and solving a Sudoku turn out to be the *same* kind of problem: a set of
decisions and a set of rules, handed to a solver that searches so you don't have to.

Hand a CP solver "no nurse works two shifts in a row and everyone gets two days off" as literal
constraints and it returns a valid roster in seconds — for a problem that defeats every
hand-written heuristic. Tighten the rules until no roster can exist and it does something no
hand-written scheduler can: it **proves** the requirements are impossible, rather than looping
forever or silently returning something broken.

## Why this exists

Constraint programming lives in operations research and rarely reaches data-science training,
so practitioners reach for fragile hand-rolled heuristics or force everything into a general
MILP. This project closes three gaps:

- **Feasibility vs optimization** — often the question is "does *any* valid solution exist?",
  which CP answers with proof before it optimizes.
- **Global constraints** — `all-different`, `no-overlap` (intervals), `at-most`/`exactly-k` are
  first-class building blocks, not loops you reinvent badly.
- **CP vs MILP** — when to reach for which, shown by modeling the *same* problems both ways.

## What's inside

- **Six notebooks** that build the ideas up one at a time (see below).
- A typed **`src/` library**: CP-SAT model builders, five worked problems, a MILP comparison,
  known-solvability instances, and an independent correctness verifier.
- A lightweight **Streamlit app** with four interactive demos.
- **Tests** that assert every returned solution satisfies every rule, and that over-constrained
  instances are *proven* infeasible.

Everything runs inside a **2-CPU / 8 GB GitHub Codespace** with no GPU and only open-source
solvers (CP-SAT and CBC).

## The notebooks

| # | Notebook | What it shows |
|---|---|---|
| 01 | [Rules, not code](notebooks/01_rules_not_code.ipynb) | A greedy scheduler gets stuck; the declared-rules version finds a valid assignment instantly. |
| 02 | [Sudoku & all-different](notebooks/02_sudoku_and_all_different.ipynb) | Constraint satisfaction at its cleanest; solve, prove uniqueness, prove infeasibility. |
| 03 | [The nurse roster](notebooks/03_the_nurse_roster.ipynb) | **The showpiece.** Coverage/rest/days-off/seniority as constraints; add a rule in one line; optimize preferences. |
| 04 | [Job-shop scheduling](notebooks/04_job_shop_scheduling.ipynb) | Interval variables + `no-overlap`, minimize makespan, Gantt chart, verified against the known optimum. |
| 05 | [Feasibility & infeasibility](notebooks/05_feasibility_and_infeasibility.ipynb) | Tighten a roster until CP-SAT *proves* it impossible; what to relax next. |
| 06 | [CP vs MILP](notebooks/06_cp_vs_milp.ipynb) | The same problems in CP-SAT and MILP (PuLP + CBC); how to choose. |

Each notebook saves every figure to [`outputs/figures/`](outputs/figures/) as a PNG and every
textual/numerical input to [`outputs/data/`](outputs/data/) as JSON, so every result is
reproducible and inspectable outside a running kernel.

## Quickstart

```bash
make setup      # install uv, sync deps, register the Jupyter kernel
make test       # run the test suite
make notebooks  # execute all six notebooks headless
make run        # launch the Streamlit app
make lab        # open JupyterLab
make ci         # sync + lint + test (what CI runs)
```

Requires [`uv`](https://docs.astral.sh/uv/); `make setup` installs it if missing. The Python
version is pinned to 3.12 (`.python-version`) and `uv` fetches it automatically.

## Repository layout

```
notebooks/        the six-notebook teaching arc
src/
  cp/             thin helpers over CP-SAT (builder) + status/stats decoding (explain)
  models/         sudoku, nurse_roster, job_shop, assignment (timetabling), bin_packing
  milp/           the same problems in PuLP, for the CP-vs-MILP comparison
  datasets/       named instances with KNOWN solvability (feasible / tight / infeasible)
  evaluation/     correctness verifier, cp-vs-milp harness, scaling study
  visualisation.py, persistence.py
app/              Streamlit app
tests/            correctness + infeasibility assertions
outputs/          figures/ (PNG) and data/ (JSON) produced by the notebooks
config/           solver time limits, seeds, problem sizes
```

## How it holds together

- **Declare the rules, don't code the search.** Variables + constraints go to CP-SAT, which
  finds a valid assignment — or proves none exists.
- **Verify, don't trust.** Every solver result is re-checked against the rules from scratch in
  [`src/evaluation/correctness.py`](src/evaluation/correctness.py); a mis-modeled rule fails a
  test. Known answers are baked in — Sudoku has a unique solution, the job-shop optimum is 11,
  the bin-packing optimum is 3 — and the tests assert them.
- **Every solve is time-limited**, so notebooks and tests are bounded.

## Related projects

Part of a family of CPU-only, open-source portfolio projects by
[Dima806](https://github.com/Dima806):

- [**optimization_101**](https://github.com/Dima806/optimization_101) — mathematical
  optimization (LP/MILP) with open solvers; the MILP side of the CP-vs-MILP decision.
- [**supply_chain_arena**](https://github.com/Dima806/supply_chain_arena) — the optimization
  models that run the physical economy; production scheduling as a plant-floor cousin of CP.

Together they map the optimization landscape: `optimization_101` covers LP/MILP,
`supply_chain_arena` covers operations, and this project covers CP-SAT for logic and scheduling.

## License

[Apache-2.0](LICENSE).
