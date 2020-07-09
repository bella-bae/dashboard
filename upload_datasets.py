# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 13:30:38 2020

@author: kt NexR
"""


# import packages
import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd




# 외부 css파일 가져오기
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



# App 실행
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Markdown 작성
markdown_text = '''
# Data Upload App *by Bella*

#### 정형 및 비정형 자료의 업로드 후 간단한 확인 가능: Dash core component 중 [Upload](https://dash.plotly.com/dash-core-components/upload) 모듈 활용
'''

app.layout = html.Div(style = {'backgroundColor': '#f5f5f5'}, children = [
    dcc.Markdown(children = markdown_text, style = {'textAlign': 'center'}),
    
    html.Label('데이터 형태 선택'),
    dcc.RadioItems(
        id = 'data-type',
        options=[{'label': i, 'value': i} for i in ['numeric', 'image']],
        value = 'numeric',
        labelStyle = {'display': 'inline-block'            
            }),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
            ]),
        style={
            'width': '95%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    
    html.Div(id='output-data-upload'),

])





# parsing numeric dataset def -> df가 최종 output
def parse_contents_numeric(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    # data upload와 함께 표출될 화면 구성
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.now()),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])




# parsing image dataset def -> contents가 최종 output
def parse_contents_img(contents, filename, date):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.now()),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])





# making interactive app with numeric&image datasets
# Input, Output은 특정 component의 property(뒤)와 id(앞)를 갖고 있음
@app.callback(Output('output-data-upload', 'children'),
              [Input('data-type', 'value'),
               Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def update_output(list_of_types, list_of_contents, list_of_names, list_of_dates):
    
    
    if list_of_types == 'numeric':
        children = [
            parse_contents_numeric(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
    elif list_of_types == 'image':
        children = [
            parse_contents_img(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        
    return children


if __name__ == '__main__':
    app.run_server(debug=True)