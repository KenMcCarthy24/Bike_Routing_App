import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

from lib.street_graph import StreetGraphManager
from ui.data_tab.data_tab_callbacks import add_data_tab_callbacks
from ui.data_tab.data_tab_layout import get_data_tab_layout
from ui.results_tab.results_tab_callbacks import add_results_tab_callbacks
from ui.results_tab.results_tab_layout import get_results_tab_layout

StreetGraphManager()

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Tabs([
        get_data_tab_layout(),
        get_results_tab_layout()
    ])
])

add_results_tab_callbacks()
add_data_tab_callbacks()

if __name__ == '__main__':
    app.run(debug=True)
