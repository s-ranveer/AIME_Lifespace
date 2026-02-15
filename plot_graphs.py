# This is the file for plotting graphs in a file
import os
import pandas as pd
from pgmpy.models import DiscreteBayesianNetwork

if __name__ == "__main__":
    graphs_dir = "graphs"
    llms = ["claude", "combined", "expert", "gemini", "gpt", "intersection"]
    for llm in llms:
        for file in os.listdir(f"{graphs_dir}/{llm}"):
            i = file.replace(".graph", "").replace("llm_", "")
            if file.endswith(".graph"):
                print("Plotting graph " + file)
                try:
                    graph = DiscreteBayesianNetwork()
                    edges = pd.read_csv(f"{graphs_dir}/{llm}/{file}")
                    for _, row in edges.iterrows():
                        graph.add_edge(row["X"], row["Y"])
                        nodes = ["educ_plwd", "educ_cg", "sex_plwd", "educ_cg", "total_burden", "community_type",
                                 "lifespace_score",
                                 "non_routine_days", "challenging_days"]
                        graph.add_nodes_from(nodes)
                    graph_gv = graph.to_graphviz()
                    save_path = "graphs"
                    os.makedirs(save_path, exist_ok=True)
                    graph_gv.draw(f"{save_path}/{llm}/llm_{i}.png", prog="dot")
                except Exception as e:
                    print(f"Error plotting graph {file}: {e}")

    print("Done!")


