"""Benchmark harness for SAT encodings and exact baselines."""

from pathlib import Path

import pandas as pd

from .baselines import BASELINES, run_baseline
from .sat_solver import (
    DEFAULT_SOLVERS,
    SUPPORTED_SOLVERS,
    solve_sat,
    solve_sat_isolated,
)

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


def _fmt(value, spec="{:.4f}"):
    """Format a metric for logging; ``None``/NaN become ``-``."""
    if value is None:
        return "-"
    try:
        if value != value:  # NaN
            return "-"
    except TypeError:
        return str(value)
    if isinstance(value, (int, float)):
        return spec.format(value)
    return str(value)


def run_sat_bench(ns, encodings=None, solvers=None, diagonal_mode="optimal",
                  repeats=1, isolate=True, timeout=None, verbose=True):
    encodings = encodings or DEFAULT_ENCODINGS
    solvers = solvers or ["glucose3", "cadical153", "kissat404"]
    solve = solve_sat_isolated if isolate else solve_sat

    total = len(ns) * len(encodings) * len(solvers) * repeats
    idx = 0
    rows = []
    for n in ns:
        for encoding in encodings:
            for solver in solvers:
                for rep in range(repeats):
                    idx += 1
                    row = {
                        "method": "sat", "n": n, "encoding": encoding,
                        "solver": solver, "diagonal_mode": diagonal_mode,
                        "rep": rep, "status": "error", "build_time": float("nan"),
                        "solve_time": float("nan"), "time": float("nan"),
                        "nv": None, "nclauses": None, "decisions": None,
                        "propagations": None, "conflicts": None, "note": "",
                    }
                    try:
                        kwargs = {"timeout": timeout} if isolate else {}
                        res = solve(n, encoding=encoding, solver_name=solver,
                                    diagonal_mode=diagonal_mode, **kwargs)
                        row.update(
                            status=res.status, build_time=res.build_time,
                            solve_time=res.solve_time, time=res.time,
                            nv=res.nv, nclauses=res.nclauses,
                            decisions=res.decisions,
                            propagations=res.propagations,
                            conflicts=res.conflicts, note=res.note,
                        )
                    except Exception as exc:  # noqa: BLE001
                        row["note"] = f"{type(exc).__name__}: {exc}"
                    rows.append(row)

                    if verbose:
                        rep_tag = f" rep={rep}" if repeats > 1 else ""
                        note_tag = f" note={row['note']}" if row["note"] else ""
                        print(
                            f"[{idx}/{total}] sat n={n} enc={encoding} "
                            f"solver={solver}{rep_tag} status={row['status']} "
                            f"time={_fmt(row['time'])}s "
                            f"(build={_fmt(row['build_time'])}, "
                            f"solve={_fmt(row['solve_time'])}) "
                            f"vars={_fmt(row['nv'], '{:.0f}')} "
                            f"clauses={_fmt(row['nclauses'], '{:.0f}')} "
                            f"dec={_fmt(row['decisions'], '{:.0f}')} "
                            f"prop={_fmt(row['propagations'], '{:.0f}')} "
                            f"conf={_fmt(row['conflicts'], '{:.0f}')}{note_tag}",
                            flush=True,
                        )
    return pd.DataFrame(rows, columns=SAT_COLUMNS)


def run_baseline_bench(ns, methods=None, time_limit=None, repeats=1,
                       verbose=True):
    methods = methods or list(BASELINES)
    total = len(ns) * len(methods) * repeats
    idx = 0
    rows = []
    for n in ns:
        for method in methods:
            for rep in range(repeats):
                idx += 1
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

                if verbose:
                    rep_tag = f" rep={rep}" if repeats > 1 else ""
                    note_tag = f" note={row['note']}" if row["note"] else ""
                    print(
                        f"[{idx}/{total}] base n={n} method={method}{rep_tag} "
                        f"status={row['status']} time={_fmt(row['time'])}s "
                        f"vars={_fmt(row['nv'], '{:.0f}')} "
                        f"constr={_fmt(row['nconstraints'], '{:.0f}')}"
                        f"{note_tag}",
                        flush=True,
                    )
    return pd.DataFrame(rows, columns=BASELINE_COLUMNS)


def save(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
