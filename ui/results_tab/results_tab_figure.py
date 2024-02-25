import plotly.graph_objs as go

from lib.default_bbox import default_bbox


def get_default_results_tab_figure():
    layout = go.Layout(
        mapbox=dict(
            style='open-street-map',
            zoom=14,
            center=dict(lat=(default_bbox["north"] + default_bbox["south"]) / 2,
                        lon=(default_bbox["east"] + default_bbox["west"]) / 2)
        ),
        height=800,
        showlegend=False
    )

    fig = go.Figure(layout=layout)

    fig.add_trace(
        go.Scattermapbox(lat=[], lon=[], mode='markers', marker=dict(color='red', size=10), name='nodes'))

    fig.add_trace(
        go.Scattermapbox(lat=[], lon=[], mode='markers', marker=dict(color='blue', size=20), name='selected node'))

    fig.add_trace(
        go.Scattermapbox(lat=[], lon=[], mode='lines', line=dict(color='black'), name='result_lines'))

    fig.add_trace(
        go.Scattermapbox(lat=[], lon=[], mode='lines', line=dict(color='black'), name='result_arrows'))

    fig.add_trace(
        go.Scattermapbox(lat=[], lon=[], text=[], mode='markers+text', textposition="top right",
                         marker=dict(size=0), textfont=dict(size=18, color='red'),
                         name='labels'))

    return fig
