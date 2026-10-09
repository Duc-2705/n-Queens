"""n-Queens: SAT encodings (PySAT) and exact baselines (MIP/CP)."""

from .model import build_cnf, var
from .sat_solver import SatResult, solve_sat
from .verify import (
    KNOWN_SOLUTION_COUNTS,
    board_from_model,
    count_solutions,
    is_valid_board,
)

__all__ = [
    "build_cnf",
    "var",
    "SatResult",
    "solve_sat",
    "KNOWN_SOLUTION_COUNTS",
    "board_from_model",
    "count_solutions",
    "is_valid_board",
]

__version__ = "0.1.0"
