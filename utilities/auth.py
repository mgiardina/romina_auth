# external imports
import traceback
from sqlalchemy import Table, create_engine, MetaData
from sqlalchemy.sql import select, and_
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from werkzeug.security import generate_password_hash
from flask_login import current_user
from functools import wraps
import random
from mailjet_rest import Client
import os
from datetime import datetime, timedelta
import shortuuid
import dash_core_components as dcc
import dash_html_components as html

from utilities.keys import (
    MAILJET_API_KEY,
    MAILJET_API_SECRET,
    FROM_EMAIL
)


Column = sqlalchemy.Column
String = sqlalchemy.String
Integer = sqlalchemy.Integer
DateTime = sqlalchemy.DateTime
db = SQLAlchemy()
Column, String, Integer, DateTime = db.Column, db.String, db.Integer, db.DateTime


class User(db.Model):
    id = Column(Integer, primary_key=True)
    first = Column(String(100))
    last = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))


def user_table():
    return Table("user", User.metadata)


def add_user(first, last, password, email, engine):
    table = user_table()
    hashed_password = generate_password_hash(password, method="sha256")

    values = dict(first=first, last=last, email=email, password=hashed_password)
    statement = table.insert().values(**values)

    try:
        conn = engine.connect()
        conn.execute(statement)
        conn.close()
        return True
    except:
        return False


def show_users(engine):
    table = user_table()
    statement = select([table.c.first, table.c.last, table.c.email])

    conn = engine.connect()
    rs = conn.execute(statement)

    for row in rs:
        print(row)

    conn.close()

def del_user(email, engine):
    table = user_table()

    delete = table.delete().where(table.c.email == email)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()

def user_exists(email, engine):
    #Chequeamos si el usuario existe
    table = user_table()
    statement = table.select().where(table.c.email == email)
    with engine.connect() as conn:
        resp = conn.execute(statement)
        ret = next(filter(lambda x: x.email == email, resp), False)
    return bool(ret)


def change_password(email, password, engine):
    if not user_exists(email, engine):
        return False

    table = user_table()
    hashed_password = generate_password_hash(password, method="sha256")
    values = dict(password=hashed_password)
    statement = table.update(table).where(table.c.email == email).values(values)

    with engine.connect() as conn:
        conn.execute(statement)

    # success value
    return True

def change_user(first, last, email, engine):
    if not user_exists(email, engine):
        return False

    table = user_table()
    values = dict(first=first, last=last,)
    statement = table.update(table).where(table.c.email == email).values(values)
    with engine.connect() as conn:
        conn.execute(statement)
    # success value
    return True


class PasswordChange(db.Model):
    __tablename__ = "password_change"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    password_key = Column(String(6))
    timestamp = Column(DateTime())


def password_change_table():
    return Table("password_change", PasswordChange.metadata)


def send_password(email, firstname, engine):
    # voy a agregar aca la logica para enviar email
    return True


def validate_password_key(email, key, engine):
    if not user_exists(email, engine):
        return False

    table = password_change_table()
    statement = select([table.c.email, table.c.password_key, table.c.timestamp]).where(
        and_(table.c.email == email, table.c.password_key == key)
    )
    with engine.connect() as conn:
        resp = list(conn.execute(statement))
        if len(resp) == 1:
            if (resp[0].timestamp - (datetime.now() - timedelta(1))).days < 1:
                return True
        return False

    return True
