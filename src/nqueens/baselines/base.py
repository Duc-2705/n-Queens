"""Common types and helpers for the exact baselines (MIP/CP)."""

from dataclasses import dataclass, field


@dataclass
class BaselineResult:
    method: str
    n: int
    status: str
    time: float
    nv: int = 0
    nconstraints: int = 0
    objective: float = None
    board: list = field(default=None)
    note: str = ""


def board_from_positions(positions, n):
    board = [["." for _ in range(n)] for _ in range(n)]
    for r, c in positions:
        board[r][c] = "Q"
    return board


def diagonals(n):
    """Yield tuples of (r, c) cells for every diagonal with >= 2 cells."""
    for d in range(-(n - 1), n):
        cells = [(r, r - d) for r in range(n) if 0 <= r - d < n]
        if len(cells) >= 2:
            yield cells
    for s in range(2 * n - 1):
        cells = [(r, s - r) for r in range(n) if 0 <= s - r < n]
        if len(cells) >= 2:
            yield cells
