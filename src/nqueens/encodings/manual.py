"""Hand-written (from-scratch) AMO/ALO encodings.

Every encoder has the signature ``f(cnf, lits, pool)`` where ``cnf`` is a
:class:`pysat.formula.CNF`, ``lits`` is the list of literals the
*at-most-one* constraint ranges over, and ``pool`` is an :class:`AuxPool`
used to allocate auxiliary variables.
"""

from itertools import combinations
from math import ceil, sqrt


class AuxPool:
    """Monotonic allocator of auxiliary variable ids."""

    def __init__(self, start=0):
        self._top = start

    def new(self):
        self._top += 1
        return self._top

    @property
    def top(self):
        return self._top


def add_alo(cnf, lits):
    """At-least-one over ``lits``: a single clause."""
    cnf.append(list(lits))


def add_pairwise(cnf, lits, pool=None):
    """At-most-one via every pairwise negative clause (O(n^2) clauses)."""
    for a, b in combinations(lits, 2):
        cnf.append([-a, -b])


def add_binary(cnf, lits, pool):
    """At-most-one with a binary (log n) address per literal."""
    n = len(lits)
    if n <= 1:
        return

    num_bits = (n - 1).bit_length()
    bits = [pool.new() for _ in range(num_bits)]

    for i, x in enumerate(lits):
        for j, b in enumerate(bits):
            if (i >> j) & 1:
                cnf.append([-x, b])
            else:
                cnf.append([-x, -b])


def add_commander(cnf, lits, pool, group_size=3):
    """Recursive commander encoding (group size <= ``group_size``)."""
    if len(lits) <= 1:
        return

    if len(lits) <= group_size:
        add_pairwise(cnf, lits)
        return

    commanders = []
    for i in range(0, len(lits), group_size):
        group = lits[i:i + group_size]
        add_pairwise(cnf, group)
        if len(group) == 1:
            commanders.append(group[0])
        else:
            commander = pool.new()
            commanders.append(commander)
            for x in group:
                cnf.append([-x, commander])

    add_commander(cnf, commanders, pool, group_size)


def add_product(cnf, lits, pool):
    """Product encoding: literals placed on a p x q grid with row/col AMO."""
    n = len(lits)
    if n <= 1:
        return

    p = ceil(sqrt(n))
    q = ceil(n / p)

    row_vars = [pool.new() for _ in range(p)]
    col_vars = [pool.new() for _ in range(q)]

    for k, x in enumerate(lits):
        r = k // q
        c = k % q
        cnf.append([-x, row_vars[r]])
        cnf.append([-x, col_vars[c]])

    add_pairwise(cnf, row_vars)
    add_pairwise(cnf, col_vars)


def add_sequential(cnf, lits, pool):
    """Sequential counter (Sinz) encoding with n-1 auxiliary variables."""
    n = len(lits)
    if n <= 1:
        return

    s = [pool.new() for _ in range(n - 1)]

    cnf.append([-lits[0], s[0]])
    for i in range(1, n - 1):
        cnf.append([-lits[i], s[i]])
        cnf.append([-s[i - 1], s[i]])
    for i in range(1, n):
        cnf.append([-lits[i], -s[i - 1]])


ENCODINGS = {
    "pairwise": add_pairwise,
    "binary": add_binary,
    "commander": add_commander,
    "product": add_product,
    "sequential": add_sequential,
}
