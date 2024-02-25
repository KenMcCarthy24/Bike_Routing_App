import numpy as np

from dash import callback, Input, Output, State

from lib.street_graph import StreetGraphManager


def add_results_tab_callbacks():
    @callback(
        Output('results_tab', 'disabled'),
        Input('route', 'data')
    )
    def change_results_tab_state(route):
        return route is None

    @callback(
        Output("results_tab_map_plot", "figure"),
        Output('results_len_text', "children"),
        Input('route', 'data'),
        State("results_tab_map_plot", "figure"),
        State('start_node_id', 'data'),
        prevent_initial_call=True
    )
    def plot_results(route, fig, start_node_id):
        if route:
            # Reset Plot
            fig['data'][0]['lon'] = []
            fig['data'][0]['lat'] = []
            fig['data'][1]['lon'] = []
            fig['data'][1]['lat'] = []
            fig['data'][2]['lon'] = []
            fig['data'][2]['lat'] = []
            fig['data'][3]['lon'] = []
            fig['data'][3]['lat'] = []
            fig['data'][4]['lon'] = []
            fig['data'][4]['lat'] = []
            fig['data'][4]['text'] = []

            street_graph = StreetGraphManager().street_graph_euler
            node_ids = street_graph.G.nodes
            fig['data'][0]['lon'] = [street_graph.G.nodes[node_id]['lon'] for node_id in node_ids]
            fig['data'][0]['lat'] = [street_graph.G.nodes[node_id]['lat'] for node_id in node_ids]

            fig['data'][1]['lon'] = [street_graph.G.nodes[start_node_id]['lon']]
            fig['data'][1]['lat'] = [street_graph.G.nodes[start_node_id]['lat']]

            fig['layout']['mapbox']['center']['lon'] = np.mean(fig['data'][0]['lon'])
            fig['layout']['mapbox']['center']['lat'] = np.mean(fig['data'][0]['lat'])

            arrow_indices = []
            text_label_dict = {}
            path_length = 0
            for i in range(len(route)):
                edge_number = i + 1
                edge_id = route[i]
                edge = street_graph.G.edges[edge_id]
                edge_points = edge['points']
                middle_point = tuple(edge_points[int(len(edge_points) / 2)])

                if middle_point not in text_label_dict.keys():
                    text_label_dict[middle_point] = [edge_number]
                else:
                    text_label_dict[middle_point].append(edge_number)

                start_node = street_graph.G.nodes[edge_id[0]]
                if (start_node['lon'], start_node['lat']) == edge_points[-1]:
                    edge_points = edge_points[::-1]

                edge_lat = [edge_points[j][1] for j in range(len(edge_points))]
                edge_lon = [edge_points[j][0] for j in range(len(edge_points))]

                fig['data'][2]['lon'].extend(edge_lon + [None])
                fig['data'][2]['lat'].extend(edge_lat + [None])

                arrow_indices.append(len(fig['data'][2]['lon']) - 2)

                path_length += edge["weight"]

            # Arrows
            arrow_head_width = 0.00008
            arrow_head_angle = np.pi / 6

            rotation_matrix_ccw = np.array([[np.cos(arrow_head_angle), -np.sin(arrow_head_angle)],
                                            [np.sin(arrow_head_angle), np.cos(arrow_head_angle)]])

            rotation_matrix_cw = np.array([[np.cos(arrow_head_angle), np.sin(arrow_head_angle)],
                                           [-np.sin(arrow_head_angle), np.cos(arrow_head_angle)]])

            A = np.array([[fig['data'][2]['lon'][idx] for idx in arrow_indices],
                          [fig['data'][2]['lat'][idx] for idx in arrow_indices]])
            B = np.array([[fig['data'][2]['lon'][idx - 1] for idx in arrow_indices],
                          [fig['data'][2]['lat'][idx - 1] for idx in arrow_indices]])

            V = B - A
            V_norm = V / np.linalg.norm(V, axis=0)

            ccw_arrow_points = A + arrow_head_width * (rotation_matrix_ccw @ V_norm)
            cw_arrow_points = A + arrow_head_width * (rotation_matrix_cw @ V_norm)

            for j in range(len(arrow_indices)):
                fig['data'][3]['lon'].extend([ccw_arrow_points[0][j], A[0][j], cw_arrow_points[0][j]] + [None])
                fig['data'][3]['lat'].extend([ccw_arrow_points[1][j], A[1][j], cw_arrow_points[1][j]] + [None])

            # Text
            for key in text_label_dict.keys():
                fig['data'][4]['lon'].append(key[0])
                fig['data'][4]['lat'].append(key[1])
                fig['data'][4]['text'].append(', '.join([str(x) for x in text_label_dict[key]]))

            path_length_km = path_length / 1000
            path_length_mi = path_length_km / 1.60934

            path_length_text = f"Minimum Path Length = {round(path_length_km, 2)} km ({round(path_length_mi, 2)} mi)"
        else:
            path_length_text = ""

        return fig, path_length_text
