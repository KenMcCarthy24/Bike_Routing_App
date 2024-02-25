from dash import html, dcc
import dash_bootstrap_components as dbc

from lib.default_bbox import default_bbox

from ui.data_tab.data_tab_figure import get_default_data_tab_figure


def get_data_tab_layout():

    selected_node_string = "Starting <br> Node"
    selected_edge_string = "Selected <br> Edge"

    tab_layout = dcc.Tab(id='data_tab', label="Data Retrieval And Cleaning", children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div("North Latitude"),
                    dcc.Input(id="north_latitude_input", type="number", value=default_bbox["north"], step=0.001,
                              min=-90, max=90, debounce=0.25)
                ]),
                dbc.Col([
                    html.Div("South Latitude"),
                    dcc.Input(id="south_latitude_input", type="number", value=default_bbox["south"], step=0.001,
                              min=-90, max=90, debounce=0.25)
                ]),
                dbc.Col([
                    html.Div("East Longitude"),
                    dcc.Input(id="east_longitude_input", type="number", value=default_bbox["east"], step=0.001,
                              min=-180, max=180, debounce=0.25)
                ]),
                dbc.Col([
                    html.Div("West Longitude"),
                    dcc.Input(id="west_longitude_input", type="number", value=default_bbox["west"], step=0.001,
                              min=-180, max=180, debounce=0.25)
                ]),
                dbc.Col([
                    html.Button("Get Raw Graph Data", id="get_data_button", n_clicks=0, style={'height': '100%'})
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=get_default_data_tab_figure(),
                              id='data_tab_map_plot',
                              style={"height": 800})
                ], width=10),
                dbc.Col([
                    dbc.Card([
                        html.Div(id='starting_node_text', children=selected_node_string),
                        html.Button("Clean Graph", id='data_cleaning_button', n_clicks=0, disabled=True)
                    ]),
                    dbc.Card([
                        html.Div(id='selected_edge_text', children=selected_edge_string),
                        html.Button("Remove Edge", id='remove_edge_button', n_clicks=0, disabled=True)
                    ]),
                    dbc.Card([
                        html.Button("Find Best Route", id='submit_button', n_clicks=0, disabled=True)
                    ])
                ])
            ]),
            dcc.Store(id='start_node_id'),
            dcc.Store(id='selected_edge_id')
        ])
    ])

    return tab_layout
