import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State
from dash import no_update
from flask_login import current_user
import time

from server import app

home_login_alert = dbc.Alert(
    'User not logged in. Redirecting you to login.',
    color='danger'
)

def layout():
    return dbc.Row(
        dbc.Col(
            [
                dcc.Location(id='home-url',refresh=True),
                html.Div(id='home-login-trigger',style=dict(display='none')),

                html.H1('Home page'),
                html.Br(),

                html.H5('Welcome to our home page!'),
                html.Br(),

                html.H6('We are going to add some cool stuff here'),
                html.Br(),
            ],
            width=6
        )
    )
