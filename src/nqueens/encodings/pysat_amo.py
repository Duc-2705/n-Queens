"""Wrappers around :mod:`pysat.card` AMO encodings."""

from pysat.card import CardEnc, EncType

ENCODINGS = {
    "pysat_pairwise": EncType.pairwise,
    "pysat_sequential": EncType.seqcounter,
    "pysat_bitwise": EncType.bitwise,
    "pysat_ladder": EncType.ladder,
    "pysat_sorting": EncType.sortnetwrk,
    "pysat_cardinality": EncType.cardnetwrk,
    "pysat_totalizer": EncType.totalizer,
}


def add_amo(cnf, lits, vpool, encoding):
    """Append the CNF of AtMostOne(``lits``) to ``cnf``."""
    if len(lits) <= 1:
        return
    encoded = CardEnc.atmost(lits=list(lits), bound=1, vpool=vpool,
                             encoding=encoding)
    cnf.extend(encoded.clauses)
