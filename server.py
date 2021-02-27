import dash
import dash_bootstrap_components as dbc
import os
from flask_login import LoginManager, UserMixin
import random
from utilities.auth import db, User as base
from utilities.config import config, engine


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
)

server = app.server
app.config.suppress_callback_exceptions = True
app.title = 'Dash Authentication App by Romina Mezher'
server.config.update(
    SECRET_KEY='#tolkienrowlingstephenkingdrikingbeertogether$20',
    SQLALCHEMY_DATABASE_URI=config.get('database', 'con'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db.init_app(server)

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


class User(UserMixin, base):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
