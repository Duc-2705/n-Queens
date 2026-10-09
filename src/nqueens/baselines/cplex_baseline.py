"""CPLEX baselines: MIP (docplex.mp) and CP (docplex.cp)."""

import os
import shutil
import sys
import time

from .base import BaselineResult, board_from_positions, diagonals


def _configure_cp_execfile():
    """Point docplex.cp at the pip-installed cpoptimizer executable."""
    from docplex.cp.config import context

    exe = shutil.which("cpoptimizer") or shutil.which("cpoptimizer.exe")
    if exe is None:
        candidate = os.path.join(sys.prefix, "Scripts", "cpoptimizer.exe")
        if os.path.exists(candidate):
            exe = candidate
    if exe:
        context.solver.local.execfile = exe


def solve_cplex_mp(n, time_limit=None):
    from docplex.mp.model import Model

    try:
        model = Model(name="nqueens")
    except Exception as exc:  # pragma: no cover - license/engine dependent
        return BaselineResult("cplex_mp", n, "error", 0.0, note=str(exc))

    if time_limit is not None:
        model.set_time_limit(float(time_limit))

    x = model.binary_var_matrix(range(n), range(n), name="x")
    for r in range(n):
        model.add_constraint(model.sum(x[r, c] for c in range(n)) == 1)
    for c in range(n):
        model.add_constraint(model.sum(x[r, c] for r in range(n)) <= 1)
    for cells in diagonals(n):
        model.add_constraint(model.sum(x[cell] for cell in cells) <= 1)

    t0 = time.perf_counter()
    solution = model.solve(log_output=False)
    elapsed = time.perf_counter() - t0

    if solution is not None:
        positions = [(r, c) for r in range(n) for c in range(n)
                     if x[r, c].solution_value > 0.5]
        return BaselineResult(
            method="cplex_mp", n=n, status="sat", time=elapsed,
            nv=model.get_statistics().number_of_variables,
            nconstraints=model.get_statistics().number_of_constraints,
            objective=solution.get_objective_value(),
            board=board_from_positions(positions, n),
        )
    return BaselineResult("cplex_mp", n, "unsat", elapsed,
                          note=str(model.solve_details.status))


def solve_cplex_cp(n, time_limit=None):
    from docplex.cp.model import CpoModel

    _configure_cp_execfile()

    try:
        model = CpoModel(name="nqueens")
    except Exception as exc:  # pragma: no cover - license/engine dependent
        return BaselineResult("cplex_cp", n, "error", 0.0, note=str(exc))

    x = [[model.integer_var(0, 1, name=f"x_{r}_{c}") for c in range(n)]
         for r in range(n)]

    for r in range(n):
        model.add(model.sum(x[r]) == 1)
    for c in range(n):
        model.add(model.sum(x[r][c] for r in range(n)) <= 1)
    for cells in diagonals(n):
        model.add(model.sum(x[r][c] for r, c in cells) <= 1)

    kwargs = {"LogVerbosity": "Quiet"}
    if time_limit is not None:
        kwargs["TimeLimit"] = int(time_limit)

    t0 = time.perf_counter()
    solution = model.solve(**kwargs)
    elapsed = time.perf_counter() - t0

    if solution and solution.is_solution():
        positions = [(r, c) for r in range(n) for c in range(n)
                     if solution.get_value(x[r][c]) > 0.5]
        return BaselineResult(
            method="cplex_cp", n=n, status="sat", time=elapsed,
            nv=n * n, board=board_from_positions(positions, n),
        )
    return BaselineResult("cplex_cp", n, "unsat", elapsed, nv=n * n)
