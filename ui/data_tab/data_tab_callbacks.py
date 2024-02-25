from dash import callback, Input, Output, State, html
import time

from lib.street_graph import StreetGraphManager, StreetGraph
from lib.cpp_solver import solve_chinese_postman


def add_data_tab_callbacks():
    @callback(
        Output('data_tab_map_plot', 'figure'),
        Input('north_latitude_input', 'value'),
        Input('south_latitude_input', 'value'),
        Input('east_longitude_input', 'value'),
        Input('west_longitude_input', 'value'),
        State('data_tab_map_plot', 'figure'),
        prevent_initial_call=True
    )
    def update_bbox(new_north_lat, new_south_lat, new_east_lon, new_west_lon, fig):
        fig["data"][0]['lat'] = [new_north_lat, new_north_lat]
        fig["data"][0]['lon'] = [new_west_lon, new_east_lon]

        fig["data"][1]['lat'] = [new_south_lat, new_south_lat]
        fig["data"][1]['lon'] = [new_west_lon, new_east_lon]

        fig["data"][2]['lat'] = [new_north_lat, new_south_lat]
        fig["data"][2]['lon'] = [new_east_lon, new_east_lon]

        fig["data"][3]['lat'] = [new_north_lat, new_south_lat]
        fig["data"][3]['lon'] = [new_west_lon, new_west_lon]

        return fig

    @callback(
        Output('starting_node_text', 'children'),
        Input('start_node_id', 'data')

    )
    def update_starting_node_text(node_id):
        if node_id:
            street_graph = StreetGraphManager().street_graph
            node_info = street_graph.G.nodes[node_id]
        else:
            node_info = dict(lat=None, lon=None)

        return [f"Starting Node ID: {node_id}", html.Br(), f"Latitude: {node_info['lat']}",
                html.Br(), f"Longitude: {node_info['lon']}"]

    @callback(
        Output('selected_edge_text', 'children'),
        Input('selected_edge_id', 'data')
    )
    def update_starting_node_text(edge_id):
        if edge_id:
            street_graph = StreetGraphManager().street_graph
            edge_info = street_graph.G.edges[edge_id]
        else:
            edge_info = dict(name=None, weight=None)

        return [f"Selected Edge ID: {edge_id}", html.Br(), f"Name: {edge_info['name']}",
                html.Br(), f"Length: {round(edge_info['weight'], 2) if edge_info['weight'] else None} m"]

    @callback(
        Output('data_tab_map_plot', 'figure', allow_duplicate=True),
        Output('start_node_id', 'data', allow_duplicate=True),
        Output('selected_edge_id', 'data', allow_duplicate=True),
        Output('route', 'data', allow_duplicate=True),
        Input('get_data_button', 'n_clicks'),
        State('north_latitude_input', 'value'),
        State('south_latitude_input', 'value'),
        State('east_longitude_input', 'value'),
        State('west_longitude_input', 'value'),
        State('data_tab_map_plot', 'figure'),
        prevent_initial_call=True
    )
    def get_graph_data_from_bbox(n_clicks, north_latitude, south_latitude, east_longitude, west_longitude, fig):
        StreetGraphManager().new_street_graph()
        street_graph = StreetGraphManager().street_graph
        street_graph.build_from_bbox(north_latitude, south_latitude, east_longitude, west_longitude)
        print(
            f"Successfully built graph with {street_graph.G.number_of_nodes()} Nodes and {street_graph.G.number_of_edges()} edges")

        # Reset previously selected nodes and edges
        fig["data"][5]["lat"] = []
        fig["data"][5]["lon"] = []
        fig["data"][5]["customdata"] = []

        fig["data"][7]["lat"] = []
        fig["data"][7]["lon"] = []
        fig["data"][7]["customdata"] = []

        return street_graph.modify_graph_traces(fig), None, None, None

    @callback(
        Output('data_cleaning_button', 'disabled'),
        Output('remove_edge_button', 'disabled'),
        Output('submit_button', 'disabled'),
        Input('get_data_button', 'n_clicks'),
        prevent_initial_call=True
    )
    def activate_buttons(get_data_n_clicks):
        if get_data_n_clicks > 0:
            return False, False, False

    @callback(
        Output('start_node_id', 'data', allow_duplicate=True),
        Output('selected_edge_id', 'data', allow_duplicate=True),
        Output('data_tab_map_plot', 'figure', allow_duplicate=True),
        Input('data_tab_map_plot', 'clickData'),
        State('data_tab_map_plot', 'figure'),
        State('start_node_id', 'data'),
        State('selected_edge_id', 'data'),
        prevent_initial_call=True
    )
    def plot_click(click_data, fig, prev_node_id, prev_edge_id):
        if click_data['points'][0]['curveNumber'] == 4:
            clicked_edge_id = click_data['points'][0]['customdata']

            street_graph = StreetGraphManager().street_graph
            clicked_edge_points = street_graph.G.edges[clicked_edge_id]['points']
            clicked_edge_lat = [point[1] for point in clicked_edge_points]
            clicked_edge_lon = [point[0] for point in clicked_edge_points]
            clicked_edge_ids = [clicked_edge_id for _ in clicked_edge_points]

            fig["data"][5]["lat"] = clicked_edge_lat
            fig["data"][5]["lon"] = clicked_edge_lon
            fig["data"][5]["customdata"] = clicked_edge_ids

            return prev_node_id, clicked_edge_id, fig
        elif click_data['points'][0]['curveNumber'] == 6:
            clicked_node_id = click_data['points'][0]['customdata']
            clicked_node_lat = click_data['points'][0]['lat']
            clicked_node_long = click_data['points'][0]['lon']

            fig["data"][7]["lat"] = [clicked_node_lat]
            fig["data"][7]["lon"] = [clicked_node_long]
            fig["data"][7]["customdata"] = [clicked_node_id]

            return clicked_node_id, prev_edge_id, fig
        else:
            return prev_node_id, prev_edge_id, fig

    @callback(
        Output('data_tab_map_plot', 'figure', allow_duplicate=True),
        Input('data_cleaning_button', 'n_clicks'),
        State('start_node_id', 'data'),
        State('data_tab_map_plot', 'figure'),
        prevent_initial_call=True
    )
    def clean_graph(n_clicks, start_node_id, fig):
        street_graph = StreetGraphManager().street_graph
        street_graph.clean_graph(start_node_id)
        return street_graph.modify_graph_traces(fig)

    @callback(
        Output('selected_edge_id', 'data', allow_duplicate=True),
        Output('data_tab_map_plot', 'figure', allow_duplicate=True),
        Input('remove_edge_button', 'n_clicks'),
        State('selected_edge_id', 'data'),
        State('data_tab_map_plot', 'figure'),
        prevent_initial_call=True
    )
    def delete_edge(n_clicks, edge_id, fig):
        if edge_id:
            street_graph = StreetGraphManager().street_graph
            street_graph.G.remove_edges_from([edge_id])
            street_graph.modify_graph_traces(fig)

            fig["data"][5]["lat"] = []
            fig["data"][5]["lon"] = []
            fig["data"][5]["customdata"] = []

            return None, fig
        else:
            return edge_id, fig

    @callback(
        Output('route', 'data'),
        Input('submit_button', 'n_clicks'),
        State('start_node_id', 'data'),
        prevent_initial_call=True
    )
    def solve_cpp_for_graph(n_clicks, start_node_id):
        street_graph = StreetGraphManager().street_graph
        print(f"Analyzing graph with {street_graph.G.number_of_nodes()} Nodes and {street_graph.G.number_of_edges()} edges")
        start = time.time()
        G_euler, best_path = solve_chinese_postman(street_graph.G, start_node_id)
        end = time.time()

        print(f"Best path found in {end - start} s ")
        StreetGraphManager().street_graph_euler = StreetGraph(G_euler)
        return best_path
