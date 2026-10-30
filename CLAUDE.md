# Project: constraint_programming_101

An educational "101" portfolio project that teaches **constraint programming** (CP) to a
data-science audience using **OR-Tools CP-SAT**. Companion to
[`optimization_101`](https://github.com/Dima806/optimization_101) (LP/MILP) and
[`supply_chain_arena`](https://github.com/Dima806/supply_chain_arena) (operations optimization);
this is the feasibility-first, logic-heavy member of the optimization track.

## Thesis (keep every deliverable pointed at this)
Scheduling, rostering, sequencing, timetabling, and puzzles are **the same problem**: a set
of decisions plus a set of rules, handed to a solver that searches so you don't have to.

- **Declare the rules, don't code the search.** Variables + constraints → the solver finds a
  valid assignment. This replaces hand-written schedulers (nested loops, greedy assignment,
  patches on patches).
- **Feasibility ≠ optimization.** Often the real question is "does *any* valid solution
  exist?" CP answers it with **proof**, and only then optimizes among feasible solutions.
- **CP-SAT can PROVE infeasibility** on over-constrained instances — the capability no
  hand-written heuristic has. "The solver says it's impossible" is a valuable, actionable
  answer.
- **Adding a rule = adding a line, not a rewrite.** Demonstrate this explicitly in the
  nurse-roster material.

## Stack & environment
- `requires-python = ">=3.11"`, but **pinned to 3.12** via `.python-version` (see pins below).
  Package manager **`uv`** — no `pip`, no `conda`.
- Solvers: **`ortools`** (CP-SAT) is the primary solver; **`pulp`** (open-source CBC) is used
  only for the CP-vs-MILP comparison. **No commercial solver**, **no GPU**.
- Data/plotting: `numpy`, `pandas`, `matplotlib`, `plotly`. App: `streamlit`. Config:
  `pydantic`, `pydantic-settings`, `pyyaml`.
- Hard constraint: must run inside a **2-CPU / 8 GB GitHub Codespace**. Models are at most a
  few thousand bool/int variables — trivial for RAM; the risk is solve time, not memory.

## Environment pins & gotchas (hard-won — don't "fix" without checking)
- **Python 3.12** (`.python-version`): OR-Tools has no 3.14 wheels yet; the Codespace's system
  Python is newer, so the pin keeps `uv sync` resolvable.
- **`pulp>=2.9,<3`**: unpinned `>=2.9` resolves to PuLP 4.x, a rewritten API that drops
  `PULP_CBC_CMD` / `LpStatus` and ships stubs that fight `ty`. The `<3` pin keeps the classic
  2.9 API the models use.
- **OR-Tools uses the snake_case API** (`new_bool_var`, `new_int_var`, `add_all_different`,
  `new_interval_var`, `add_no_overlap`, `add`, `maximize`, `solve`, `value`). The PascalCase
  methods are gone from the stubs, so PascalCase fails `ty`. Status type is
  `cp_model.CpSolverStatus`, not `int`.
- **`ty` type-checks `src/` only** (not `tests/` or `app/`); `ruff` covers `src/ tests/ app/`.
- Untyped deps (`pulp`, `pandas`, `plotly`, `pyyaml`) are lenient under `ty`; `matplotlib`,
  `numpy`, `pydantic`, `ortools` are typed and checked.

## Repository map (what goes where)
```
config/settings.yaml      Problem sizes, time limits, seeds (loaded via pydantic-settings)
notebooks/01..06          The teaching arc (see "Notebook arc" below)
src/config.py             Typed settings loader
src/models/
  sudoku.py               all-different over rows/cols/boxes; solve + prove uniqueness
  nurse_roster.py         bool assignment vars; coverage / rest / days-off / seniority; + optimize
  job_shop.py             interval vars + no-overlap; minimize makespan
  assignment.py           exams → rooms/time-slots with capacity + conflict rules
  bin_packing.py          pack items into fewest bins (CP formulation)
src/cp/
  builder.py              thin helpers over CP-SAT: bool/int vars, common global constraints
  explain.py              feasible/infeasible status, objective value, solve stats
src/milp/same_problems.py selected problems (assignment, bin packing) in PuLP for comparison
src/datasets/instances.py named instances with KNOWN solvability (feasible / tight / infeasible)
src/evaluation/
  correctness.py          verify every constraint holds in a returned solution
  cp_vs_milp.py           solve time + modeling effort on shared problems (bin packing, timetabling)
  scaling.py              solve time vs problem size (random job-shop)
src/visualisation.py      sudoku_figure, gantt_chart, roster_heatmap, sudoku_to_text
src/persistence.py        save_figure (PNG) + save_json; writes under outputs/
app/streamlit_app.py      Sudoku solver / roster builder / job-shop Gantt / constraint stress test
tests/                    6 files: sudoku, nurse_roster, job_shop, infeasibility,
                          assignment_bin_packing, cp_vs_milp (15 tests)
outputs/figures/          PNG figures saved by the notebooks (one per visual)
outputs/data/             JSON inputs/results saved by the notebooks (one per instance)
```

## Notebook arc (strict build-up — don't reorder)
All six are written and execute headless in < 5 min total. Each cell saves every figure as a
PNG (`outputs/figures/`) and every textual/numerical input as JSON (`outputs/data/`) via
`src/persistence.py`. A bootstrap cell puts the repo root on `sys.path` so they run from either
the repo root or `notebooks/`.
1. `01_rules_not_code` — the paradigm shift: a tiny problem solved by hand-coded search vs.
   by declaring rules; the hand-coded version balloons, the declared one stays short.
2. `02_sudoku_and_all_different` — constraint satisfaction at its cleanest; introduces the
   `all-different` global constraint, uniqueness proof, and infeasibility.
3. `03_the_nurse_roster` — **the showpiece.** Real rules as constraints, a valid roster in
   seconds, a new rule in one line, then optimize (maximize satisfied preferences) among
   feasible rosters.
4. `04_job_shop_scheduling` — interval variables + `no-overlap`, minimize makespan, Gantt
   chart, makespan verified against the known optimum at small size.
5. `05_feasibility_and_infeasibility` — tighten a roster until no solution exists; CP-SAT
   proves infeasibility; discuss which constraints to relax.
6. `06_cp_vs_milp` — the decision framework: model the same problems (assignment, bin
   packing) in both CP-SAT and PuLP; contrast modeling effort and solve behavior.

## Modeling conventions
- Build models through `src/cp/builder.py` helpers, not raw `CpModel` boilerplate scattered
  across files. Prefer first-class **global constraints** — `add_all_different`,
  `add_no_overlap` (over `new_interval_var`), `add_at_most_one` / `add_exactly_one` — over
  hand-rolled inequality loops. The point of the project is that these exist and are native.
- **Every solve is time-limited.** Set `solver.parameters.max_time_in_seconds` from
  `config/settings.yaml` so no notebook or test can hang. Never ship an uncapped solve.
- Decode the solver status explicitly (`OPTIMAL` / `FEASIBLE` / `INFEASIBLE` /
  `MODEL_INVALID` / `UNKNOWN`) via `src/cp/explain.py`; don't assume a solution exists.
- Keep models seeded and deterministic where the solver allows; record seeds in settings.

## Testing & verification discipline (non-negotiable)
This repo's claims are about *correctness of feasibility verdicts*, so verification is the
product, not an afterthought:
- **Verify, don't trust.** Every returned solution is checked against *all* its constraints
  in `src/evaluation/correctness.py`, and tests assert it. A mis-modeled rule must fail a test.
- Instances have **known solvability**: comfortably feasible, exactly feasible (tight), and
  over-constrained (provably infeasible). Tests assert the solver's verdict matches the known
  answer — including asserting `INFEASIBLE` on over-constrained instances (not a timeout).
- Sudoku: solve valid boards, prove uniqueness (search for a second solution and fail),
  report deliberately unsolvable boards infeasible.
- Job-shop: no machine overlaps; makespan equals the known optimum (11) at small size.
- Bin packing reaches the known optimum (3 bins); CP-SAT and MILP agree on shared problems.

## Commands (always via the Makefile / `uv run ...`)
- `make setup` — first-time: install `uv`, `uv sync --all-extras`, register the Jupyter kernel.
- `make lint` — `ruff format` + `ruff check --fix` + `ty check` (run before every commit).
- `make test` — `pytest`; `make test-cov` for coverage.
- `make notebooks` — execute all notebooks headless (300s timeout each) to prove they run.
- `make run` — launch the Streamlit app. `make lab` — JupyterLab.
- `make ci` — `sync lint test` (what CI runs). `make dev` — fast `lint test` loop.

## Code style
- `ruff` (line length **99**, `E501` ignored), rule sets `E,F,W,I,UP,N,B,A,SIM,PTH`. Prefer
  `pathlib` over `os.path` (PTH), modern syntax (UP), no builtin shadowing (A).
- Type-checked with `ty` (`make typecheck`, `src/` only). Keep public functions typed.
- Use `pathlib`, not string paths. Keep notebook cells short; push logic into `src/`.

## Success bar (from the PRD)
`make lint` and `make test` pass with zero errors; every notebook runs < 5 min on 2 CPUs;
every rule verified in returned solutions; infeasibility proven (asserted) on over-constrained
instances; all solvers open-source (CP-SAT, CBC).

## Working style
- **Caveman mode: ON.** Code-first, minimal prose. `/compact` at notebook boundaries.
- Keep every piece tied to the thesis above; if a feature doesn't illustrate "declare the
  rules, let the solver search," it probably doesn't belong in the 101.
