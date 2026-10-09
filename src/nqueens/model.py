"""CNF model of the N-Queens problem."""

from pysat.formula import CNF, IDPool

from .encodings import manual, pysat_amo
from .encodings.manual import AuxPool

DIAGONAL_MODES = ("naive", "optimal")


def var(r, c, n):
    """1-based SAT variable for cell (r, c): ``r*n + c + 1``."""
    return r * n + c + 1


def _diagonal_lits(n):
    """Yield literal lists for every diagonal with at least two cells."""
    for d in range(-(n - 1), n):
        lits = [var(r, r - d, n) for r in range(n) if 0 <= r - d < n]
        if len(lits) >= 2:
            yield lits
    for s in range(2 * n - 1):
        lits = [var(r, s - r, n) for r in range(n) if 0 <= s - r < n]
        if len(lits) >= 2:
            yield lits


def _make_amo(cnf, encoding, n):
    """Return a callable applying the chosen AMO encoding to a literal list."""
    if encoding in manual.ENCODINGS:
        pool = AuxPool(n * n)
        fn = manual.ENCODINGS[encoding]
        return lambda lits: fn(cnf, lits, pool)

    if encoding in pysat_amo.ENCODINGS:
        pool = IDPool(start_from=n * n + 1)
        enc_type = pysat_amo.ENCODINGS[encoding]
        return lambda lits: pysat_amo.add_amo(cnf, lits, pool, enc_type)

    raise ValueError(
        f"Unknown encoding: {encoding!r}. "
        f"Choose from {sorted(manual.ENCODINGS) + sorted(pysat_amo.ENCODINGS)}"
    )


def build_cnf(n, encoding="pairwise", diagonal_mode="optimal"):
    """Build the CNF for N-Queens.

    Rows use ALO + AMO (exactly one queen); columns and diagonals use AMO
    only, which together with the rows implies exactly one queen per column.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if diagonal_mode not in DIAGONAL_MODES:
        raise ValueError(f"diagonal_mode must be one of {DIAGONAL_MODES}")

    cnf = CNF()
    amo = _make_amo(cnf, encoding, n)

    for r in range(n):
        lits = [var(r, c, n) for c in range(n)]
        manual.add_alo(cnf, lits)
        amo(lits)

    for c in range(n):
        amo([var(r, c, n) for r in range(n)])

    if diagonal_mode == "naive":
        for r1 in range(n):
            for c1 in range(n):
                for r2 in range(r1 + 1, n):
                    for c2 in range(n):
                        if abs(r1 - r2) == abs(c1 - c2):
                            cnf.append([-var(r1, c1, n), -var(r2, c2, n)])
    else:
        for lits in _diagonal_lits(n):
            amo(lits)

    return cnf
