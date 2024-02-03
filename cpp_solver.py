import networkx as nx
from itertools import combinations


def solve_chinese_postman(G, start_node):
    """Solves the Chinese Postman Problem for a Graph G and the given starting node, finding the minimum length path
     that traverses all edges in the graph at least once and returns to the starting node."""
    G = G.copy()
    # If G is already eulerian, simply find and return the eulerian circuit of G
    if nx.is_eulerian(G):
        return list(nx.eulerian_circuit(G, source=start_node, keys=True))
    # If G is not eulerian, edges need to be duplicated to make it eulerian, while adding the least possible length
    else:
        # Find all nodes of odd degree in G
        node_degrees = G.degree
        odd_nodes = []
        for key in dict(node_degrees):
            if node_degrees[key] % 2 != 0:
                odd_nodes.append(key)

        # Create a new graph G', whose nodes are all the odd degree nodes in G
        G_prime = nx.Graph()
        for node in odd_nodes:
            G_prime.add_node(node)

        # Find the shortest path between all possible pairs of nodes in G'.
        # Add edges to G' representing these paths, with weights
        # representing the length of the shortest paths
        for u, v in list(combinations(odd_nodes, 2)):
            shortest_path = nx.shortest_path(G, u, v, "weight")
            shortest_path_length = nx.shortest_path_length(G, u, v, "weight")

            G_prime.add_edge(u, v, weight=shortest_path_length, path=shortest_path)

        # Find the minimal weight matching of nodes in G', representing the paths that need to be added to G.
        min_matching = nx.min_weight_matching(G_prime, "weight")

        # Duplicate all edges in G represented by the edges in the minimal weight matching in G'. If there are already
        # multiple edges in G between to nodes, duplicate the one with the lowest length
        for matching_nodes in min_matching:
            matching_path = G_prime.get_edge_data(*matching_nodes)["path"]

            for i in range(len(matching_path) - 1):
                min_weight_edge_metadata = min(G.get_edge_data(matching_path[i], matching_path[i + 1]).values(),
                                               key=lambda x: x['weight'])

                G.add_edge(matching_path[i], matching_path[i + 1], **min_weight_edge_metadata)

        # Now G should be Eulerian and an Eulerian path can be found
        return list(nx.eulerian_circuit(G, source=start_node, keys=True))