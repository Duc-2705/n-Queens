"""Run PySAT solvers on the N-Queens CNF and collect statistics."""

import time
from dataclasses import dataclass, field

from pysat.solvers import Solver, SolverNames

from .model import build_cnf
from .verify import board_from_model

SUPPORTED_SOLVERS = [
    "cadical103", "cadical153", "cadical195", "cadical300",
    "cryptosat", "glucose3", "glucose4", "glucose42",
    "kissat404", "lingeling", "maplesat", "mergesat3",
    "minicard", "minisat22", "minisatgh",
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

    @property
    def time(self):
        return self.build_time + self.solve_time


def solve_sat(n, encoding="pairwise", solver_name="glucose3",
              diagonal_mode="optimal"):
    """Build the CNF and solve it once with the given PySAT solver."""
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
