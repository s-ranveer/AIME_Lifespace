from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2, fisher_exact
from pgmpy.models import BayesianNetwork

# CONFIG
DATA_CSV_PATH = "lifespace_data.csv"

# Folder containing edge CSVs (one DAG per file)
GRAPHS_DIR = os.path.join(os.path.dirname(__file__), "graphs")

# Folder where results will be written
OUTPUT_DIR = "ci_results"       
OUTPUT_ROOT = os.path.join(os.path.dirname(__file__), OUTPUT_DIR)

MAX_COND_SET = 1

RUN_GTEST = True

ALPHA = 0.05

# Data structures
@dataclass(frozen=True)
class CI:
    x: str
    y: str
    z: Tuple[str, ...]

    def label(self) -> str:
        return f"{self.x} independent of {self.y} | {list(self.z)}"

# I/O helpers
def read_edges(edges_csv_path: str) -> List[Tuple[str, str]]:
    df = pd.read_csv(edges_csv_path)
    candidates = [
        ("source", "target"),
        ("from", "to"),
        ("parent", "child"),
        ("u", "v"),
        ("src", "dst"),
        ("X", "Y"),
    ]
    for a, b in candidates:
        if a in df.columns and b in df.columns:
            return [(str(u), str(v)) for u, v in zip(df[a], df[b])]

    if df.shape[1] >= 2:
        a, b = df.columns[:2]
        return [(str(u), str(v)) for u, v in zip(df[a], df[b])]

    raise ValueError("Edges CSV must have at least 2 columns (Example: source,target).")

def read_data(data_csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(data_csv_path)
    for c in df.columns:
        if df[c].dtype == bool:
            df[c] = df[c].astype(int)
        df[c] = df[c].astype("category")
    return df

# DAG -> implied conditional independencies
def dag_to_implied_cis(edges: Sequence[Tuple[str, str]], max_cond_set: int) -> List[CI]:
    model = BayesianNetwork(list(edges))
    indeps = model.get_independencies()

    cis: List[CI] = []
    for assertion in indeps.get_assertions():
        Xs, Ys, Zs = assertion.event1, assertion.event2, assertion.event3

        Xs = list(Xs) if isinstance(Xs, (set, frozenset, list, tuple)) else [Xs]
        Ys = list(Ys) if isinstance(Ys, (set, frozenset, list, tuple)) else [Ys]
        Zs = list(Zs) if isinstance(Zs, (set, frozenset, list, tuple)) else [Zs]

        Zs = [z for z in Zs if z is not None]
        if len(Zs) > max_cond_set:
            continue

        zt = tuple(sorted(map(str, Zs)))

        for x in Xs:
            for y in Ys:
                x, y = str(x), str(y)
                if x == y:
                    continue
                a, b = sorted([x, y])
                cis.append(CI(a, b, zt))

    cis = sorted(set(cis), key=lambda ci: (ci.x, ci.y, ci.z))
    return cis

# Statistical tests
def _g_stat_from_table(obs: np.ndarray) -> Tuple[float, int]:
    obs = np.asarray(obs, dtype=float)
    rsum = obs.sum(axis=1)
    csum = obs.sum(axis=0)
    obs = obs[np.ix_(rsum > 0, csum > 0)]

    r, c = obs.shape
    if r < 2 or c < 2:
        return 0.0, 0

    n = obs.sum()
    row = obs.sum(axis=1, keepdims=True)
    col = obs.sum(axis=0, keepdims=True)
    exp = (row @ col) / n

    mask = obs > 0
    G = 2.0 * np.sum(obs[mask] * np.log(obs[mask] / exp[mask]))
    dof = (r - 1) * (c - 1)
    return float(G), int(dof)

def g_test_conditional(df: pd.DataFrame, x: str, y: str, z: Sequence[str]) -> Dict[str, Any]:
    cols = [x, y] + list(z)
    d = df[cols].dropna().copy()

    if len(z) == 0:
        ct = pd.crosstab(d[x], d[y], dropna=False)
        G, dof = _g_stat_from_table(ct.to_numpy())
        p = 1.0 - chi2.cdf(G, dof) if dof > 0 else 1.0
        return {"test": "g_test", "G": G, "dof": dof, "p_value": p, "n": int(ct.values.sum()), "strata": 1}

    G_total, dof_total, n_total, strata = 0.0, 0, 0, 0
    for _, sub in d.groupby(list(z), observed=True):
        ct = pd.crosstab(sub[x], sub[y], dropna=False)
        G, dof = _g_stat_from_table(ct.to_numpy())
        G_total += G
        dof_total += dof
        n_total += int(ct.values.sum())
        strata += 1

    p = 1.0 - chi2.cdf(G_total, dof_total) if dof_total > 0 else 1.0
    return {"test": "g_test", "G": G_total, "dof": dof_total, "p_value": p, "n": n_total, "strata": strata}


def fisher_unconditional_2x2(df: pd.DataFrame, x: str, y: str) -> Optional[Dict[str, Any]]:
    d = df[[x, y]].dropna()
    ct = pd.crosstab(d[x], d[y], dropna=False)
    if ct.shape != (2, 2):
        return None
    oddsratio, p = fisher_exact(ct.to_numpy(), alternative="two-sided")
    return {"test": "fisher_exact", "oddsratio": float(oddsratio), "p_value": float(p), "n": int(ct.values.sum())}

def build_ci_universe(vars_: Sequence[str], max_cond_set: int) -> List[CI]:
    """
    Universe U of CI statements over vars_ with |Z| <= max_cond_set.
    Currently supports max_cond_set=0 or 1 (extendable).
    """
    vars_sorted = sorted(map(str, vars_))
    cis: List[CI] = []

    for i in range(len(vars_sorted)):
        for j in range(i + 1, len(vars_sorted)):
            x, y = vars_sorted[i], vars_sorted[j]

            # Z = empty
            cis.append(CI(x, y, ()))

            if max_cond_set >= 1:
                for z in vars_sorted:
                    if z != x and z != y:
                        cis.append(CI(x, y, (z,)))

            # If we later want MAX_COND_SET > 1, we can extend here with combinations.

    return sorted(set(cis), key=lambda ci: (ci.x, ci.y, ci.z))

def ci_p_value_current_test(df: pd.DataFrame, ci: CI) -> float:
    """
    Return ONE p-value for CI using the currently enabled test.
    """
    if RUN_GTEST:
        return float(g_test_conditional(df, ci.x, ci.y, ci.z)["p_value"])
    
    raise RuntimeError("Enable at least one CI test for confusion matrix.")

# Run one graph 
def run_one_graph(edges_path: Path, df: pd.DataFrame, out_dir: Path) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)

    edges = read_edges(str(edges_path))

    # Sanity check: DAG variables must exist in dataset
    dag_nodes = sorted(set([u for u, v in edges] + [v for u, v in edges]))
    missing = [v for v in dag_nodes if v not in df.columns]
    if missing:
        raise ValueError(f"[{edges_path.name}] DAG vars missing from data: {missing}")

    implied_cis = dag_to_implied_cis(edges, max_cond_set=MAX_COND_SET)

    # CI-level confusion matrix over universe U (|Z| <= MAX_COND_SET)
    # Predicted positive  = CI implied by DAG (model predicts independence)
    # Predicted negative  = CI not implied by DAG
    # Actual positive     = data does not reject independence  (p_value >= ALPHA)
    # Actual negative     = data rejects independence   (p_value <  ALPHA)

    U = build_ci_universe(dag_nodes, MAX_COND_SET)
    implied_set = set(implied_cis)

    TP = FP = FN = TN = 0
    cm_rows: List[Dict[str, Any]] = []

    p_values = {}

    for ci in U:
        predicted_independent = (ci in implied_set)
        p_val = ci_p_value_current_test(df, ci)
        if not np.isfinite(p_val):
            continue  # skip untestable cases
        actual_not_rejected_by_data = (p_val >= ALPHA)

        if predicted_independent and actual_not_rejected_by_data:
            TP += 1
            bucket = "TP"
        elif predicted_independent and (not actual_not_rejected_by_data):
            FP += 1
            bucket = "FP"
        elif (not predicted_independent) and actual_not_rejected_by_data:
            FN += 1
            bucket = "FN"
        else:
            TN += 1
            bucket = "TN"

        cm_rows.append({
            "x": ci.x,
            "y": ci.y,
            "z": ",".join(ci.z),
            "ci": ci.label(),
            "predicted_independent": predicted_independent,
            "actual_not_rejected_by_data": actual_not_rejected_by_data,
            "p_value": p_val,
            "confusion_bucket": bucket,
        })
        p_values[ci] = p_val

    precision = TP / (TP + FP) if (TP + FP) > 0 else float("nan")
    fpr = FP / (FP + TN) if (FP + TN) > 0 else float("nan")
    npv = TN / (TN + FN) if (TN + FN) > 0 else float("nan")

    # Build detailed results for each graph
    n_satisfied = sum(
        1 for ci in implied_set
        if ci in p_values and p_values[ci] >= ALPHA
    )

    n_not_satisfied = sum(
        1 for ci in implied_set
        if ci in p_values and p_values[ci] < ALPHA
    )

    # Return counts for global summary across graphs
    return {
        "graph_file": edges_path.name,
        "n_implied": int(len(implied_cis)),
        "n_satisfied": n_satisfied,
        "n_not_satisfied":n_not_satisfied,
        "alpha": float(ALPHA),

        # CI confusion matrix based metrics
        "U_size": int(len(U)),
        "TP_CI": int(TP),
        "FP_CI": int(FP),
        "TN_CI": int(TN),
        "FN_CI": int(FN),
        "precision_CI": float(precision),
        "false_positive_rate_CI": float(fpr),
        "negative_predictive_value_CI": float(npv),
    }

# Main: run all graphs in folder
def main() -> None:
    graphs_dir = Path(GRAPHS_DIR)
    out_root = Path(OUTPUT_ROOT)
    out_root.mkdir(parents=True, exist_ok=True)

    df_main = read_data(DATA_CSV_PATH)
    df = df_main.dropna().reset_index(drop=True)

    edge_files = sorted([p for p in graphs_dir.iterdir() if p.is_file() and p.suffix.lower() == ".csv"])
    if not edge_files:
        raise ValueError(f"No .csv edge files found in {graphs_dir.resolve()}")

    summary_rows: List[Dict[str, Any]] = []
    for edges_path in edge_files:
        graph_name = edges_path.stem  # file name without .csv
        out_dir = out_root / graph_name
        counts = run_one_graph(edges_path, df, out_dir)
        summary_rows.append(counts)

        print(f"[{graph_name}] implied={counts['n_implied']} satisfied={counts['n_satisfied']} not_satisfied={counts['n_not_satisfied']}")

    summary = pd.DataFrame(summary_rows)

    # Add violation and satisfaction rates
    summary["violation_rate"] = np.where(
        summary["n_implied"] > 0,
        summary["n_not_satisfied"] / summary["n_implied"],
        np.nan
    )
    summary["satisfaction_rate"] = np.where(
        summary["n_implied"] > 0,
        summary["n_satisfied"] / summary["n_implied"],
        np.nan
    )

    # sort by violation rate (best first)
    summary = summary.sort_values(
        ["violation_rate", "n_implied"],
        ascending=[True, False]
    )

    # Rename confusion matrix columns and metrics for clarity in the summary
    summary = summary.rename(columns={
        "n_implied": "Total Model-Implied C.Is",
        "TP_CI": "Model-Implied CIs & Not Rejected by Data",
        "FP_CI": "Model-Implied CIs & Rejected by Data",
        "TN_CI": "Model-Not-Implied CIs & Rejected by Data",
        "FN_CI": "Model-Not-Implied CIs & Not Rejected by Data",
        "precision_CI": "Precision",
        "false_positive_rate_CI": "False Positive Rate",
        "negative_predictive_value_CI": "Negative Predictive Value",
    })

    summary.to_csv(out_root / "summary_across_graphs.csv", index=False, float_format="%.2f")

    # Metrics by model (rows = models, columns = metrics)
    metrics_by_model = (
        summary[[
            "graph_file",
            "Total Model-Implied C.Is",
            "Precision",
            "False Positive Rate",
            "Negative Predictive Value",
        ]]
        .rename(columns={"graph_file": "model"})
        .set_index("model")
        .sort_index()
    )

    metrics_by_model.to_csv(
        out_root / "metrics_by_model.csv",
        float_format="%.2f"
    )

    print(f"Saved metrics-by-model table to: {out_root / 'metrics_by_model.csv'}")

    print(f"\nSaved global summary to: {out_root / 'summary_across_graphs.csv'}")

if __name__ == "__main__":
    main()
