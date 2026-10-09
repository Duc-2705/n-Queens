"""Run PySAT solvers on the N-Queens CNF and collect statistics.

Two entry points:

* :func:`solve_sat` runs the solver in-process (fast, used by tests/CLI when the
  solver is known to be safe).
* :func:`solve_sat_isolated` runs the solver in a child process so that a
  native crash (segfault) or a hang is reported as ``status="crash"`` /
  ``status="timeout"`` instead of killing the whole benchmark.
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass, field

from pysat.solvers import Solver, SolverNames

from .model import build_cnf
from .verify import board_from_model

try:
    SUPPORTED_SOLVERS = sorted(
        name for name in dir(SolverNames) if not name.startswith("_")
    )
except Exception:  # pragma: no cover
    SUPPORTED_SOLVERS = [
        "cadical153", "glucose3", "glucose4", "kissat404",
        "mergesat3", "minicard", "minisat22",
    ]

DEFAULT_SOLVERS = [
    "glucose3", "glucose4", "cadical153", "cadical195",
    "kissat404", "mergesat3", "minicard", "minisat22", "lingeling",
]


@dataclass
class SatResult:
    n: int
    encoding: str
    diagonal_mode: str
    solver: str
    status: str
    build_time: float
    solve_time: float
    nv: int
    nclauses: int
    decisions: int = 0
    propagations: int = 0
    conflicts: int = 0
    restarts: int = 0
    board: list = field(default=None)
    note: str = ""

    @property
    def time(self):
        return self.build_time + self.solve_time


def solve_sat(n, encoding="pairwise", solver_name="glucose3",
              diagonal_mode="optimal"):
    """Build the CNF and solve it once, in-process."""
    t0 = time.perf_counter()
    cnf = build_cnf(n, encoding=encoding, diagonal_mode=diagonal_mode)
    build_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        status = "sat" if solver.solve() else "unsat"
        model = solver.get_model() if status == "sat" else None
        stats = solver.accum_stats()
    solve_time = time.perf_counter() - t1

    board = board_from_model(model, n) if model is not None else None

    return SatResult(
        n=n,
        encoding=encoding,
        diagonal_mode=diagonal_mode,
        solver=solver_name,
        status=status,
        build_time=build_time,
        solve_time=solve_time,
        nv=cnf.nv,
        nclauses=len(cnf.clauses),
        decisions=stats.get("decisions", 0),
        propagations=stats.get("propagations", 0),
        conflicts=stats.get("conflicts", 0),
        restarts=stats.get("restarts", 0),
        board=board,
    )


def solve_sat_isolated(n, encoding="pairwise", solver_name="glucose3",
                       diagonal_mode="optimal", timeout=None):
    """Solve in a child process; survives native crashes and enforces timeout."""
    payload = json.dumps({
        "n": n, "encoding": encoding, "solver_name": solver_name,
        "diagonal_mode": diagonal_mode,
    })
    cmd = [sys.executable, "-m", "nqueens._worker", payload]

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - t0
        return SatResult(n=n, encoding=encoding, diagonal_mode=diagonal_mode,
                         solver=solver_name, status="timeout", build_time=0.0,
                         solve_time=elapsed, nv=0, nclauses=0)
    elapsed = time.perf_counter() - t0

    if proc.returncode != 0:
        note = (proc.stderr or proc.stdout or "").strip()[-300:]
        return SatResult(n=n, encoding=encoding, diagonal_mode=diagonal_mode,
                         solver=solver_name, status="crash", build_time=0.0,
                         solve_time=elapsed, nv=0, nclauses=0,
                         note=note or f"exit code {proc.returncode}")

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        note = (proc.stdout + proc.stderr).strip()[-300:]
        return SatResult(n=n, encoding=encoding, diagonal_mode=diagonal_mode,
                         solver=solver_name, status="error", build_time=0.0,
                         solve_time=elapsed, nv=0, nclauses=0, note=note)
    return SatResult(**data)


def probe_solvers(solvers=None, n=6, timeout=30):
    """Return a {solver: status} report by trying each solver in isolation."""
    solvers = solvers or list(dict.fromkeys(DEFAULT_SOLVERS + SUPPORTED_SOLVERS))
    report = {}
    for name in solvers:
        result = solve_sat_isolated(n, encoding="sequential",
                                    solver_name=name, timeout=timeout)
        report[name] = result.status
    return report
