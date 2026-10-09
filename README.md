# n-Queens — SAT Encoding and Exact Solvers

Empirical study of the **N-Queens** problem solved via **SAT encoding** (PySAT with
multiple AMO/ALO encodings and SAT solvers) and compared against other exact
approaches: **MIP / ILP** and **CP** (CPLEX, Gurobi, OR-Tools CP-SAT, CBC/SCIP).

> Coursework: *Các vấn đề hiện đại KHMT* — Assignment 1 (SAT Encoding for Logic
> puzzles, N-Queens).

## Status

Repository is being built incrementally. Source code, experiments and the report
will be added next.

## Planned layout

```
n-Queens/
  src/nqueens/            # package: encodings, model, sat solver, baselines
  tests/                  # correctness tests
  results/                # raw CSV + figures
  report/                 # LaTeX paper (Elsevier cas-sc)
  requirements.txt
```

## Environment

Python 3.11. Create the virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Gurobi and CPLEX need a free academic license; OR-Tools/PuLP/CBC/SCIP and
PySAT work out of the box.

## License

MIT — see [LICENSE](LICENSE).
