import pandas as pd
import networkx as nx
import numpy as np
from scipy.spatial import Delaunay

from lib.cpp_solver import solve_chinese_postman

import time

def generate_random_planar_graph(n_nodes, n_edges):
    node_points = np.random.random_sample((n_nodes, 2))
    tri = Delaunay(node_points)

    edges = set()
    for simplex in tri.simplices:
        edges.add(tuple(sorted([simplex[0], simplex[1]])))
        edges.add(tuple(sorted([simplex[1], simplex[2]])))
        edges.add(tuple(sorted([simplex[2], simplex[0]])))
    edges_list = list(edges)

    G = nx.Graph()
    for i in range(len(node_points)):
        G.add_node(i, x=node_points[i][0], y=node_points[i][1])

    for i in range(len(edges_list)):
        start_node_idx = edges_list[i][0]
        end_node_idx = edges_list[i][1]

        weight = np.sqrt((G.nodes[start_node_idx]['x'] - G.nodes[end_node_idx]['x']) ** 2 + (
                    G.nodes[start_node_idx]['y'] - G.nodes[end_node_idx]['y']) ** 2)

        G.add_edge(start_node_idx, end_node_idx, weight=weight)

    if len(G.edges) == n_edges:
        G = nx.MultiGraph(G)
    elif len(G.edges) < n_edges:
        G = nx.MultiGraph(G)

        n_edges_to_add = n_edges - len(G.edges)
        edge_idxs_to_duplicate = np.random.choice(list(range(len(G.edges))), n_edges_to_add)

        for i in edge_idxs_to_duplicate:
            edge_id_to_duplicate = list(G.edges)[i]
            edge_weight_to_duplicate = G.edges[edge_id_to_duplicate]["weight"]
            G.add_edge(edge_id_to_duplicate[0], edge_id_to_duplicate[1], weight=edge_weight_to_duplicate)
    else:
        n_edges_to_remove = len(G.edges) - n_edges
        for _ in range(n_edges_to_remove):
            # Find non-bridge edges that won't isolate a node
            bridges = np.array(list(nx.bridges(G)), dtype=object)
            if len(bridges) == 0:
                candidates = list(G.edges)
            else:
                candidates = [edge for edge in G.edges if not edge in bridges]

            # If removing any non-bridge edge would still isolate a node, check if there are any candidates left
            if not candidates:
                # If no suitable candidates, raise an exception
                raise Exception("No suitable edge to remove")

            # Choose a random edge from the candidates to remove
            edge_to_remove = candidates[np.random.choice(len(candidates))]

            G.remove_edge(*edge_to_remove)

        G = nx.MultiGraph(G)

    return G


if __name__ == '__main__':
    n_trials_per_graph_size = 10
    n_nodes_to_analyze = np.array([130])
    # n_nodes_to_analyze = np.arange(105, 135, 5)

    results_df = pd.DataFrame(columns=["N Nodes", "N Edges", "Trial Number", "Runtime"])

    count = 0
    for n_nodes in n_nodes_to_analyze:
        n_edges_high = int((n_nodes / 0.6) + 2)
        n_edges_low = n_nodes - 1

        n_edges_to_analyze = np.arange(n_edges_low, n_edges_high + 1, 1)

        for n_edges in n_edges_to_analyze:
            trial_number = 0
            failed_attempts = 0
            while trial_number < n_trials_per_graph_size and failed_attempts < 30:
                try:
                    G = generate_random_planar_graph(n_nodes, n_edges)

                    if nx.is_eulerian(G):
                        continue

                    start = time.time()
                    _ = solve_chinese_postman(G, 0)
                    end = time.time()
                    runtime = end - start

                    print(n_nodes, n_edges, trial_number)
                    results_df.loc[len(results_df.index)] = [n_nodes, n_edges, trial_number, runtime]
                    trial_number += 1
                except Exception as e:
                    failed_attempts += 1
                    continue

    out_path = "./runtime_results3.csv"
    results_df.to_csv(out_path)


