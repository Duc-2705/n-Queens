import pytest

from nqueens import is_valid_board, solve_sat
from nqueens.encodings import ALL_ENCODINGS

MANUAL = ["pairwise", "binary", "commander", "product", "sequential"]
PYSAT = ["pysat_pairwise", "pysat_sequential", "pysat_bitwise",
         "pysat_ladder", "pysat_sorting", "pysat_cardinality",
         "pysat_totalizer"]


@pytest.mark.parametrize("encoding", ALL_ENCODINGS)
def test_encoding_solves_and_board_valid(encoding):
    result = solve_sat(6, encoding=encoding, solver_name="glucose3")
    assert result.status == "sat"
    assert is_valid_board(result.board)


@pytest.mark.parametrize("encoding", MANUAL + PYSAT)
def test_encoding_unsat_for_small_n(encoding):
    for n in (2, 3):
        result = solve_sat(n, encoding=encoding, solver_name="glucose3")
        assert result.status == "unsat"


@pytest.mark.parametrize("encoding", MANUAL + PYSAT)
def test_encoding_n1(encoding):
    result = solve_sat(1, encoding=encoding, solver_name="glucose3")
    assert result.status == "sat"
    assert result.board == [["Q"]]


def test_unknown_encoding_raises():
    with pytest.raises(ValueError):
        solve_sat(4, encoding="does-not-exist")
