"""Exact baselines: MIP/ILP and CP solvers."""

from .base import BaselineResult, board_from_positions, diagonals
from .ortools_baseline import solve_cpsat, solve_mip_ortools
from .pulp_mip import solve_pulp
from .gurobi_baseline import solve_gurobi
from .cplex_baseline import solve_cplex_mp, solve_cplex_cp

BASELINES = {
    "cpsat": solve_cpsat,
    "mip_scip": lambda n, time_limit=None: solve_mip_ortools(
        n, time_limit=time_limit, solver_id="SCIP"),
    "mip_cbc": lambda n, time_limit=None: solve_mip_ortools(
        n, time_limit=time_limit, solver_id="CBC"),
    "pulp_cbc": solve_pulp,
    "gurobi": solve_gurobi,
    "cplex_mp": solve_cplex_mp,
    "cplex_cp": solve_cplex_cp,
}


def run_baseline(name, n, time_limit=None):
    """Run a single baseline by name and return a :class:`BaselineResult`."""
    if name not in BASELINES:
        raise ValueError(f"Unknown baseline {name!r}. Choose from {list(BASELINES)}")
    return BASELINES[name](n, time_limit=time_limit)


__all__ = [
    "BaselineResult",
    "board_from_positions",
    "diagonals",
    "BASELINES",
    "run_baseline",
    "solve_cpsat",
    "solve_mip_ortools",
    "solve_pulp",
    "solve_gurobi",
    "solve_cplex_mp",
    "solve_cplex_cp",
]
