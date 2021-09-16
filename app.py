import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

#df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server=app.server, external_stylesheets=external_stylesheets, external_scripts=[{"src": "https://cdn.plot.ly/plotly-2.3.1.min.js"}])

df = pd.read_csv('owid-covid-data.csv')
dff = df[df['location']=='Australia']
dff = dff[['date', 'new_cases_smoothed']]
fig = px.line(dff, x='date', y='new_cases_smoothed')

app.layout = html.Div([
    html.Div(
        id='status', children=""
    ),
    dcc.Graph(id='myDiv', figure=fig),
    dcc.RangeSlider(id='slider',
               min=0,
               max=1000,
               value=[0, dff.shape[0]],
               updatemode='mouseup'),
    html.Button('>', id='button', n_clicks=0),
    dcc.Store(
        id='dataframe', data={}
    ),
    dcc.Interval(
        id='serverside-interval',
        interval=10000,
        n_intervals=1
    ),
    dcc.Interval(
        id='playing',
        n_intervals=1,
        interval=25,
        disabled=True
    ),
])


@app.callback(
    Output('dataframe', 'data'),
    Output('slider', 'max'),
    Input('serverside-interval', 'n_intervals'),
)
def update_store_data(n_intervals):
    return [dff['date'],dff['new_cases_smoothed']], dff.shape[0]



app.clientside_callback(
    """
    function(n_intervals, drag_value, value, data, not_playing) {
        value[0] = drag_value[0];
        if (not_playing) {
            value[1] = drag_value[1]
            new_data = {
            x: data[0].slice(value[0], value[1]),
            y: data[1].slice(value[0], value[1]),
            type: 'scatter'
            };
            data = [new_data];
            var layout = {
            showlegend: false
            };
            Plotly.newPlot('myDiv', data, layout, {staticPlot: true});
            return [value[0], value[1]];
        } else {
            if (drag_value[1] != value[1]) {
                value[1] = drag_value[1];
            } else {
                value[1] = value[1]+1;
            }
            new_data = {
            x: data[0].slice(value[0], value[1]),
            y: data[1].slice(value[0], value[1]),
            type: 'scatter'
            };
            data = [new_data];
            var layout = {
            showlegend: false
            };
            Plotly.newPlot('myDiv', data, layout, {staticPlot: true});
            return [value[0], value[1]];
        }
    }
    """,
    Output('slider', 'value'),
    Input('playing', 'n_intervals'),
    Input('slider', 'drag_value'),
    State('slider', 'value'),
    State('dataframe', 'data'),
    State('playing', 'disabled'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function(n_clicks, not_playing) {
        if (not_playing) {
            return false;
        } else {
            return true;
        }
    }
    """,
    Output('playing', 'disabled'),
    Input('button', 'n_clicks'),
    State('playing', 'disabled'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run_server(debug=True, port=5559)
