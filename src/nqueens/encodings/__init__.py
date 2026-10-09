"""AMO/ALO encodings.

``manual`` holds hand-written (from-scratch) encodings.
``pysat_amo`` wraps :mod:`pysat.card` encodings.
"""

from . import manual, pysat_amo

MANUAL_ENCODINGS = manual.ENCODINGS
PYSAT_ENCODINGS = pysat_amo.ENCODINGS
ALL_ENCODINGS = {**MANUAL_ENCODINGS, **PYSAT_ENCODINGS}

__all__ = [
    "manual",
    "pysat_amo",
    "MANUAL_ENCODINGS",
    "PYSAT_ENCODINGS",
    "ALL_ENCODINGS",
]
