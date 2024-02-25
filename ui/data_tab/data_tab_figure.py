import plotly.graph_objs as go

from lib.default_bbox import default_bbox


def get_default_data_tab_figure():
    layout = go.Layout(
        mapbox=dict(
            style='open-street-map',
            zoom=14,
            center=dict(lat=(default_bbox["north"] + default_bbox["south"])/2,
                        lon=(default_bbox["east"] + default_bbox["west"])/2)
        ),
        autosize=True,
        showlegend=False
    )

    fig = go.Figure(layout=layout)

    # Index 0: north_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox["north"], default_bbox["north"]],
                                   lon=[default_bbox["west"], default_bbox["east"]],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='north_bbox'))

    # Index 1: south_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox["south"], default_bbox["south"]],
                                   lon=[default_bbox["west"], default_bbox["east"]],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='south_bbox'))

    # Index 2: east_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox["north"], default_bbox["south"]],
                                   lon=[default_bbox["east"], default_bbox["east"]],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='east_bbox'))

    # Index 3: west_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox["north"], default_bbox["south"]],
                                   lon=[default_bbox["west"], default_bbox["west"]],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='west_bbox'))

    # Index 4: edges
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='lines', line=dict(color='red'), name='edges'))

    # Index 5: selected edge
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='lines', line=dict(color='blue', width=5),
                                   name='selected_edge'))

    # Index 6: nodes
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='markers', marker=dict(color='red', size=10),
                                   name='nodes'))

    # Index 7: selected node
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='markers', marker=dict(color='blue', size=20),
                                   name='selected_node'))

    return fig