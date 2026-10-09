"""Benchmark harness for SAT encodings and exact baselines."""

import time
from pathlib import Path

import pandas as pd

from .baselines import BASELINES, run_baseline
from .sat_solver import SUPPORTED_SOLVERS, solve_sat

DEFAULT_ENCODINGS = [
    "pairwise", "binary", "commander", "product", "sequential",
]

SAT_COLUMNS = [
    "method", "n", "encoding", "solver", "diagonal_mode", "rep",
    "status", "build_time", "solve_time", "time", "nv", "nclauses",
    "decisions", "propagations", "conflicts", "note",
]

BASELINE_COLUMNS = [
    "method", "n", "rep", "status", "time", "nv", "nconstraints",
    "objective", "note",
]


def parse_ns(spec):
    """Parse ``8,10,12`` or ``8:40:2`` (start:stop:step) into a list of ints."""
    if ":" in spec and "," not in spec:
        start, stop, step = (int(x) for x in spec.split(":"))
        return list(range(start, stop + 1, step))
    return [int(x) for x in spec.split(",") if x.strip()]


def run_sat_bench(ns, encodings=None, solvers=None, diagonal_mode="optimal",
                  repeats=1):
    encodings = encodings or DEFAULT_ENCODINGS
    solvers = solvers or ["glucose3", "cadical153", "kissat404"]

    rows = []
    for n in ns:
        for encoding in encodings:
            for solver in solvers:
                for rep in range(repeats):
                    row = {
                        "method": "sat", "n": n, "encoding": encoding,
                        "solver": solver, "diagonal_mode": diagonal_mode,
                        "rep": rep, "status": "error", "build_time": float("nan"),
                        "solve_time": float("nan"), "time": float("nan"),
                        "nv": None, "nclauses": None, "decisions": None,
                        "propagations": None, "conflicts": None, "note": "",
                    }
                    try:
                        res = solve_sat(n, encoding=encoding,
                                        solver_name=solver,
                                        diagonal_mode=diagonal_mode)
                        row.update(
                            status=res.status, build_time=res.build_time,
                            solve_time=res.solve_time, time=res.time,
                            nv=res.nv, nclauses=res.nclauses,
                            decisions=res.decisions,
                            propagations=res.propagations,
                            conflicts=res.conflicts,
                        )
                    except Exception as exc:  # noqa: BLE001
                        row["note"] = f"{type(exc).__name__}: {exc}"
                    rows.append(row)
    return pd.DataFrame(rows, columns=SAT_COLUMNS)


def run_baseline_bench(ns, methods=None, time_limit=None, repeats=1):
    methods = methods or list(BASELINES)
    rows = []
    for n in ns:
        for method in methods:
            for rep in range(repeats):
                row = {
                    "method": method, "n": n, "rep": rep, "status": "error",
                    "time": float("nan"), "nv": None, "nconstraints": None,
                    "objective": None, "note": "",
                }
                try:
                    res = run_baseline(method, n, time_limit=time_limit)
                    row.update(
                        status=res.status, time=res.time, nv=res.nv,
                        nconstraints=res.nconstraints,
                        objective=res.objective, note=res.note,
                    )
                except Exception as exc:  # noqa: BLE001
                    row["note"] = f"{type(exc).__name__}: {exc}"
                rows.append(row)
    return pd.DataFrame(rows, columns=BASELINE_COLUMNS)


def save(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
