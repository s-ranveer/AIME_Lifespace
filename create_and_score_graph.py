# This is the file where we would be creating and scoring the log likelihood graph
import os
import pandas as pd
import numpy as np
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from pgmpy.factors.discrete import TabularCPD
from pgmpy.metrics.metrics import log_likelihood_score
from sklearn.model_selection import StratifiedKFold


def clean_for_pgmpy(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure pgmpy-compatible discrete data."""
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    if df.empty:
        return df
    return df.astype(int)


def create_cpd(feature: str, df: pd.DataFrame) -> TabularCPD:
    counts = df[feature].value_counts(normalize=True)

    return TabularCPD(
        variable=feature,
        variable_card=len(counts),
        values=[[p] for p in counts.values],   # <-- FIXED SHAPE
        state_names={feature: counts.index.tolist()}
    )


llms_considered = ["claude", "gemini", "gpt", "expert", "combined", "intersection"]

if __name__ == "__main__":

    data = pd.read_csv("data/processed_data.csv", index_col=0)

    data_y = data["lifespace_score"]
    data_x = data.drop(columns=["lifespace_score"])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    nodes = list(data.columns)

    for llm in llms_considered:
        results_df = pd.DataFrame(
            columns=["id", "mean_log_likelihood", "total_runs_with_non_inf", "num_nodes", "num_edges"]
        )

        for file in os.listdir(f"graphs_new/{llm}"):
            if not file.endswith(".graph"):
                continue

            edges = pd.read_csv(f"graphs_new/{llm}/{file}")
            edges_list = [(row["X"], row["Y"]) for _, row in edges.iterrows()]

            scores = []

            for fold, (train_idx, test_idx) in enumerate(cv.split(data_x, data_y)):
                bn = DiscreteBayesianNetwork()
                bn.add_nodes_from(nodes)
                bn.add_edges_from(edges_list)

                train_data = data.iloc[train_idx][nodes]
                test_data = data.iloc[test_idx][nodes]

                train_data = clean_for_pgmpy(train_data)
                test_data = clean_for_pgmpy(test_data)

                # Skip degenerate folds
                if train_data.empty or test_data.empty:
                    continue

                # Fit CPDs
                bn.fit(
                    train_data,
                    estimator=BayesianEstimator,
                    prior_type="BDeu",
                    equivalent_sample_size=0.1
                )

                # Repair missing CPDs (isolated / single-state nodes)
                for node in bn.nodes:
                    if bn.get_cpds(node) is None:
                        bn.add_cpds(create_cpd(node, train_data))

                # Validate model
                try:
                    bn.check_model()
                except Exception:
                    continue

                # Score
                try:
                    score = log_likelihood_score(bn, test_data)
                    if np.isfinite(score):
                        scores.append(score)
                except Exception:
                    continue

            scores = np.array(scores)
            scores = scores[np.isfinite(scores)]

            mean_score = float(np.mean(scores)) if len(scores) else -np.inf

            results_df.loc[len(results_df)] = [
                file.replace(".graph", ""),
                mean_score,
                len(scores),
                len(nodes),
                len(edges_list),
            ]

        os.makedirs(f"metrics/{llm}", exist_ok=True)
        results_df.to_csv(f"metrics/{llm}/log_likelihoods.csv", index=False)




