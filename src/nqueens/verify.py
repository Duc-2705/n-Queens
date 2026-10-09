"""Board helpers and solution counting."""

from pysat.solvers import Solver

from .model import build_cnf

KNOWN_SOLUTION_COUNTS = {
    1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40,
    8: 92, 9: 352, 10: 724, 11: 2680, 12: 14200,
}


def board_from_model(model, n):
    """Convert a SAT model (list of literals) into an n x n character board."""
    true_lits = {lit for lit in model if lit > 0}
    board = [["." for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            if (r * n + c + 1) in true_lits:
                board[r][c] = "Q"
    return board


def queen_positions(board):
    return [
        (r, c)
        for r, row in enumerate(board)
        for c, cell in enumerate(row)
        if cell == "Q"
    ]


def is_valid_board(board):
    """True iff ``board`` is a valid non-attacking N-Queens placement."""
    if not board:
        return False
    n = len(board)
    if any(len(row) != n for row in board):
        return False

    positions = queen_positions(board)
    if len(positions) != n:
        return False

    rows, cols, diag, anti = set(), set(), set(), set()
    for r, c in positions:
        if r in rows or c in cols or (r - c) in diag or (r + c) in anti:
            return False
        rows.add(r)
        cols.add(c)
        diag.add(r - c)
        anti.add(r + c)
    return True


def count_solutions(n, encoding="sequential", solver_name="glucose3",
                    diagonal_mode="optimal", limit=None):
    """Enumerate solutions by repeatedly blocking the current assignment."""
    cnf = build_cnf(n, encoding=encoding, diagonal_mode=diagonal_mode)
    count = 0
    with Solver(name=solver_name, bootstrap_with=cnf.clauses) as solver:
        while solver.solve():
            model = solver.get_model()
            count += 1
            if limit is not None and count >= limit:
                break
            solver.add_clause([-v for v in model if 1 <= v <= n * n])
    return count
