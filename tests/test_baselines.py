import pytest

from nqueens import is_valid_board
from nqueens.baselines import run_baseline

FREE_BASELINES = ["cpsat", "mip_scip", "mip_cbc", "pulp_cbc"]


@pytest.mark.parametrize("method", FREE_BASELINES)
def test_free_baseline_solves(method):
    result = run_baseline(method, 6, time_limit=30)
    assert result.status == "sat"
    assert is_valid_board(result.board)


@pytest.mark.parametrize("method", ["cpsat"])
def test_baseline_unsat(method):
    for n in (2, 3):
        result = run_baseline(method, n, time_limit=30)
        assert result.status == "unsat"
