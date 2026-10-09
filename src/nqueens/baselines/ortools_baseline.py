"""OR-Tools baselines: CP-SAT (CP) and the MIP solver (SCIP/CBC)."""

import time

from .base import BaselineResult, board_from_positions, diagonals


def solve_cpsat(n, time_limit=None, num_search_workers=8):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    x = {(r, c): model.NewBoolVar(f"x_{r}_{c}")
         for r in range(n) for c in range(n)}

    for r in range(n):
        model.AddExactlyOne(x[(r, c)] for c in range(n))
    for c in range(n):
        model.AddAtMostOne(x[(r, c)] for r in range(n))
    for cells in diagonals(n):
        model.AddAtMostOne(x[cell] for cell in cells)

    solver = cp_model.CpSolver()
    if time_limit is not None:
        solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_search_workers = num_search_workers

    t0 = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - t0

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        positions = [(r, c) for (r, c) in x if solver.Value(x[(r, c)])]
        return BaselineResult(
            method="cpsat", n=n, status="sat", time=elapsed,
            nv=len(x), nconstraints=len(model.Proto().constraints),
            board=board_from_positions(positions, n),
        )
    if status == cp_model.INFEASIBLE:
        return BaselineResult("cpsat", n, "unsat", elapsed, nv=len(x))
    return BaselineResult("cpsat", n, "unknown", elapsed, nv=len(x),
                          note=solver.StatusName(status))


def solve_mip_ortools(n, time_limit=None, solver_id="SCIP"):
    from ortools.linear_solver import pywraplp

    solver = pywraplp.Solver.CreateSolver(solver_id)
    if solver is None:
        raise RuntimeError(f"OR-Tools MIP backend {solver_id!r} unavailable")

    if time_limit is not None:
        solver.SetTimeLimit(int(time_limit * 1000))

    x = {(r, c): solver.IntVar(0, 1, f"x_{r}_{c}")
         for r in range(n) for c in range(n)}

    for r in range(n):
        solver.Add(solver.Sum(x[(r, c)] for c in range(n)) == 1)
    for c in range(n):
        solver.Add(solver.Sum(x[(r, c)] for r in range(n)) <= 1)
    for cells in diagonals(n):
        solver.Add(solver.Sum(x[cell] for cell in cells) <= 1)

    t0 = time.perf_counter()
    status = solver.Solve()
    elapsed = time.perf_counter() - t0

    if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        positions = [(r, c) for (r, c) in x if x[(r, c)].solution_value() > 0.5]
        return BaselineResult(
            method=f"mip_{solver_id.lower()}", n=n, status="sat", time=elapsed,
            nv=len(x), nconstraints=solver.NumConstraints(),
            board=board_from_positions(positions, n),
        )
    if status == pywraplp.Solver.INFEASIBLE:
        return BaselineResult(f"mip_{solver_id.lower()}", n, "unsat", elapsed,
                              nv=len(x))
    return BaselineResult(f"mip_{solver_id.lower()}", n, "unknown", elapsed,
                          nv=len(x))
