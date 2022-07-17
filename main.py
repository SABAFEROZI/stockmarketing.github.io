import dash
from dash import Dash, Input, Output, State, html, dcc, dash_table, callback
from flask import flash,render_template
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime as dt
from model import prediction
def get_stock_price_fig(df):

    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Openning Price vs Date")

    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig



app = dash.Dash(__name__)
server = app.server

app.layout=html.Div([

html.Div([
    html.P("Welcome to the Stock Dash App!"),



html.Div([
    html.H3("Input stock code:"
            ),
html.Div([
    dcc.Input(id="dropdown_tickers", type="text"),
    html.Button('Submit', id='submit-val', n_clicks=0),
])
    ]),
    html.Div([
        dcc.DatePickerRange(id='my-date-picker-range',
                            min_date_allowed=dt(1995, 8, 5),
                            max_date_allowed=dt.now(),
                            initial_visible_month=dt.now(),
                            end_date=dt.now().date()),
    ]),

    html.Div([
                    html.Button(
                        "Stock Price",  id="stock", n_clicks=0),
                    html.Button("Indicators",

                                id="indicators", n_clicks=0),
                    dcc.Input(id="n_days",
                              type="text",
                              placeholder="number of days"),
                    html.Button(
                        "Forecast",  id="forecast", n_clicks=0)
                ]),
html.P("To verify the stock prices click on the image below."),
html.Div(
html.A(

    href="https://finance.yahoo.com/",
    children=[
        html.Img(
            alt="Link to yfinance verification",
            src="/assets/logo.png",
        )
    ]
)),]),


html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),
html.Br(),

html.Div(
            [
                html.Div(
                    [html.Img(id="logo"),
                        html.P(id="ticker")
                ]),
                html.Div( id="description"),
                html.Div([], id="graphs-content"),
                html.Div([], id="main-content"),


                html.Div([], id="forecast-content"),

],className="content"),
],className="container")













@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
],
[Input("submit-val", "n_clicks")], [State("dropdown_tickers", "value")])

def update_data(n, val):
    if n == None:
          return  "","", "", None, None, None
    else:
        if val==None:
                return "", "", "", None, None, None


        else:
                ticker = yf.Ticker(val)
                inf = ticker.info
                if (ticker.info['regularMarketPrice'] == None):
                    return ("You did not input a correct stock ticker! Try again."),"","",None,None,None
                else:

                    df = pd.DataFrame().from_dict(inf, orient="index").T
                    df[['logo_url', 'shortName', 'longBusinessSummary']]





                    return df['longBusinessSummary'].values[0], df['logo_url'].values[0], df['shortName'].values[0], None, None, None

@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
    if val == None:
        return [""]
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]

@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        return [""]
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]






if __name__ == '__main__':
      app.run_server(debug=True)