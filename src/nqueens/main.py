"""Command-line entry point: ``python -m nqueens ...``."""

import argparse

from .baselines import BASELINES
from .bench import (
    DEFAULT_ENCODINGS,
    parse_ns,
    run_baseline_bench,
    run_sat_bench,
    save,
)
from .encodings import ALL_ENCODINGS
from .sat_solver import (
    DEFAULT_SOLVERS,
    SUPPORTED_SOLVERS,
    probe_solvers,
    solve_sat_isolated,
)
from .verify import KNOWN_SOLUTION_COUNTS, count_solutions, is_valid_board


def _print_board(board):
    for row in board:
        print(" ".join(row))


def cmd_solve(args):
    res = solve_sat_isolated(args.n, encoding=args.encoding,
                             solver_name=args.solver,
                             diagonal_mode=args.diagonal,
                             timeout=args.time_limit)
    print(f"n={res.n} encoding={res.encoding} solver={res.solver} "
          f"diagonal={res.diagonal_mode}")
    print(f"status={res.status} time={res.time:.4f}s "
          f"(build={res.build_time:.4f}, solve={res.solve_time:.4f})")
    if res.status == "sat":
        print(f"vars={res.nv} clauses={res.nclauses} "
              f"decisions={res.decisions} propagations={res.propagations} "
              f"conflicts={res.conflicts}")
        _print_board(res.board)
        print("valid:", is_valid_board(res.board))
    elif res.note:
        print("note:", res.note)


def cmd_count(args):
    count = count_solutions(args.n, encoding=args.encoding,
                            solver_name=args.solver,
                            diagonal_mode=args.diagonal, limit=args.limit)
    expected = KNOWN_SOLUTION_COUNTS.get(args.n)
    print(f"n={args.n} encoding={args.encoding} solutions={count}"
          + (f" (expected {expected})" if expected is not None else ""))


def cmd_bench(args):
    ns = parse_ns(args.ns)
    verbose = not args.quiet
    if args.what in ("sat", "all"):
        df = run_sat_bench(ns, encodings=args.encodings,
                           solvers=args.solvers, diagonal_mode=args.diagonal,
                           repeats=args.repeats, isolate=not args.no_isolate,
                           timeout=args.time_limit, verbose=verbose)
        print("wrote", save(df, args.sat_out))
    if args.what in ("baselines", "all"):
        methods = args.methods or list(BASELINES)
        df = run_baseline_bench(ns, methods=methods,
                                time_limit=args.time_limit,
                                repeats=args.repeats, verbose=verbose)
        print("wrote", save(df, args.baseline_out))


def cmd_probe(args):
    solvers = args.solvers or DEFAULT_SOLVERS
    report = probe_solvers(solvers, n=args.n, timeout=args.time_limit or 30)
    print(f"{'solver':<16} status")
    for name, status in report.items():
        print(f"{name:<16} {status}")


def cmd_plot(args):
    from . import plot

    argv = ["--sat", args.sat, "--baselines", args.baselines,
            "--outdir", args.outdir]
    import sys
    old, sys.argv = sys.argv, ["nqueens-plot", *argv]
    try:
        plot.main()
    finally:
        sys.argv = old


def build_parser():
    parser = argparse.ArgumentParser(prog="nqueens",
                                     description="N-Queens: SAT encodings and exact baselines.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_solve = sub.add_parser("solve", help="Solve N-Queens and print the board.")
    p_solve.add_argument("n", type=int)
    p_solve.add_argument("--encoding", default="sequential",
                         choices=sorted(ALL_ENCODINGS))
    p_solve.add_argument("--solver", default="glucose3",
                         choices=SUPPORTED_SOLVERS)
    p_solve.add_argument("--diagonal", default="optimal",
                         choices=["naive", "optimal"])
    p_solve.add_argument("--time-limit", type=float, default=None,
                         help="timeout in seconds for the solver subprocess")
    p_solve.set_defaults(func=cmd_solve)

    p_count = sub.add_parser("count", help="Count all solutions for small n.")
    p_count.add_argument("n", type=int)
    p_count.add_argument("--encoding", default="sequential",
                         choices=sorted(ALL_ENCODINGS))
    p_count.add_argument("--solver", default="glucose3",
                         choices=SUPPORTED_SOLVERS)
    p_count.add_argument("--diagonal", default="optimal",
                         choices=["naive", "optimal"])
    p_count.add_argument("--limit", type=int, default=None)
    p_count.set_defaults(func=cmd_count)

    p_bench = sub.add_parser("bench", help="Run benchmark grids to CSV.")
    p_bench.add_argument("--what", default="all",
                         choices=["sat", "baselines", "all"])
    p_bench.add_argument("--ns", default="8,10,12,14,16",
                         help="e.g. '8,10,12' or '8:40:2'")
    p_bench.add_argument("--encodings", nargs="*", default=None)
    p_bench.add_argument("--solvers", nargs="*", default=None)
    p_bench.add_argument("--methods", nargs="*", default=None)
    p_bench.add_argument("--diagonal", default="optimal",
                         choices=["naive", "optimal"])
    p_bench.add_argument("--time-limit", type=float, default=None)
    p_bench.add_argument("--repeats", type=int, default=1)
    p_bench.add_argument("--no-isolate", action="store_true",
                         help="run SAT solvers in-process (a crash aborts the run)")
    p_bench.add_argument("--quiet", action="store_true",
                         help="suppress per-run progress logging")
    p_bench.add_argument("--sat-out", default="results/sat.csv")
    p_bench.add_argument("--baseline-out", default="results/baselines.csv")
    p_bench.set_defaults(func=cmd_bench)

    p_probe = sub.add_parser("probe", help="Check which SAT solvers work here.")
    p_probe.add_argument("--solvers", nargs="*", default=None)
    p_probe.add_argument("--n", type=int, default=6)
    p_probe.add_argument("--time-limit", type=float, default=None)
    p_probe.set_defaults(func=cmd_probe)

    p_plot = sub.add_parser("plot", help="Generate figures from CSV results.")
    p_plot.add_argument("--sat", default="results/sat.csv")
    p_plot.add_argument("--baselines", default="results/baselines.csv")
    p_plot.add_argument("--outdir", default="results/figures")
    p_plot.set_defaults(func=cmd_plot)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
