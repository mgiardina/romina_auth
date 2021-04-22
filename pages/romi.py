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
                                        dcc.Dropdown(
                                            id="ddlFolderSearch",
                                            options=list_folders(),
                                            placeholder="select folder", className = "mb-3",value= 'root'
                                        ),
                                        dbc.Input(
                                            id="txtSearch", type="search", placeholder="Search"),
                                        dbc.Button(
                                            "Search", id="btnSearch", color="primary", className="mt-3"),
                                        dbc.Button(
                                            "Clear", id="btnClear", color="secondary", className="mt-3 ml-3"),
                                        #html.H2("Current Blob List",className="mt-3"), 
                                        html.Ul(id="file-list", className="mt-3")        
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
                                        dcc.Dropdown(
                                            id="ddl-folder",
                                            options=list_folders(),
                                            placeholder="select folder to upload", style= {"margin": "10px"}
                                        ),
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
                                            id="ddl-folderDelete",
                                            options=list_folders(),
                                            placeholder="select folder", className = "mb-3",
                                        ),
                                        dcc.Dropdown(
                                            id="ddl-delete",
                                            placeholder="select blob to delete",
                                        ),
                                        dbc.Button(
                                            "Delete Blob", id="btnDelete", color="danger", className="mt-3", style={"float": "right"}),

                                    ]
                                ), className="mt-3"
                            ),
                        ], label="Delete blobs"),
                        dbc.Tab(children=[
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H2("Folder management"),
                                        dbc.Input(id="txtFolderName", placeholder="Enter folder name...", type="text"),
                                        dbc.Button("Create Folder", id="btnFolder", color="primary", className="mt-3", style={"float": "right"}),

                                    ]
                                ), className="mt-3"
                            ),
                        ], label="Create your Folder")                        
                    ]
                ),
                html.Div(id="toastContainer"),
                html.Div(id="FolderToastContainer"),
                html.Div(id="toastSearch"),
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

def list_folders():

    folders = []
    folders.append({'label': '/', 'value': 'root'})

    result = client.list_objects(Bucket=BUCKET, Delimiter='/')
    for folder in result.get('CommonPrefixes'):
        folders.append({'label': folder['Prefix'].replace('/',''), 'value': folder['Prefix']})

    return folders    

def save_file(folderName,name, content):

    data = content.encode("utf8").split(b";base64,")[1]
 
    finalName = folderName + name

    if (folderName == 'root'):
        finalName = name
        
    s3.Bucket(BUCKET).put_object(Key=finalName, Body=base64.decodebytes(data))
    s3.ObjectAcl(BUCKET, finalName).put(ACL='public-read')


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

def getBlobs(searchFolder,pattern):
    files = []
    tempFiles = []
    response = client.list_objects(Bucket=BUCKET)

    if (len(searchFolder) == 0):  # valida si selecciono una carpeta
        if (len(pattern) == 0):
            for blob in response['Contents']:
                files.append(blob['Key'])
        else:
            for blob in response['Contents']:
                if (blob['Key'].lower().find(pattern.lower()) != -1):
                    files.append(blob['Key'])
    else:
        tempFiles = []
        if (searchFolder == "root"):
            for blob in response['Contents']:
                if (blob['Key'].lower().find("/") == -1):
                    tempFiles.append(blob['Key'])  

            for blob in tempFiles:  # tempFiles es la filtrada del folder
                if (blob.lower().find(pattern.lower()) != -1):
                    files.append(blob)                      
        else:
            for blob in response['Contents']:
                if (blob['Key'].lower().find("/") != -1):
                    if (blob['Key'].lower().find(searchFolder.lower()) != -1):
                        tempFiles.append(blob['Key']) 

            if (len(pattern) == 0):
                counter = 0
                for blob in tempFiles:
                    if (counter > 0):
                        files.append(blob)       
                    counter = counter + 1
            else:
                for blob in tempFiles:
                    if (blob.lower().find(pattern.lower()) != -1):
                        files.append(blob)        

    return files


@app.callback(Output('FolderToastContainer', 'children'), 
            [Input('btnFolder', 'n_clicks'),
            State('txtFolderName', 'value')])

def create_folder(n_clicks,value):

    s3.Bucket(BUCKET).put_object(Key= value + '/')

    returnedToast = dbc.Toast([html.P("Folder " + value + " created")], header=("Success"), icon="success", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})                  
    
    return returnedToast

@app.callback(Output('ddl-delete','options'),
                [Input('ddl-folderDelete','value'),State('ddl-folderDelete','value')])

def delete_from_folder(value,selFolder):

    optionList = []
    response = client.list_objects(Bucket=BUCKET)

    if (selFolder == 'root'):
        for blob in response['Contents']:
            if (blob['Key'].find('/') == -1):  # No lo encontro
                optionList.append({'label': blob['Key'].replace(selFolder,''), 'value': blob['Key']})  
    else:
        for blob in response['Contents']:
            if (blob['Key'].find(selFolder) != -1):
                optionList.append({'label': blob['Key'].replace(selFolder,''), 'value': blob['Key']})  
                    
    return optionList


@app.callback([Output('file-list', 'children'), Output('toastSearch', 'children'),
                Output('txtSearch','value'),Output('ddlFolderSearch','value')],
               [Input('btnSearch', 'n_clicks'),Input('btnClear', 'n_clicks'),
               State('txtSearch', 'value'),State('ddlFolderSearch','value')])
def display(btnSearch, btnClear, pattern, searchFolder):

    context = dash.callback_context

    buttonClicked = context.triggered[0]['prop_id'].split('.')[0]

    blobCount = 0

    if (searchFolder is None):
        searchFolder = ""

    if (pattern is None):
        pattern = ""

    txtSearch = ""

    ddlFolderSearch = "root"

    if (buttonClicked == "btnSearch"):
        if(pattern == "" and searchFolder == ""):
            foundedBlobs = []
            returnedToast = dbc.Toast([html.P("Please select folder or pattern")], header=("No blobs founded"), icon="danger", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"})
        else:        
            txtSearch = pattern
            ddlFolderSearch = searchFolder
            foundedBlobs = getBlobs(searchFolder, pattern)
            blobCount = len(foundedBlobs)
            if (blobCount > 0):
                returnedToast = dbc.Toast([html.P(str(blobCount) + " Blobs founded")], header=("Success"), icon="success", dismissable=True, style={
                    "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})
            else:
                returnedToast = dbc.Toast([html.P("No Matches")], header=("No blobs founded"), icon="danger", dismissable=True, style={
                    "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"})


    if (buttonClicked == "btnClear"):
        foundedBlobs = getBlobs('root', '')
        returnedToast = dbc.Toast([html.P("Search Cleared")], header=("Success"), icon="success", dismissable=True, style={
            "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})          



    if len(foundedBlobs) == 0:
        if(pattern != "" and searchFolder != ""):
            returnedHtml = [html.Li("No blobs founded!")]
        else:
            returnedHtml = ""    
    else:
        returnedHtml = [html.Li(file_download_link(filename))
                        for filename in foundedBlobs]        

    return(returnedHtml,returnedToast,txtSearch,ddlFolderSearch)

@app.callback(Output('toastContainer', 'children'),
              [Input('btnUpload', 'filename'), Input('btnUpload', 'contents'),
               Input('btnDelete', 'n_clicks'), 
               State('ddl-delete', 'value'),State('ddl-folder','value')])
def display(uploaded_filenames, uploaded_file_contents, btnDelete,deleteKey, selFolder):
    
    context = dash.callback_context

    buttonClicked = context.triggered[0]['prop_id'].split('.')[0]

    if (buttonClicked == "btnUpload"):
            if (selFolder):
                if uploaded_filenames is not None and uploaded_file_contents is not None:
                    for name, data in zip(uploaded_filenames, uploaded_file_contents):
                        save_file(selFolder,name, data)                  
                
                filesCount = len(uploaded_filenames)
                message = "Blob " + name + " uploaded"
            
                if (filesCount > 1):
                    message = str(filesCount) + " Blobs uploaded"

                returnedToast = dbc.Toast([html.P(message)], header=("Success"), icon="success", dismissable=True, style={
                    "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})                  
            else:
                returnedToast = dbc.Toast([html.P("You must select a folder")], header=("No folder selected"), icon="danger", dismissable=True, style={
                    "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"})


    if (buttonClicked == "btnDelete"):
        if deleteKey:
            client.delete_object(Bucket=BUCKET, Key=deleteKey)
            returnedToast = dbc.Toast([html.P("Blob " + deleteKey + " deleted")], header=("Success"), icon="success", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "green", "color": "white"})                      
        else:
            returnedToast = dbc.Toast([html.P("You must select a blob")], header=("No blob selected"), icon="danger", dismissable=True, style={
                "position": "fixed", "top": 66, "right": 20, "width": 350, "background-color": "red", "color": "white"})
             
    return(returnedToast)
