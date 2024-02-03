import plotly.graph_objs as go


def get_default_fig(default_bbox_north_lat, default_bbox_south_lat,
                    default_bbox_east_lon, default_bbox_west_lon):
    layout = go.Layout(
        mapbox=dict(
            style='open-street-map',
            zoom=14,  # Zoom level
            center=dict(lat=(default_bbox_north_lat + default_bbox_south_lat)/2,
                        lon=(default_bbox_east_lon + default_bbox_west_lon)/2)
        ),
        height=800,
        showlegend=False
    )

    fig = go.Figure(layout=layout)

    # Index 0: north_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox_north_lat, default_bbox_north_lat],
                                   lon=[default_bbox_west_lon, default_bbox_east_lon],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='north_bbox'))

    # Index 1: south_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox_south_lat, default_bbox_south_lat],
                                   lon=[default_bbox_west_lon, default_bbox_east_lon],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='south_bbox'))

    # Index 2: east_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox_north_lat, default_bbox_south_lat],
                                   lon=[default_bbox_east_lon, default_bbox_east_lon],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='east_bbox'))

    # Index 3: west_bbox
    fig.add_trace(go.Scattermapbox(lat=[default_bbox_north_lat, default_bbox_south_lat],
                                   lon=[default_bbox_west_lon, default_bbox_west_lon],
                                   mode='lines', line=dict(color='black'), hoverinfo='skip', name='west_bbox'))

    # Index 4: edges
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='lines', line=dict(color='red'), name='edges'))

    # Index 5: selected edge
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='lines', marker=dict(color='blue', size=10),
                                   name='selected_edge'))

    # Index 6: nodes
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='markers', marker=dict(color='red', size=10),
                                   name='nodes'))

    # Index 7: selected node
    fig.add_trace(go.Scattermapbox(lat=[], lon=[], customdata=[], mode='markers', marker=dict(color='blue', size=20),
                                   name='selected_node'))

    return fig
