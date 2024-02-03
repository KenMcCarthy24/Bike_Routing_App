from singleton import Singleton
import osmnx as ox
import networkx as nx
import pandas as pd


class StreetGraph(metaclass=Singleton):
    def __init__(self):
        self.G = None

    def build_from_bbox(self, north_lat_bound, south_lat_bound, west_lon_bound, east_lon_bound):
        nodes, edges = ox.utils_graph.graph_to_gdfs(
            ox.utils_graph.get_undirected(
                ox.graph_from_bbox(north=north_lat_bound, south=south_lat_bound,
                                   east=east_lon_bound, west=west_lon_bound,
                                   network_type="bike", retain_all=True)))

        graph = nx.MultiGraph()
        for i in range(len(nodes)):
            graph.add_node(nodes.index[i], lat=nodes.y.iloc[i], lon=nodes.x.iloc[i])

        for i in range(len(edges)):
            edge_id = edges.index[i]
            edge_info = edges.loc[edge_id]

            if isinstance(edge_info['name'], list):
                edge_info['name'] = edge_info['name'][0]

            edge_points = [point for point in edge_info.geometry.coords]

            if len(edge_info.geometry.coords) == 2:
                middle_lat = (edge_points[0][1] + edge_points[1][1]) / 2
                middle_lon = (edge_points[0][0] + edge_points[1][0]) / 2
                edge_points.insert(1, (middle_lon, middle_lat))

            if (graph.nodes[edge_id[0]]['lon'], graph.nodes[edge_id[0]]['lat']) == edge_points[-1]:
                edge_points = edge_points[::-1]

            graph.add_edge(edge_id[0], edge_id[1], name=edge_info["name"], weight=edge_info["length"],
                           points=edge_points)

        self.G = graph

    def clean_graph(self, starting_node):
        self.remove_nan_streets()
        self.remove_disconnected_nodes_and_edges(starting_node)
        self.clean_up_nodes()

    def remove_nan_streets(self):
        nan_streets_ids = []
        for edge in self.G.edges:
            if pd.isna(self.G.edges[edge]["name"]):
                nan_streets_ids.append(edge)

        self.G.remove_edges_from(nan_streets_ids)

    def remove_disconnected_nodes_and_edges(self, starting_node):
        """Graph cleaning method to remove all nodes and edges not reachable from starting_node
         using a Depth First Search (DFS)"""
        # Initialize sets to keep track of nodes and edges found with DFS
        dfs_nodes = set()
        dfs_edges = set()

        # Run DFS to find all edges reachable from starting_node.
        for edge in nx.edge_dfs(self.G, starting_node):
            dfs_edges.add(edge)
            # Add copy of edge directed other direction to make sure both directions are in set
            dfs_edges.add((edge[1], edge[0], edge[2]))

        # Extract node ids from the edges found in the DFS
        for edge in dfs_edges:
            dfs_nodes.add(edge[0])
            dfs_nodes.add(edge[1])

        # Get set of nodes that weren't visited by the DFS
        unvisited_nodes = set(self.G.nodes) - dfs_nodes
        unvisited_edges = set(self.G.edges) - dfs_edges

        # Remove unvisited nodes from the graph
        self.G.remove_nodes_from(unvisited_nodes)
        self.G.remove_edges_from(unvisited_edges)

    def clean_up_nodes(self):
        for node_id in list(self.G.nodes):
            node_edges = list(self.G.edges(node_id, keys=True))
            if len(node_edges) == 2:
                edge1_id = node_edges[0]
                edge1_info = self.G.edges[edge1_id]
                edge2_id = node_edges[1]
                edge2_info = self.G.edges[edge2_id]

                # Make sure graph points are correctly going from first node to second node
                if (self.G.nodes[edge1_id[0]]['lon'], self.G.nodes[edge1_id[0]]['lat']) == edge1_info["points"][-1]:
                    edge1_info["points"] = edge1_info["points"][::-1]

                if (self.G.nodes[edge2_id[0]]['lon'], self.G.nodes[edge2_id[0]]['lat']) == edge2_info["points"][-1]:
                    edge2_info["points"] = edge2_info["points"][::-1]

                if edge1_info["name"] == edge2_info["name"]:
                    new_edge_name = edge1_info["name"]
                    new_edge_weight = edge1_info["weight"] + edge2_info["weight"]

                    if edge1_id[0] == node_id and edge2_id[0] == node_id:
                        new_start_id, new_end_id = edge1_id[1], edge2_id[1]
                        new_points = edge1_info['points'][::-1] + edge2_info['points'][1:]

                    elif edge1_id[0] == node_id and edge2_id[1] == node_id:
                        new_start_id, new_end_id = edge1_id[1], edge2_id[0]
                        new_points = edge1_info['points'][::-1] + edge2_info['points'][::-1][1:]

                    elif edge1_id[1] == node_id and edge2_id[0] == node_id:
                        new_start_id, new_end_id = edge1_id[0], edge2_id[1]
                        new_points = edge1_info['points'] + edge2_info['points'][1:]

                    elif edge1_id[1] == node_id and edge2_id[1] == node_id:
                        new_start_id, new_end_id = edge1_id[0], edge2_id[0]
                        new_points = edge1_info['points'] + edge2_info['points'][::-1][1:]

                    self.G.add_edge(new_start_id, new_end_id, name=new_edge_name, weight=new_edge_weight,
                                    points=new_points)

                    self.G.remove_nodes_from([node_id])
                    self.G.remove_edges_from(node_edges)

    def modify_graph_traces(self, fig):
        # Make Nodes Trace
        node_lat, node_lon, node_ids = [], [], []
        for node_id in self.G.nodes:
            node_lat.append(self.G.nodes[node_id]['lat'])
            node_lon.append(self.G.nodes[node_id]['lon'])
            node_ids.append(node_id)

        fig["data"][6]['lat'] = node_lat
        fig["data"][6]['lon'] = node_lon
        fig["data"][6]['customdata'] = node_ids

        # Make Edge Traces
        fig["data"][4]['lat'] = []
        fig["data"][4]['lon'] = []
        fig["data"][4]['customdata'] = []
        for edge_id in self.G.edges:
            edge = self.G.edges[edge_id]
            edge_lat = [edge['points'][i][1] for i in range(len(edge['points']))]
            edge_lon = [edge['points'][i][0] for i in range(len(edge['points']))]
            edge_ids = [edge_id for _ in range(len(edge['points']))]

            fig["data"][4]['lat'].extend(edge_lat + [None])
            fig["data"][4]['lon'].extend(edge_lon + [None])
            fig["data"][4]['customdata'].extend(edge_ids + [None])

        return fig
