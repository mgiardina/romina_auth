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
import dash

BUCKET = 'rominamarianoblobjob'

s3 = boto3.resource('s3')

client = boto3.client('s3',
                      config=Config(signature_version='s3v4'))

login_alert = dbc.Alert(
    'User not logged in. Taking you to login.',
    color='danger'
)

location = dcc.Location(id='romi-url', refresh=True)


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
                        dbc.Tab(children=[dbc.Row(
                            [dbc.Col(dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Search Blob List"),
                                        dbc.Input(
                                            id="search_file", type="search", placeholder="Search"),
                                        dbc.Button(
                                            "Search", id="btnSearch", color="primary", className="mt-3")
                                    ],
                                ), className="mt-3"
                            ), md=12),
                            ],)
                        ], label="Current Blob List"),
                        dbc.Tab(children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Upload your file"),
                                        dcc.Upload(
                                            id="btnUpload",
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
                            )
                        ], label="Upload your File"),
                        dbc.Tab(children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Delete blob"),
                                        dcc.Dropdown(
                                            id="data-dropdown",
                                            options=list_blobs(),
                                            placeholder="select blob to delete",
                                        ),
                                        dbc.Button(
                                            "Delete Blob", id="btnDelete", color="danger", className="mt-3", style={"float": "right"}),

                                    ]
                                ), className="mt-3"
                            ),
                        ], label="Delete blobs")
                    ]
                ),
                html.Div(id="toastContainer"),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H2("Current Blob List"), html.Ul(
                                id="file-list", children=list_files())
                        ]
                    ), className="mt-3"
                )
            ]
        )
    )

# metodo usado para actualizar dinamicamente el contenido del dropdown cuando se navega a otra pantalla y se vuelve a la de blob management
# anteriormente estabamos populando el dropdown solo una vez al comienzo de todo el Dash


def list_blobs():
    response = client.list_objects(Bucket=BUCKET)

    optionList = []
    for blob in response['Contents']:
        optionList.append({'label': blob['Key'], 'value': blob['Key']})
    return optionList


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
    location = "https://rominamarianoblobjob.s3.us-east-2.amazonaws.com/{}".format(
        urlquote(filename))
    return html.A(filename, href=location)

def getBlobs(pattern):
    files = []
    response = client.list_objects(Bucket=BUCKET)

    if (len(pattern) == 0):
        for blob in response['Contents']:
            files.append(blob['Key'])
    else:
        for blob in response['Contents']:
            if (blob['Key'].find(pattern) != -1):
                files.append(blob['Key'])

    return files


@app.callback([Output('file-list', 'children'), Output('toastContainer', 'children'), Output('data-dropdown', 'options')],
              [Input('btnSearch', 'n_clicks'),
               Input("btnUpload", "filename"), Input("btnUpload", "contents"),
               Input('btnDelete', 'n_clicks'), State('data-dropdown', 'value'),
               State('search_file', 'value')])
def display(btnSearch, uploaded_filenames, uploaded_file_contents, btnDelete, deleteKey, pattern):

    context = dash.callback_context

    buttonClicked = context.triggered[0]['prop_id'].split('.')[0]
    blobCount = 0

    if (buttonClicked == "btnSearch"):
        if (pattern):

            foundedBlobs = getBlobs(pattern)
            blobCount = len(foundedBlobs)

            if (blobCount > 0):
                returnedToast = dbc.Toast([html.P("Success")], header=("Blobs founded"), icon="success", dismissable=True, style={
                    "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})
            else:
                returnedToast = dbc.Toast([html.P("No Matches")], header=("No blobs founded"), icon="danger", dismissable=True, style={
                    "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"})
        else:
            pattern = ""
            returnedToast = dbc.Toast([html.P("Information")], header=("Please enter a pattern"), icon="danger", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"})
    else:
        if (buttonClicked == "btnUpload"):

            if uploaded_filenames is not None and uploaded_file_contents is not None:
                for name, data in zip(uploaded_filenames, uploaded_file_contents):
                    save_file(name, data)                  

            pattern = ""   
            returnedToast = dbc.Toast([html.P("Success")], header=("Blobs uploaded"), icon="success", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})                  
        else:
            if deleteKey:
                client.delete_object(Bucket=BUCKET, Key=deleteKey)
                pattern = ""   
                returnedToast = dbc.Toast([html.P("Success")], header=("Blob deleted"), icon="success", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})                      

    blobs = getBlobs(pattern)

    if len(blobs) == 0:
        returnedHtml = [html.Li("No blobs founded!")]
    else:
        returnedHtml = [html.Li(file_download_link(filename))
                        for filename in blobs]

    optionList = []
    response = client.list_objects(Bucket=BUCKET)
    for blob in response['Contents']:
        optionList.append({'label': blob['Key'], 'value': blob['Key']})                        

    return(returnedHtml, returnedToast, optionList)
