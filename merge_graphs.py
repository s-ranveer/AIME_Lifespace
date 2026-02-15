# This is the file for merging the different graphs provided by the LLMs
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
llms = ["claude", "expert", "gemini", "gpt"]
tld = Path(__file__).parent

# This is the method where we pass in the edge list to create the combined graph for the LLM
def create_graphs(llm_df: pd.DataFrame, stop_at_cycles: bool = False, threshold=4) -> pd.DataFrame:
    g = nx.DiGraph()
    meta_cols = [c for c in llm_df.columns if c not in {"X", "Y"}]
    metadata = None
    if meta_cols:
        metadata = llm_df[["X", "Y", *meta_cols]].drop_duplicates()
    for idx, row in llm_df.iterrows():
        x, y, weight = row["X"], row["Y"], row["Weight"] if "Weight" in row else None
        if weight is not None and weight > threshold:
            g.add_edge(x, y)
        # If the graph became cyclic after adding the edge, remove it
        if not nx.is_directed_acyclic_graph(g):
            g.remove_edge(x, y)
            if stop_at_cycles:
                break

    # We would get the edge lists for the graph, and save them
    nx.draw(g, with_labels=True, font_weight="bold")
    plt.show()
    edge_list = g.edges()
    edge_list_dict = {}
    edge_list_dict["X"] = [e[0] for e in edge_list]
    edge_list_dict["Y"] = [e[1] for e in edge_list]
    df = pd.DataFrame(edge_list_dict)
    if metadata is not None:
        df = df.merge(metadata, on=["X", "Y"], how="left")
    return df

if __name__ == "__main__":
    TOTAL_FILES = 5
    SORT_BY = "Weight"
    for llm in llms:
        llm_combined_df = pd.DataFrame(columns=["X", "Y", "Weight"])
        num_files = 0
        for file in os.listdir(os.path.join(tld, "graphs", llm)):
            if file.endswith(".graph"):
                num_files += 1
                edge_lists = pd.read_csv(os.path.join(tld, "graphs", llm, file))
                llm_combined_df = pd.concat([llm_combined_df, edge_lists], ignore_index=True)

        llm_combined_df = (
            llm_combined_df.groupby(["X", "Y"], as_index=False)
            .agg(Count=("Weight", "size"), Weight=("Weight", "sum"))
            .sort_values(by="Weight", ascending=False)
        )
        llm_combined_df["Weight"] = llm_combined_df["Weight"] / TOTAL_FILES

        llm_combined_df_union = create_graphs(llm_combined_df)
        os.makedirs(os.path.join(tld, "graphs", "combined"), exist_ok=True)
        llm_combined_df_union.to_csv(os.path.join(tld, "graphs", "combined", f"{llm}.graph"), index=False)

        llm_combined_df_intersection = llm_combined_df[llm_combined_df["Count"] == num_files]
        llm_combined_df_intersection = create_graphs(llm_combined_df_intersection)
        os.makedirs(os.path.join(tld, "graphs", "intersection"), exist_ok=True)
        llm_combined_df_intersection.to_csv(os.path.join(tld, "graphs", "intersection", f"{llm}.graph"), index=False)
