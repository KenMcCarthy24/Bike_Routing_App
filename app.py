from dash import Dash, html, callback, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import time

from default_plot_traces import get_default_fig
from street_graph import StreetGraph
from cpp_solver import solve_chinese_postman

default_bbox_north_lat = 39.864
default_bbox_south_lat = 39.856
default_bbox_east_lon = -105.034
default_bbox_west_lon = -105.052

StreetGraph()

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div("North Latitude"),
            dcc.Input(id="north_latitude_input", type="number", value=default_bbox_north_lat, step=0.001, min=-90, max=90, debounce=0.25)
        ]),
        dbc.Col([
            html.Div("South Latitude"),
            dcc.Input(id="south_latitude_input", type="number", value=default_bbox_south_lat, step=0.001, min=-90, max=90, debounce=0.25)
        ]),
        dbc.Col([
            html.Div("East Longitude"),
            dcc.Input(id="east_longitude_input", type="number", value=default_bbox_east_lon, step=0.001, min=-180, max=180, debounce=0.25)
        ]),
        dbc.Col([
            html.Div("West Longitude"),
            dcc.Input(id="west_longitude_input", type="number", value=default_bbox_west_lon, step=0.001, min=-180, max=180, debounce=0.25)
        ]),
        dbc.Col([
            html.Button("Get Raw Graph Data", id="get_data_button", n_clicks=0, style={'height': '100%'})
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=get_default_fig(default_bbox_north_lat, default_bbox_south_lat,
                                             default_bbox_east_lon, default_bbox_west_lon), id='map_plot')
        ], width=10),
        dbc.Col([
            dbc.Card([
                html.Div(id='starting_node_text', children="Starting Node: None"),
                html.Button("Clean Graph", id='data_cleaning_button', n_clicks=0)
            ]),
            dbc.Card([
                html.Div(id='selected_edge_text', children="Selected Edge: None"),
                html.Button("Remove Edge", id='remove_edge_button', n_clicks=0)
            ]),
            dbc.Card([
                html.Button("Find Best Route", id='submit_button', n_clicks=0)
            ])
        ])
    ]),
    dcc.Store(id='start_node_id'),
    dcc.Store(id='selected_edge_id'),
    dcc.Store(id='route')
])


@callback(
    Output('map_plot', 'figure'),
    Input('north_latitude_input', 'value'),
    Input('south_latitude_input', 'value'),
    Input('east_longitude_input', 'value'),
    Input('west_longitude_input', 'value'),
    State('map_plot', 'figure'),
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
    return f"Starting Node: {node_id}"


@callback(
    Output('selected_edge_text', 'children'),
    Input('selected_edge_id', 'data')
)
def update_starting_node_text(edge_id):
    return f"Selected Edge: {edge_id}"


@callback(
    Output('map_plot', 'figure', allow_duplicate=True),
    Output('start_node_id', 'data', allow_duplicate=True),
    Output('selected_edge_id', 'data', allow_duplicate=True),
    Input('get_data_button', 'n_clicks'),
    State('north_latitude_input', 'value'),
    State('south_latitude_input', 'value'),
    State('east_longitude_input', 'value'),
    State('west_longitude_input', 'value'),
    State('map_plot', 'figure'),
    prevent_initial_call=True
)
def get_graph_data_from_bbox(n_clicks, north_latitude, south_latitude, east_longitude, west_longitude, fig):
    street_graph = StreetGraph()
    street_graph.build_from_bbox(north_latitude, south_latitude, east_longitude, west_longitude)
    print(f"Successfully built graph with {street_graph.G.number_of_nodes()} Nodes and {street_graph.G.number_of_edges()} edges")

    # Reset previously selected nodes and edges
    fig["data"][5]["lat"] = []
    fig["data"][5]["lon"] = []
    fig["data"][5]["customdata"] = []

    fig["data"][7]["lat"] = []
    fig["data"][7]["lon"] = []
    fig["data"][7]["customdata"] = []

    return street_graph.modify_graph_traces(fig), None, None


@callback(
    Output('start_node_id', 'data', allow_duplicate=True),
    Output('selected_edge_id', 'data', allow_duplicate=True),
    Output('map_plot', 'figure', allow_duplicate=True),
    Input('map_plot', 'clickData'),
    State('map_plot', 'figure'),
    State('start_node_id', 'data'),
    State('selected_edge_id', 'data'),
    prevent_initial_call=True
)
def plot_click(click_data, fig, prev_node_id, prev_edge_id):
    if click_data['points'][0]['curveNumber'] == 4:
        clicked_edge_id = click_data['points'][0]['customdata']

        street_graph = StreetGraph()
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
    Output('map_plot', 'figure', allow_duplicate=True),
    Input('data_cleaning_button', 'n_clicks'),
    State('start_node_id', 'data'),
    State('map_plot', 'figure'),
    prevent_initial_call=True
)
def clean_graph(n_clicks, start_node_id, fig):
    street_graph = StreetGraph()
    street_graph.clean_graph(start_node_id)
    return street_graph.modify_graph_traces(fig)


@callback(
    Output('selected_edge_id', 'data', allow_duplicate=True),
    Output('map_plot', 'figure', allow_duplicate=True),
    Input('remove_edge_button', 'n_clicks'),
    State('selected_edge_id', 'data'),
    State('map_plot', 'figure'),
    prevent_initial_call=True
)
def delete_edge(n_clicks, edge_id, fig):
    if edge_id:
        street_graph = StreetGraph()
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
    street_graph = StreetGraph()
    start = time.time()
    best_path = solve_chinese_postman(street_graph.G, start_node_id)
    end = time.time()

    print(f"Best path found in {end-start} s ")
    print(best_path)
    return best_path


if __name__ == '__main__':
    app.run(debug=True)
