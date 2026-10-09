import pytest

from nqueens import (
    KNOWN_SOLUTION_COUNTS,
    board_from_model,
    count_solutions,
    is_valid_board,
)


def make_board(positions, n):
    board = [["." for _ in range(n)] for _ in range(n)]
    for r, c in positions:
        board[r][c] = "Q"
    return board


@pytest.mark.parametrize("encoding", ["pairwise", "sequential", "commander"])
def test_solution_counts_match_known(encoding):
    for n in range(1, 8):
        count = count_solutions(n, encoding=encoding, solver_name="glucose3")
        assert count == KNOWN_SOLUTION_COUNTS[n], (n, encoding, count)


def test_board_from_model():
    model = [2, 8, 9, 15]
    board = board_from_model(model, 4)
    assert is_valid_board(board)
    assert board == make_board([(0, 1), (1, 3), (2, 0), (3, 2)], 4)


def test_is_valid_board_accepts_known_solution():
    assert is_valid_board(make_board([(0, 1), (1, 3), (2, 0), (3, 2)], 4))


def test_is_valid_board_rejects_attacks():
    assert not is_valid_board(make_board([(0, 0), (1, 1)], 4))
    assert not is_valid_board(make_board([(0, 0), (0, 1)], 4))
    assert not is_valid_board(make_board([(0, 0)], 4))
    assert not is_valid_board([])


def test_count_with_limit():
    assert count_solutions(8, encoding="sequential", limit=5) == 5
