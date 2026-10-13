"""Build report figures and LaTeX tables from the benchmark CSVs.

Reads ``results/sat.csv`` and ``results/baselines.csv`` and writes:
    report/figures/*.pdf|png
    report/tables/*.tex
Run:  python scripts/make_report_assets.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numbers
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAT_CSV = ROOT / "results" / "sat.csv"
BASE_CSV = ROOT / "results" / "baselines.csv"
FIGDIR = ROOT / "report" / "figures"
TABDIR = ROOT / "report" / "tables"

ENCODINGS = ["pairwise", "binary", "commander", "product", "sequential"]
SOLVERS = ["minisat22", "minicard", "cadical153", "cadical195",
           "mergesat3", "lingeling", "glucose4", "glucose3"]
METHODS = ["gurobi", "cplex_mp", "cpsat", "cplex_cp",
           "mip_scip", "mip_cbc", "pulp_cbc"]
SIZES = [16, 24, 32, 40, 48, 56, 64, 72, 80]


def save(fig, name):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIGDIR / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print("figure:", name)


def sat_pivot(sat, index="n", columns="solver", min_n=None):
    d = sat[sat.status == "sat"]
    if min_n is not None:
        d = d[d.n >= min_n]
    return d.pivot_table(index=index, columns=columns, values="time",
                         aggfunc="median")


def fig_heatmap(sat):
    piv = sat_pivot(sat, index="encoding", columns="solver", min_n=40)
    piv = piv.reindex(index=ENCODINGS, columns=SOLVERS)
    data = piv.values.astype(float)
    masked = np.ma.masked_invalid(data)

    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    im = ax.imshow(np.log10(masked), aspect="auto", cmap="viridis_r")
    ax.set_xticks(range(len(SOLVERS)), SOLVERS, rotation=45, ha="right")
    ax.set_yticks(range(len(ENCODINGS)), ENCODINGS)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            ax.text(j, i, "-" if np.isnan(v) else f"{v:.2f}",
                    ha="center", va="center", fontsize=7,
                    color="white" if (not np.isnan(v) and v > 3) else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("log10 median time (s)")
    ax.set_title("Median SAT time, n >= 40 (encoding x solver)")
    save(fig, "heatmap_encoding_solver")


def fig_solver_by_encoding(sat):
    fig, axes = plt.subplots(2, 3, figsize=(11, 6), sharex=True, sharey=True)
    axes = axes.ravel()
    d = sat[sat.status == "sat"]
    for k, enc in enumerate(ENCODINGS):
        ax = axes[k]
        part = d[d.encoding == enc]
        for sol in SOLVERS:
            s = part[part.solver == sol].groupby("n").time.median()
            if len(s):
                ax.plot(s.index, s.values, marker=".", ms=4, lw=1, label=sol)
        ax.set_yscale("log")
        ax.set_title(enc)
        ax.grid(True, which="both", ls=":", lw=0.4)
    axes[5].axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    axes[5].legend(handles, labels, loc="center", fontsize=8, ncol=2)
    for ax in axes[4:6]:
        ax.set_xlabel("n")
    for ax in (axes[0], axes[3]):
        ax.set_ylabel("time (s)")
    fig.suptitle("SAT time vs n, per encoding (line = solver)", y=1.02)
    save(fig, "solver_by_encoding")


def fig_baselines(base):
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for m in METHODS:
        s = base[base.method == m].groupby("n").time.median()
        ax.plot(s.index, s.values, marker="s", ms=3, lw=1, label=m)
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("time (s)")
    ax.set_title("MIP/CP baselines: time vs n")
    ax.grid(True, which="both", ls=":", lw=0.4)
    ax.legend(fontsize=8)
    save(fig, "baselines_time_vs_n")


def fig_method_comparison(sat, base):
    best_enc, best_sol = "binary", "minisat22"
    d = sat[(sat.status == "sat") & (sat.solver == best_sol)
            & (sat.encoding == best_enc)]
    s = d.groupby("n").time.median()

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(s.index, s.values, marker="o", label=f"SAT ({best_enc}+{best_sol})")
    for m in METHODS:
        b = base[base.method == m].groupby("n").time.median()
        ax.plot(b.index, b.values, marker="s", ms=3, lw=1, label=m)
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("time (s)")
    ax.set_title("Best SAT vs MIP/CP")
    ax.grid(True, which="both", ls=":", lw=0.4)
    ax.legend(fontsize=7)
    save(fig, "method_comparison")


def esc(s):
    """Escape LaTeX special characters in plain text (avoid double escaping)."""
    s = str(s)
    s = re.sub(r"(?<!\\)_", r"\\_", s)
    s = re.sub(r"(?<!\\)&", r"\\&", s)
    s = re.sub(r"(?<!\\)%", r"\\%", s)
    return s


def tex_table(df, caption, label, fmt="{:.3f}", row_name=None):
    df = df.copy()
    index_name = df.index.name or ""
    cols = list(df.columns)
    lines = [
        "\\begin{table}[t]", "\\centering",
        f"\\caption{{{caption}}}", f"\\label{{{label}}}",
        "\\begin{tabular}{l" + "r" * len(cols) + "}", "\\toprule",
        esc(index_name) + " & " + " & ".join(esc(c) for c in cols) + " \\\\",
        "\\midrule",
    ]
    for row in df.itertuples(index=True):
        idx = row[0]
        cells = []
        for v in row[1:]:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                cells.append("--")
            elif isinstance(v, bool):
                cells.append(str(v))
            elif isinstance(v, numbers.Integral):
                cells.append(str(int(v)))
            elif isinstance(v, numbers.Real):
                cells.append(fmt.format(float(v)))
            else:
                cells.append(esc(v))
        lines.append(esc(idx) + " & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


CAPTIONS = {
    "en": {
        "structure": "CNF size of each encoding for n = 40.",
        "solver": ("SAT solver ranking over $n \\geq$ 40 (median time across "
                   "encodings) and number of timeouts."),
        "enc_solver": ("Median SAT solving time (s) for $n \\geq 40$ by "
                       "encoding and solver (-- = all runs timed out)."),
        "baseline": "Median solving time (s) of the MIP/CP baselines.",
    },
    "vi": {
        "structure": "Kích thước CNF của mỗi encoding với n = 40.",
        "solver": ("Xếp hạng các bộ giải SAT với $n \\geq 40$ (thời gian trung vị "
                   "trên mọi encoding) và số lần timeout."),
        "enc_solver": ("Thời gian giải SAT trung vị (giây) với $n \\geq 40$ theo "
                       "encoding và solver (-- = mọi lần chạy đều timeout)."),
        "baseline": "Thời gian giải trung vị (giây) của các baseline MIP/CP.",
    },
}


def write_tables(sat, base):
    structure = (sat[(sat.n == 40) & (sat.rep == 0)]
                 .drop_duplicates("encoding").set_index("encoding")
                 [["nv", "nclauses"]].reindex(ENCODINGS))
    structure.columns = ["\\#vars", "\\#clauses"]
    structure["\\#clauses"] = structure["\\#clauses"].astype(int)

    piv = sat_pivot(sat, "encoding", "solver", min_n=40).reindex(
        index=ENCODINGS, columns=SOLVERS)

    solver_rank = sat_pivot(sat, None, "solver", min_n=40).T.median(axis=1)
    solver_rank = solver_rank.sort_values()
    timeouts = (sat[sat.status == "timeout"].groupby("solver").size()
                .reindex(solver_rank.index).fillna(0).astype(int))
    ranking = pd.DataFrame({"median time (s)": solver_rank,
                            "timeouts": timeouts})
    ranking.index.name = "solver"

    bp = base[base.n.isin(SIZES)].pivot_table(
        index="n", columns="method", values="time", aggfunc="median")
    bp = bp.reindex(columns=METHODS)

    for lang, cap in CAPTIONS.items():
        out = TABDIR / lang
        out.mkdir(parents=True, exist_ok=True)
        (out / "structure.tex").write_text(tex_table(
            structure, cap["structure"], "tab:structure", fmt="{:.0f}"),
            encoding="utf-8")
        (out / "encoding_solver.tex").write_text(tex_table(
            piv, cap["enc_solver"], "tab:enc_solver"), encoding="utf-8")
        (out / "solver_ranking.tex").write_text(tex_table(
            ranking, cap["solver"], "tab:solver_rank"), encoding="utf-8")
        (out / "baseline.tex").write_text(tex_table(
            bp, cap["baseline"], "tab:baseline"), encoding="utf-8")
    print("tables written to", TABDIR)


def main():
    sat = pd.read_csv(SAT_CSV)
    base = pd.read_csv(BASE_CSV)
    fig_heatmap(sat)
    fig_solver_by_encoding(sat)
    fig_baselines(base)
    fig_method_comparison(sat, base)
    write_tables(sat, base)


if __name__ == "__main__":
    main()
