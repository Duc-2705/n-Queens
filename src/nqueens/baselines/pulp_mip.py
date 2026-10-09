"""PuLP baseline using the bundled CBC solver."""

import time

from .base import BaselineResult, board_from_positions, diagonals


def solve_pulp(n, time_limit=None, msg=False):
    import pulp

    prob = pulp.LpProblem("nqueens", pulp.LpMinimize)
    x = {(r, c): pulp.LpVariable(f"x_{r}_{c}", cat="Binary")
         for r in range(n) for c in range(n)}
    prob += 0

    for r in range(n):
        prob += pulp.lpSum(x[(r, c)] for c in range(n)) == 1
    for c in range(n):
        prob += pulp.lpSum(x[(r, c)] for r in range(n)) <= 1
    for cells in diagonals(n):
        prob += pulp.lpSum(x[cell] for cell in cells) <= 1

    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit)

    t0 = time.perf_counter()
    status = prob.solve(solver)
    elapsed = time.perf_counter() - t0

    if status == pulp.LpStatusOptimal:
        positions = [(r, c) for (r, c) in x if x[(r, c)].value() > 0.5]
        return BaselineResult(
            method="pulp_cbc", n=n, status="sat", time=elapsed,
            nv=len(x), nconstraints=len(prob.constraints),
            board=board_from_positions(positions, n),
        )
    label = pulp.LpStatus.get(status, str(status))
    if label == "Infeasible":
        return BaselineResult("pulp_cbc", n, "unsat", elapsed, nv=len(x))
    return BaselineResult("pulp_cbc", n, "unknown", elapsed, nv=len(x),
                          note=label)
