import plotly.graph_objects as go

lon = [-99.1332, -98.4831, -97.7431, -96.7970, -95.3698]
lat = [19.4326, 29.4237, 30.2672, 32.7767, 29.7604]
text = ["Mexico City", "San Antonio", "Austin", "Dallas", "Houston"]

layout = go.Layout(
        mapbox=dict(
            style='open-street-map',
            zoom=14,  # Zoom level
            center=dict(lat=29.7604, lon=-95.3698)
        ),
        height=800,
        showlegend=False
    )

fig = go.Figure(layout=layout)

fig.add_trace(go.Scattermapbox(
    lon=lon,
    lat=lat,
    text=text,
    mode='markers+text',  # Use 'text' mode so only text is displayed
    textposition="top right",
))

fig.show()