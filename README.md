# n-Queens — SAT Encoding and Exact Solvers

Empirical study of the **N-Queens** problem solved via **SAT encoding** (PySAT,
multiple AMO/ALO encodings and SAT solvers) and compared against other exact
approaches: **MIP/ILP** and **CP** (CPLEX, Gurobi, OR-Tools CP-SAT, CBC/SCIP).

> Coursework: *Các vấn đề hiện đại KHMT* — Assignment 1
> (SAT Encoding for Logic puzzles, N-Queens).

## Features

- **CNF model** of N-Queens: rows use exactly-one (ALO + AMO); columns and
  diagonals use AMO. Two diagonal encodings: `naive` (pairwise) and `optimal`
  (AMO per diagonal).
- **AMO encodings implemented from scratch**: `pairwise`, `binary`, `commander`,
  `product`, `sequential`.
- **AMO encodings via PySAT** (`pysat.card`): `pysat_pairwise`,
  `pysat_sequential`, `pysat_bitwise`, `pysat_ladder`, `pysat_sorting`,
  `pysat_cardinality`, `pysat_totalizer`.
- **SAT solvers** through PySAT: CaDiCaL, Glucose, Kissat, CryptoMiniSat,
  MergeSAT, MiniCard, MiniSat, Lingeling.
- **Exact baselines**: OR-Tools **CP-SAT**, OR-Tools **MIP** (SCIP/CBC),
  **PuLP** (CBC), **Gurobi** (MIP), **CPLEX** (MIP and CP).
- **Benchmark harness** writing raw CSV, plus plotting utilities.
- **Correctness tests**: known solution counts for n = 1..12 and board validity.

## Layout

```
n-Queens/
  src/nqueens/            # package
    encodings/manual.py   # hand-written AMO encodings
    encodings/pysat_amo.py# pysat.card wrappers
    model.py              # build_cnf
    sat_solver.py         # run PySAT solvers + stats
    verify.py             # board checks and solution counting
    baselines/            # OR-Tools, PuLP, Gurobi, CPLEX
    bench.py plot.py main.py
  tests/                  # pytest suite
  results/                # raw CSV + figures (generated)
  report/                 # LaTeX paper (to be added)
  pyproject.toml requirements.txt
```

## Installation

Python 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

The last step installs the `nqueens` package (src-layout) in editable mode and
registers the `nqueens` command; without it `python -m nqueens` fails with
`No module named nqueens`. Alternatively, set `PYTHONPATH=src`.

PySAT, OR-Tools, PuLP, CBC and SCIP work out of the box. Gurobi and CPLEX need a
free academic license to lift their size limits (see below).

## Usage

Run as a module (`python -m nqueens ...`) or via the installed `nqueens` script.

```powershell
# Solve a single instance and print the board
python -m nqueens solve 8 --encoding commander --solver cadical153

# Enumerate all solutions (small n) and compare to the known count
python -m nqueens count 6 --encoding sequential

# Benchmark SAT encodings/solvers -> results/sat.csv
python -m nqueens bench --what sat --ns 8:40:2 `
    --encodings pairwise binary commander product sequential `
    --solvers glucose3 cadical153 kissat404

# Benchmark exact baselines -> results/baselines.csv
python -m nqueens bench --what baselines --ns 8:40:2 `
    --methods cpsat mip_scip mip_cbc pulp_cbc gurobi cplex_mp cplex_cp `
    --time-limit 300

# Generate figures from the CSVs
python -m nqueens plot --sat results/sat.csv --baselines results/baselines.csv `
    --outdir results/figures
```

`--ns` accepts a comma list (`8,10,12`) or a range (`8:40:2` = start:stop:step).

Check which SAT solvers work in your environment (each is tried in a child
process, so a crashing solver is reported instead of aborting):

```powershell
python -m nqueens probe
```

> **Solver notes.** SAT solving runs in an isolated subprocess, so a native
> crash or timeout is recorded as `status=crash`/`status=timeout` rather than
> killing the benchmark. On the current Windows build `kissat404` segfaults on
> N-Queens instances and `cryptosat`/`minisatgh` are not shipped in the wheel;
> the remaining solvers (CaDiCaL, Glucose, MergeSAT, MiniCard, MiniSat,
> Lingeling) work. Use `--no-isolate` only for known-good solvers.

## Metric reference

The benchmark prints one log line per run, e.g.:

```
[3/8] sat n=8 enc=sequential solver=glucose3 status=sat time=0.0016s (build=0.0008, solve=0.0008) vars=274 clauses=596 dec=54 prop=1332 conf=19
[2/4] base n=8 method=gurobi status=sat time=0.0082s vars=64 constr=42
```

**SAT fields**

| Field | Meaning |
|---|---|
| `[i/total]` | Progress: run *i* of *total* |
| `n` | Board size (n x n) |
| `enc` | AMO encoding in use (pairwise/binary/commander/product/sequential/...) |
| `solver` | SAT solver (glucose3, cadical153, ...) |
| `rep` | Repetition index (shown only when `--repeats > 1`) |
| `status` | `sat`, `unsat`, `crash` (segfault), `timeout`, or `error` |
| `time` | Total wall time = build + solve (seconds) |
| `build` | Time to **build the CNF** (encoding the puzzle into clauses) |
| `solve` | Time spent inside the **SAT solver** |
| `vars` | Boolean variables in the CNF: `n^2` original + auxiliary from encoding |
| `clauses` | Number of CNF clauses |
| `dec` | **Decisions** - solver guesses a variable value |
| `prop` | **Propagations** - unit propagation forces variable values |
| `conf` | **Conflicts** - contradictions that trigger clause learning and backtracking |
| `note` | Extra info (e.g. process exit code on crash) |

**Baseline fields**

| Field | Meaning |
|---|---|
| `method` | cpsat, mip_scip, mip_cbc, pulp_cbc, gurobi, cplex_mp, cplex_cp |
| `vars` | Model variables (n^2 binary cells) |
| `constr` | Number of constraints (rows + columns + diagonals) |
| `objective` | Objective value (0 here; N-Queens is a feasibility problem) |

**About `dec / prop / conf`.** Modern SAT solvers run CDCL: they repeatedly
*decide* (dec), *propagate* (prop) implications, and when they hit a
*conflict* (conf) they learn a new clause and backtrack. These numbers measure
the internal search effort: for the same `n`, a better encoding/solver needs
fewer `dec/prop/conf` and is therefore faster. They let you compare the quality
of AMO encodings independently of raw machine speed.

For example, `pairwise` keeps `vars = n^2` (no auxiliary variables) but produces
many `clauses`, while `sequential` adds auxiliary variables (`vars` grows) yet
uses fewer clauses - the classic trade-off between "many clauses" and
"intermediate variables".

### Giải thích chỉ số (Tiếng Việt)

**Log SAT**

| Chỉ số | Ý nghĩa |
|---|---|
| `[i/total]` | Tiến độ: lần chạy thứ *i*/tổng |
| `n` | Kích thước bàn cờ (n x n) |
| `enc` | Kiểu mã hoá AMO (pairwise/binary/commander/product/sequential/...) |
| `solver` | SAT solver (glucose3, cadical153, ...) |
| `rep` | Lần lặp thứ mấy (chỉ hiện khi `--repeats > 1`) |
| `status` | `sat` (có nghiệm), `unsat` (vô nghiệm), `crash` (segfault), `timeout`, `error` |
| `time` | Tổng thời gian = build + solve (giây) |
| `build` | Thời gian **sinh CNF** (mã hoá bài toán thành clauses) |
| `solve` | Thời gian **solver giải** CNF |
| `vars` | Số biến Boolean: `n^2` biến gốc + biến phụ do encoding sinh ra |
| `clauses` | Số mệnh đề (clause) trong CNF |
| `dec` | **Decisions** - số lần solver tự "đoán" giá trị một biến |
| `prop` | **Propagations** - số lần lan truyền đơn vị (suy ra biến bắt buộc) |
| `conf` | **Conflicts** - số lần mâu thuẫn, buộc học clause mới rồi quay lui |
| `note` | Ghi chú thêm (vd mã thoát khi crash) |

**Log baseline**

| Chỉ số | Ý nghĩa |
|---|---|
| `method` | cpsat, mip_scip, mip_cbc, pulp_cbc, gurobi, cplex_mp, cplex_cp |
| `vars` | Số biến trong mô hình (n^2 ô nhị phân) |
| `constr` | Số ràng buộc (hàng + cột + đường chéo) |
| `objective` | Giá trị hàm mục tiêu (0 ở đây; N-Queens là bài toán thoả mãn) |

**Về `dec / prop / conf`.** SAT solver hiện đại chạy theo CDCL: liên tục *quyết
định* (dec), *suy diễn* (prop), và khi vấp *mâu thuẫn* (conf) thì học clause mới
rồi quay lui. Các con số này đo "công sức tìm kiếm" nội tại: cùng một `n`,
encoding/solver càng tốt thì càng ít `dec/prop/conf` và do đó nhanh hơn - giúp
so sánh chất lượng mã hoá (AMO) tách biệt khỏi tốc độ thô của máy.



## Academic licenses (mandatory for large n)

For n up to ~100 the models exceed the size limits of the free default engines
(Gurobi ~2000 vars, CPLEX Community ~1000 vars), so full academic licenses are
required.

**Gurobi — free Academic Named-User License (1 year):**

1. Register an academic account at <https://www.gurobi.com/academics>.
2. Install Gurobi and `pip install gurobipy`.
3. Connect to the **university network** (directly or via a full-tunnel VPN),
   open the User Portal → Licenses → *Generate Now*, then run the shown
   `grbgetkey <key>` command to create `gurobi.lic`.
4. If you cannot reach the campus network, create an **Academic WLS license**
   instead (portable, usable anywhere).

   Put the resulting `gurobi.lic` in the default location
   (`%USERPROFILE%\gurobi.lic`); it holds your secret and must never be
   committed (it is already covered by `.gitignore`). WLS licenses need an
   internet connection while solving.

**CPLEX — IBM Academic Initiative (full version, free):**

1. Go to <https://www.ibm.com/academic> and log in with your university email.
2. Software → **ILOG CPLEX Optimization Studio** → download and install
   (default: `C:\Program Files\IBM\ILOG\CPLEX_Studio<VER>`).
3. `pip install cplex docplex`, then connect the pip packages to the full
   install (copies the size-unlimited runtimes into the venv):

   ```powershell
   .\.venv\Scripts\docplex.exe config --upgrade "C:\Program Files\IBM\ILOG\CPLEX_Studio222"
   ```

   Re-run this command after recreating the virtual environment.

Both `cplex_mp` (MIP) and `cplex_cp` (CP) then solve models well beyond the
1000-variable Community limit (verified at n = 50).

## Testing

```powershell
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
