import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State
from dash import no_update
import random
from flask_login import current_user
import time
from functools import wraps

from server import app

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='romi-url',refresh=True)

def layout():
    # si el usuario esta autenticado
    # esta es solo una pagina de prueba 
    return dbc.Row(
        dbc.Col(
            [
                location,
                html.Div(id='romi-login-trigger'),

                html.H1('Romi Page'),
                html.Br(),

                html.H5('Welcome to Romi Page!'),
                html.Br(),

                html.H6('We are going to add some other cool stuff here'),
                html.Br(),
            ],
            width=6
        )

    )

