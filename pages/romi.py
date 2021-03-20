from urllib.parse import quote as urlquote
from server import app, User, engine
from botocore.client import Config
import boto3
import base64
from functools import wraps
import time
from flask_login import current_user
import random
from dash import no_update
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

BUCKET = 'rominamarianoblobjob'

s3 = boto3.resource('s3')

client = boto3.client('s3',
                      config=Config(signature_version='s3v4'))

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='romi-url', refresh=True)

response = client.list_objects(Bucket=BUCKET)

optionList = []
for blob in response['Contents']:
    optionList.append({'label': blob['Key'], 'value': blob['Key']})


def layout():
    return dbc.Row(
        dbc.Col(
            [
                location,
                html.Div(id='romi-login-trigger'),
                html.H1('Romi Blob Manager'),
                html.Br(),

                html.H5('Welcome to Romi Blobs Manager!'),
                html.Br(),

                html.H6('We are going to add some other cool stuff here'),
                html.Br(),
                dbc.Tabs(
                    [
                        dbc.Tab(children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Blob List"), html.Ul(
                                            id="file-list", children=list_files())
                                    ]
                                ), className="mt-3"
                            )
                        ], label="Blob List"),
                        dbc.Tab(children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Upload your file"),
                                        dcc.Upload(
                                            id="upload-data",
                                            children=html.Div(
                                                ["Drag and drop or click to select a file to upload."]
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "60px",
                                                "lineHeight": "60px",
                                                "borderWidth": "1px",
                                                "borderStyle": "dashed",
                                                "borderRadius": "5px",
                                                "textAlign": "center",
                                                "margin": "10px",
                                            },
                                            multiple=True,
                                        ),
                                    ]
                                ), className="mt-3"
                            ),
                            html.Div(id="uploaded-files"),
                        ], label="Upload your File"),
                        dbc.Tab(children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Delete files"),
                                        dcc.Dropdown(
                                            id="data-dropdown",
                                            options=optionList,
                                            placeholder="select file to delete",
                                        )
                                    ]
                                ), className="mt-3"
                            ),
                            dbc.Button("Delete File", id="btn-delete"),
                            html.Div(id="deleted-files"),
                        ], label="Delete files")
                    ]
                )
            ]
        )
    )


def list_files():
    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]


def save_file(name, content):
    data = content.encode("utf8").split(b";base64,")[1]

    s3.Bucket(BUCKET).put_object(Key=name, Body=base64.decodebytes(data))
    s3.ObjectAcl(BUCKET, name).put(ACL='public-read')


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    response = client.list_objects(Bucket=BUCKET)

    for blob in response['Contents']:
        files.append(blob['Key'])

    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "https://rominamarianoblobjob.s3.us-east-2.amazonaws.com/{}".format(
        urlquote(filename))
    return html.A(filename, href=location)


@ app.callback(
    [Output("file-list", "children"),
     Output("uploaded-files", "children")],
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def upload_blob(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files], dbc.Toast([html.P("Operation finished Succesfully")], header=("Blob(s) uploaded OK"),
                                                                                        icon="success", dismissable=True, style={"position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"},
                                                                                        )


@ app.callback(
    [Output("deleted-files", "children"),
     Output('data-dropdown', 'options')],
    Input('btn-delete', 'n_clicks'),
    state=[State(component_id='data-dropdown', component_property='value')]
)
def delete_blob(btn1, value):
    if value:
        client.delete_object(Bucket=BUCKET, Key=value)

        optionList = []
        response = client.list_objects(Bucket=BUCKET)
        for blob in response['Contents']:
            optionList.append({'label': blob['Key'], 'value': blob['Key']})

    return dbc.Toast([html.P("Blob deleted OK")], header=("Blob " + value),
                     icon="danger", dismissable=True, style={"position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"},
                     ), optionList,
