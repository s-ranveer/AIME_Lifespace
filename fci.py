# This is the method for learning a causal network using FCI
from causallearn.search.ConstraintBased.FCI import fci
from causallearn.utils.GraphUtils import GraphUtils
import pandas as pd
if __name__ == "__main__":
    print("This is the method for learning a causal network using FCI")
    data = pd.read_csv("data/processed_data.csv")
    data = data.drop(columns=["id"]).dropna().astype(int)

    # Learn the causal graph using FCI
    g, _ = fci(data.to_numpy(), independence_test_method="gsq", verbose=True)

    # Rename the nodes and edges base on the data
    pdy = GraphUtils.to_pydot(g, labels=list(data.columns))

    # Plot the graph
    pdy.write_png("fci_graph.png")

    # Mapping from internal node to label name
    node_label_map = {}
    for node in pdy.get_nodes():
        name = node.get_name().strip('"')
        label = node.get_attributes().get("label", name).strip('"')
        node_label_map[name] = label

    # Extracting edges using actual labels
    pdy_edges_direct = []
    pdy_edges_weak_direct = []
    all_edges = []

    for edge in pdy.get_edges():
        ignore_edge = -1
        # We would only consider directly causal edges
        edge_ends = (edge.obj_dict["attributes"]["arrowhead"], edge.obj_dict["attributes"]["arrowtail"])
        if not (edge_ends[0] == "normal" and edge_ends[1] == "none"):
            if not (edge_ends[0] == "normal" and edge_ends[1] == "odot"):
                ignore_edge = 1
            else:
                ignore_edge = 0
        source = str(edge.get_source())
        target = str(edge.get_destination())
        source_label = node_label_map[source]
        target_label = node_label_map[target]
        if ignore_edge == -1:
            pdy_edges_direct.append((source_label, target_label))
        elif ignore_edge == 0:
            pdy_edges_weak_direct.append((source_label, target_label))
        else:
            pass
        all_edges.append((source_label, target_label, (edge_ends[1], edge_ends[0])))

    # Save the graph as a json file
    graph_json_fci1 = {
        "nodes": list(data.columns),
        "edges": pdy_edges_direct,
        "_all_edges": all_edges
    }

    graph_json_fci2 = {
        "nodes": list(data.columns),
        "edges": pdy_edges_weak_direct + pdy_edges_direct,
        "_all_edges": all_edges
    }

    print(graph_json_fci1)
    print(graph_json_fci2)