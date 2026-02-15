import os
import pandas as pd
from pathlib import Path

from pgmpy.factors.discrete import TabularCPD

from structure_learning_subtractive import refine_bn, StructuredBicScore
from pgmpy.readwrite import BIFWriter
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator, BIC

tld = Path(__file__).parent.parent
data_path = os.path.join(tld, "data", "processed_data.csv")
results_path = os.path.join(tld, "refinement", "results", "combined")
initial_edges_path = os.path.join(tld, "graphs", "combined")
"""
You may need to change some part of the pgmpy library. The BayesianEstimator would not work as expected in case of a 
graph without any edge. The BayesianEstimator initialization may need to be modified for the code to work
"""
def create_cpd(feature, df):
    counts = df[feature].value_counts(normalize=True)

    return TabularCPD(
        variable=feature,
        variable_card=len(counts),
        values=[[p] for p in counts.values],  # <-- column shape
        state_names={feature: counts.index.tolist()}
    )


if __name__ == "__main__":
    os.makedirs(results_path, exist_ok=True)
    os.makedirs(os.path.join(results_path, "llm"), exist_ok=True)
    os.makedirs(os.path.join(results_path, "llm", "subtractive"), exist_ok=True)
    for llm_edges_file in os.listdir(initial_edges_path):
        if llm_edges_file.endswith(".graph"):
            llm = llm_edges_file.split(".")[0]
            print("Considering the LLM edges from", llm)
            initial_edges_df = pd.read_csv(os.path.join(initial_edges_path, llm_edges_file))

            data = pd.read_csv(data_path).dropna().astype(int)
            data = data.drop(columns={"id"})
            print("\nProcessing the original data")

            # Load the black list df for the domain
            black_list_df = pd.read_csv(os.path.join(tld, "refinement", "blacklists.csv"))
            black_list = []
            for i, row in black_list_df.iterrows():
                if (row.X not in data.columns) or (row.Y not in data.columns):
                    print(f"Edge {(row.X, row.Y)} contains an unknown node. Skipping.")
                else:
                    black_list.append((row.X, row.Y))
            print(f"Loaded {len(black_list)} edges as black list.")


            edges = []
            for _, row in initial_edges_df.iterrows():
                if (row.X not in data.columns) or (row.Y not in data.columns):
                    print(f"Edge {(row.X, row.Y)} contains an unknown node. Skipping.")
                else:
                    if not (row.X, row.Y) in black_list:
                        edges.append((row.X, row.Y))
            print(f"Loaded {len(edges)} edges.")

            M0 = DiscreteBayesianNetwork()
            M0.add_nodes_from(data.columns)
            M0.add_edges_from(edges)

            state_names = {col: list(range(2)) for col in data.columns}

            M1 = refine_bn(M0.copy(), data, state_names, scoring_method=BIC(data, state_names=state_names),
                           tabu_length=0, black_list=black_list, subtractive_refinement_only=True)
            M1.fit(data, state_names=state_names, estimator=BayesianEstimator, prior_type="BDeu",
                   equivalent_sample_size=0.1)

            for node in M1.nodes:
                if M1.get_cpds(node) is None:
                    cpd = create_cpd(node, data)
                    M1.add_cpds(cpd)
            BIFWriter(M1).write_bif(os.path.join(results_path,
                                                 "llm", "subtractive",  f"{llm}-1.bif"))

            scorer = StructuredBicScore(data, state_names=state_names)
            M2 = refine_bn(M0.copy(), data, state_names=state_names, scoring_method=scorer, tabu_length=0,
                           black_list=black_list,
                           subtractive_refinement_only=True)
            cpds = []
            for node in M2.nodes:
                parents = M2.get_parents(node)
                _, cpd = scorer.local_score(node, parents, return_cpd=True)
                cpd.normalize()
                cpds.append(cpd)
            M2.add_cpds(*cpds)
            BIFWriter(M2).write_bif(os.path.join(results_path,
                                                 "llm", "subtractive", f"{llm}-2.bif"))