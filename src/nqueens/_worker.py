"""Isolated worker: solve one SAT instance and print the result as JSON.

Run as ``python -m nqueens._worker '<json>'`` so that a crashing solver only
kills this short-lived process instead of the whole benchmark.
"""

import json
import sys


def main():
    payload = json.loads(sys.argv[1])
    from .sat_solver import solve_sat

    result = solve_sat(**payload)
    json.dump(result.__dict__, sys.stdout)


if __name__ == "__main__":
    main()
