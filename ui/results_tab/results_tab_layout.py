from dash import html, dcc

from ui.results_tab.results_tab_figure import get_default_results_tab_figure


def get_results_tab_layout():
    tab_layout = dcc.Tab(id='results_tab', label="Results", children=[
        html.Div(children=[
            html.Div(id='results_len_text', children="", style={'fontSize': '30px', 'textAlign': 'center'}),
            dcc.Graph(figure=get_default_results_tab_figure(), id='results_tab_map_plot',
                      style={"height": "900px", "width": "100%", "margin": "auto"}),
            dcc.Store(id='route')
        ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})
    ], disabled=True)

    return tab_layout
