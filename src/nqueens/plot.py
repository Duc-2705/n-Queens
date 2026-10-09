"""Generate figures from benchmark CSVs (matplotlib, non-interactive)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def _save(fig, outdir, name):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(outdir / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)


def plot_time_vs_n(df, outdir, group="solver", method="sat",
                   solver=None, encoding=None, name="time_vs_n"):
    """Plot solve time versus n, one curve per ``group`` value."""
    data = df[(df["method"] == method) & (df["status"] == "sat")].copy()
    if solver is not None:
        data = data[data["solver"] == solver]
    if encoding is not None:
        data = data[data["encoding"] == encoding]
    if data.empty:
        return None

    fig, ax = plt.subplots()
    for key, part in data.groupby(group):
        series = part.groupby("n")["time"].median()
        ax.plot(series.index, series.values, marker="o", label=str(key))
    ax.set_xlabel("n")
    ax.set_ylabel("time (s)")
    ax.set_yscale("log")
    ax.set_title(f"SAT time vs n (by {group})")
    ax.legend()
    ax.grid(True, which="both", ls=":")
    _save(fig, outdir, name)
    return name


def plot_encoding_comparison(df, outdir, solver="glucose3",
                             name="encoding_comparison"):
    data = df[(df["method"] == "sat") & (df["solver"] == solver)
              & (df["status"] == "sat")]
    if data.empty:
        return None

    fig, ax = plt.subplots()
    for encoding, part in data.groupby("encoding"):
        series = part.groupby("n")["time"].median()
        ax.plot(series.index, series.values, marker="o", label=encoding)
    ax.set_xlabel("n")
    ax.set_ylabel("time (s)")
    ax.set_yscale("log")
    ax.set_title(f"Encoding comparison ({solver})")
    ax.legend()
    ax.grid(True, which="both", ls=":")
    _save(fig, outdir, name)
    return name


def plot_method_comparison(sat_df, baseline_df, outdir,
                           name="method_comparison", solver="glucose3",
                           encoding="sequential"):
    sat = sat_df[(sat_df["method"] == "sat")
                 & (sat_df["solver"] == solver)
                 & (sat_df["encoding"] == encoding)
                 & (sat_df["status"] == "sat")]
    base = baseline_df[baseline_df["status"].isin(["sat", "unsat"])]

    fig, ax = plt.subplots()
    if not sat.empty:
        s = sat.groupby("n")["time"].median()
        ax.plot(s.index, s.values, marker="o", label=f"SAT ({encoding})")
    for method, part in base.groupby("method"):
        s = part.groupby("n")["time"].median()
        ax.plot(s.index, s.values, marker="s", label=method)
    ax.set_xlabel("n")
    ax.set_ylabel("time (s)")
    ax.set_yscale("log")
    ax.set_title("SAT vs MIP/CP")
    ax.legend()
    ax.grid(True, which="both", ls=":")
    _save(fig, outdir, name)
    return name


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Plot benchmark CSVs.")
    parser.add_argument("--sat", default="results/sat.csv")
    parser.add_argument("--baselines", default="results/baselines.csv")
    parser.add_argument("--outdir", default="results/figures")
    args = parser.parse_args()

    sat_path = Path(args.sat)
    base_path = Path(args.baselines)
    sat_df = pd.read_csv(sat_path) if sat_path.exists() else None
    base_df = pd.read_csv(base_path) if base_path.exists() else None

    if sat_df is not None:
        plot_time_vs_n(sat_df, args.outdir)
        plot_encoding_comparison(sat_df, args.outdir)
    if sat_df is not None and base_df is not None:
        plot_method_comparison(sat_df, base_df, args.outdir)
    print("Figures written to", args.outdir)


if __name__ == "__main__":
    main()
