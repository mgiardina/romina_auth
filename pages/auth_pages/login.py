import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State
from dash import no_update

from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
import time

from server import app, User


success_alert = dbc.Alert(
    'Logged in successfully. Taking you home!',
    color='success',
    dismissable=True
)
failure_alert = dbc.Alert(
    'Login unsuccessful. Try again.',
    color='danger',
    dismissable=True
)
already_login_alert = dbc.Alert(
    'User already logged in. Taking you home!',
    color='warning',
    dismissable=True
)


def layout():
    return dbc.Row(
        dbc.Col(
            [
                dcc.Location(id='login-url',refresh=True,pathname='/login'),
                html.Div(id='login-trigger',style=dict(display='none')),
                html.Div(id='login-alert'),
                html.H2("Please, Sign in"),
                html.Br(),
                dbc.FormGroup(
                    [
                        dbc.Alert('Try romi@aws.com / romi', color='info',dismissable=True),
                        html.Br(),

                        dbc.FormText('Email'),
                        dbc.Input(id='login-email',autoFocus=True),
                       
                        
                        html.Br(),
                        dbc.FormText('Password'),                        
                        dbc.Input(id='login-password',type='password',debounce=True),
                        
                        
                        html.Br(),
                        dbc.Button('Login',color='success',id='login-button',size="lg", className="mr-1"),
                        dbc.Button('Register', color="info", href='/register', className="mr-1"),
                        dbc.Button('Forgot Password',color="warning", href='/forgot', className="mr-1")
                    ]
                )
            ],
            width=6
        )
    )

@app.callback(
    [Output('login-url', 'pathname'),
     Output('login-alert', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('login-password', 'value')],
    [State('login-email', 'value')]
)
def login_success(n_clicks, password, email):
    #logueo del usuario aca
    if password is not None or n_clicks > 0:
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)

                return '/home',success_alert
            else:
                return no_update,failure_alert
        else:
            return no_update,failure_alert
    else:
        return no_update,''