from urllib.parse import quote as urlquote
from server import app, User, engine
from functools import wraps
import time
import random
import datetime
import plotly.express as px
from flask_login import current_user
import random
from dash import no_update
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='research-url', refresh=True)

temp = []

nValues = []

def layout():
    return dbc.Row(
        dbc.Col(
            [
                location,
                html.Div(id='romi-login-trigger'),
                html.H1('Multiple output callback research'),
                html.Br(),


                html.H5('by Romina Mezher & Mariano Giardina'),
                html.Br(),

                html.H6('We developed a way to use a same output for different inputs inside one callback'),
                html.H6('Inside the callback, and calling the app context, we have access to information regarding the control which triggered the callback'),
                html.H6('=)'),
                html.Br(),
                dbc.Button('Primary', id='btnPrimary', color="primary", className="mr-1"),
                dbc.Button('Warning', id='btnWarning', color="warning", className="mr-1"),
                dbc.Button('Danger', id='btnDanger', color="danger"),
                html.Div(id='htmlContainer', className="mt-4"),
                dcc.Graph(id='live-update-graph'),
                dcc.Interval(id='interval-component',interval=1*2000,n_intervals=0)
            ]
        )
    )

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_figure(n):

    values = round(random.uniform(10.0, 20.0), 1)    

    temp.append(values) 

    nValues.append(n)    

    fig = px.line(x=nValues,y=temp)
    
    return(fig)



@app.callback(Output('htmlContainer', 'children'),
              [Input('btnPrimary', 'n_clicks'),
               Input('btnWarning', 'n_clicks'),
               Input('btnDanger', 'n_clicks')])
def display(btn1, btn2, btn3):

    # leo el contexto actual de la app
    context = dash.callback_context

    # IMPORTANTE
    # levanto el ID del control que triggereo el callback, con esto obtengo el ID
    buttonClicked = context.triggered[0]['prop_id'].split('.')[0] 

    # En base al ID del control que fue el trigger, puedo ejecutar diferentes logicas
    # Actualizando el mismo output =)
    if (buttonClicked == "btnPrimary"):
        returnedHtml = "You clicked Primary Button"
    else:
        if (buttonClicked == "btnWarning"):
            returnedHtml = "You clicked Warning Button"       
        else:
            returnedHtml = "You clicked Danger Button"       

    # WE DID IT
    return(returnedHtml)
