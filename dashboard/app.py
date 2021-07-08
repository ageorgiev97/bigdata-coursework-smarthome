from collections import OrderedDict
import datetime
from typing import List, Optional

import dash
import dash_core_components as dcc
import dash_html_components as html
import mysql.connector
import numpy as np
import plotly.graph_objects as go
import plotly.subplots
from dash.dependencies import Output, Input
from mysql.connector import MySQLConnection

connection: Optional[MySQLConnection] = None


def ensure_connection():
    global connection
    if connection is not None and connection.is_connected():
        return connection

    if connection is not None:
        connection.close()

    connection = mysql.connector.connect(
        host='localhost',
        database='SensorData',
        user='root',
        password='root'
    )


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "SmartHome Analytics: visualise and analyze your home!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🏠", className="header-emoji"),
                html.H1(
                    children="SmartHome Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the data from different sensors in your home",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed="2020-12-1",
                            max_date_allowed="2021-12-1",
                            start_date="2020-12-28",
                            end_date="2020-12-29",
                        ),
                    ]
                ),

            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(id="temperature-chart"),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(id="humidity-chart"),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(id="battery-chart"),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(id="memory-chart"),
                    className="card",
                )
            ],
            className="wrapper",
        ),
    ]
)

mega_cache: OrderedDict = OrderedDict()


def query_sensor_data(name: str, start: str, stop: str):
    cursor = connection.cursor()

    now = datetime.datetime.now()
    key = (name, start, stop)
    if key in mega_cache:
        values = mega_cache[key]
        date, x, y = values
        if now - date < datetime.timedelta(minutes=2):
            print(f"Using cached values for key: {key}")

            del mega_cache[key]
            mega_cache[key] = values
            return x, y
        else:
            del mega_cache[key]

    query = f"""
        select Created, State from SensorData
        where Entity like '%{name}'
            and Created between
                '{start}' and '{stop}'
    """
    cursor.execute(query)
    data = cursor.fetchall()
    x, y = zip(*data)

    mega_cache[key] = now, x, np.array(y)

    if len(mega_cache) > 100:
        del mega_cache[list(mega_cache)[0]]

    return mega_cache[key][1:]


def make_scatter(value: str, name: str, start: str, stop: str):
    x, y = query_sensor_data(value, start, stop)
    y[np.where(y == -696969)] = np.nan

    return go.Scatter(
        x=x,
        y=y,
        line_shape='spline',
        name=name
    )


def make_subplot(values: List[str], names: List[str], title: str, start: str, stop: str):
    fig = plotly.subplots.make_subplots(
        rows=1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.009,
        horizontal_spacing=0.009
    )
    fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 50, 't': 25}
    fig['layout']['title'] = title
    for value, name in zip(values, names):
        fig.append_trace(make_scatter(value, name, start, stop), 1, 1)

    return fig


@app.callback(
    [
        Output("temperature-chart", "figure"),
        Output("humidity-chart", "figure"),
        Output("battery-chart", "figure"),
        Output("memory-chart", "figure")
    ],
    [Input("date-range", "start_date"), Input("date-range", "end_date")],
)
def update_figures(start, stop):
    ensure_connection()
    return (
        make_subplot(
            [
                "humidity_kitchen",
                "humidity_livingroom"
            ],
            [
                "Kitchen",
                "Living Room"
            ],
            'Humidity by room',
            start,
            stop
        ), make_subplot(
            [
                "temperature_kitchen",
                "temperature_livingroom"
            ],
            [
                "Kitchen",
                "Living Room"
            ],
            'Temperature by room',
            start,
            stop
        ), make_subplot(
            [
                "battery_kitchen",
                "battery_livingroom"
            ],
            [
                "Kitchen",
                "Living Room"
            ],
            'Battery left by room',
            start,
            stop
        ), make_subplot(
            [
                "memory_free",
            ],
            [
                "",
            ],
            'Free memory',
            start,
            stop
        )
    )


if __name__ == "__main__":
    app.run_server(debug=False)
