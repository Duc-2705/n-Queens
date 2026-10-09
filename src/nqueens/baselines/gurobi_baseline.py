"""Gurobi MIP baseline (requires a Gurobi license)."""

import time

from .base import BaselineResult, board_from_positions, diagonals


def solve_gurobi(n, time_limit=None):
    import gurobipy as gp
    from gurobipy import GRB

    try:
        model = gp.Model("nqueens")
    except gp.GurobiError as exc:
        return BaselineResult("gurobi", n, "error", 0.0, note=str(exc))

    model.Params.OutputFlag = 0
    if time_limit is not None:
        model.Params.TimeLimit = float(time_limit)

    x = model.addVars(n, n, vtype=GRB.BINARY, name="x")

    for r in range(n):
        model.addConstr(gp.quicksum(x[r, c] for c in range(n)) == 1)
    for c in range(n):
        model.addConstr(gp.quicksum(x[r, c] for r in range(n)) <= 1)
    for cells in diagonals(n):
        model.addConstr(gp.quicksum(x[cell] for cell in cells) <= 1)

    t0 = time.perf_counter()
    model.optimize()
    elapsed = time.perf_counter() - t0

    if model.Status in (GRB.OPTIMAL, GRB.SUBOPTIMAL):
        positions = [(r, c) for r in range(n) for c in range(n)
                     if x[r, c].X > 0.5]
        return BaselineResult(
            method="gurobi", n=n, status="sat", time=elapsed,
            nv=model.NumVars, nconstraints=model.NumConstrs,
            board=board_from_positions(positions, n),
        )
    if model.Status == GRB.INFEASIBLE:
        return BaselineResult("gurobi", n, "unsat", elapsed, nv=model.NumVars)
    return BaselineResult("gurobi", n, "unknown", elapsed, nv=model.NumVars)
