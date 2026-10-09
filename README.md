# n-Queens — SAT Encoding and Exact Solvers

Empirical study of the **N-Queens** problem solved via **SAT encoding** (PySAT,
multiple AMO/ALO encodings and SAT solvers) and compared against other exact
approaches: **MIP/ILP** and **CP** (CPLEX, Gurobi, OR-Tools CP-SAT, CBC/SCIP).

> Coursework: *Các vấn đề hiện đại KHMT* — Assignment 1
> (SAT Encoding for Logic puzzles, N-Queens).

## Features

- **CNF model** of N-Queens: rows use exactly-one (ALO + AMO); columns and
  diagonals use AMO. Two diagonal encodings: `naive` (pairwise) and `optimal`
  (AMO per diagonal).
- **AMO encodings implemented from scratch**: `pairwise`, `binary`, `commander`,
  `product`, `sequential`.
- **AMO encodings via PySAT** (`pysat.card`): `pysat_pairwise`,
  `pysat_sequential`, `pysat_bitwise`, `pysat_ladder`, `pysat_sorting`,
  `pysat_cardinality`, `pysat_totalizer`.
- **SAT solvers** through PySAT: CaDiCaL, Glucose, Kissat, CryptoMiniSat,
  MergeSAT, MiniCard, MiniSat, Lingeling.
- **Exact baselines**: OR-Tools **CP-SAT**, OR-Tools **MIP** (SCIP/CBC),
  **PuLP** (CBC), **Gurobi** (MIP), **CPLEX** (MIP and CP).
- **Benchmark harness** writing raw CSV, plus plotting utilities.
- **Correctness tests**: known solution counts for n = 1..12 and board validity.

## Layout

```
n-Queens/
  src/nqueens/            # package
    encodings/manual.py   # hand-written AMO encodings
    encodings/pysat_amo.py# pysat.card wrappers
    model.py              # build_cnf
    sat_solver.py         # run PySAT solvers + stats
    verify.py             # board checks and solution counting
    baselines/            # OR-Tools, PuLP, Gurobi, CPLEX
    bench.py plot.py main.py
  tests/                  # pytest suite
  results/                # raw CSV + figures (generated)
  report/                 # LaTeX paper (to be added)
  pyproject.toml requirements.txt
```

## Installation

Python 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

The last step installs the `nqueens` package (src-layout) in editable mode and
registers the `nqueens` command; without it `python -m nqueens` fails with
`No module named nqueens`. Alternatively, set `PYTHONPATH=src`.

PySAT, OR-Tools, PuLP, CBC and SCIP work out of the box. Gurobi and CPLEX need a
free academic license to lift their size limits (see below).

## Usage

Run as a module (`python -m nqueens ...`) or via the installed `nqueens` script.

```powershell
# Solve a single instance and print the board
python -m nqueens solve 8 --encoding commander --solver cadical153

# Enumerate all solutions (small n) and compare to the known count
python -m nqueens count 6 --encoding sequential

# Benchmark SAT encodings/solvers -> results/sat.csv
python -m nqueens bench --what sat --ns 8:40:2 `
    --encodings pairwise binary commander product sequential `
    --solvers glucose3 cadical153 kissat404

# Benchmark exact baselines -> results/baselines.csv
python -m nqueens bench --what baselines --ns 8:40:2 `
    --methods cpsat mip_scip mip_cbc pulp_cbc gurobi cplex_mp cplex_cp `
    --time-limit 300

# Generate figures from the CSVs
python -m nqueens plot --sat results/sat.csv --baselines results/baselines.csv `
    --outdir results/figures
```

`--ns` accepts a comma list (`8,10,12`) or a range (`8:40:2` = start:stop:step).

## Academic licenses (mandatory for large n)

For n up to ~100 the models exceed the size limits of the free default engines
(Gurobi ~2000 vars, CPLEX Community ~1000 vars), so full academic licenses are
required.

**Gurobi — free Academic Named-User License (1 year):**

1. Register an academic account at <https://www.gurobi.com/academics>.
2. Install Gurobi and `pip install gurobipy`.
3. Connect to the **university network** (directly or via a full-tunnel VPN),
   open the User Portal → Licenses → *Generate Now*, then run the shown
   `grbgetkey <key>` command to create `gurobi.lic`.
4. If you cannot reach the campus network, create an **Academic WLS license**
   instead (portable, usable anywhere).

**CPLEX — IBM Academic Initiative (full version, free):**

1. Go to <https://www.ibm.com/academic> and log in with your university email.
2. Software → **ILOG CPLEX Optimization Studio** → download and install.
3. `pip install cplex docplex`, then point docplex at the full install:
   `docplex config --upgrade "<CPLEX_STUDIO_DIR>"`.

## Testing

```powershell
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
