#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 21:46:23 2018

@author: cesare
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash()

df = pd.read_csv(
  'https://raw.githubusercontent.com/charleyferrari/CUNY_DATA_608/master/module4/Data/riverkeeper_data_2013.csv'
)

#the following allows for modification of the categorical EnteroCount to numeric.

df['EnteroCount'].replace(to_replace = "<1", value = 0, inplace = True)
df['EnteroCount'].replace(to_replace = "<10", value = 5, inplace = True)
df['EnteroCount'].replace(to_replace = ">2420", value = 2430, inplace = True)
df['EnteroCount'].replace(to_replace = ">24196", value = 24200, inplace = True)
df['EnteroCount'] = pd.to_numeric(df['EnteroCount'])

# df2 = pd.read_csv(
#     'https://gist.githubusercontent.com/chriddyp/'
#     'cb5392c35661370d95f300086accea51/raw/'
#     '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
#     'indicators.csv')

#create unique values for callback.
Site = df['Site'].unique()
Dates = df['Date'].unique()

app.layout = html.Div([
    html.Div([
        html.P('Please pick the two sites you wish to compare from the drop down below.  Log scales used to show relativeity and remove skewness.'),
        html.Div([
            
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in Site],
                value='Bethlehem Launch Ramp'
            )
            # ,
            # dcc.RadioItems(
            #     id='xaxis-type',
            #     options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            #     value='Linear',
            #     labelStyle={'display': 'inline-block'}
            # )
        ],
        style={'width': '40%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in Site],
                value='Hudson above Mohawk River'
            )
            # ,
            # dcc.RadioItems(
            #     id='yaxis-type',
            #     options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            #     value='Linear',
            #     labelStyle={'display': 'inline-block'}
            # )
        ],style={'width': '40%', 'float': 'right', 'display': 'inline-block'}),
            html.P(''),
    ]),

    dcc.Graph(id='indicator-graphic'),
    html.P('Note: Black dots indicate the average EnteroCount vs. FourDayRainTotal for all other non chosen sites.  Log scales chosen to ensure relative correlations can be drawn.'),
    html.P('Created by Cesar L. Espitia for Data 608 Spring 2018.  Project 4 Question 2 submission.')
    # ,
    # ,

    # dcc.Slider(
    #     id='year--slider',
    #     min=df['Date'].min(),
    #     max=df['Date'].max(),
    #     value=df['Date'].max(),
    #     step=None,
    #     marks={str(year): str(year) for year in df['Date'].unique()}
    # )
])

@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value')
#     ,
#     dash.dependencies.Input('date-column','value')
#     # ,
     # dash.dependencies.Input('xaxis-type', 'value'),
     # dash.dependencies.Input('yaxis-type', 'value')
     # ,
     # dash.dependencies.Input('year--slider', 'value')
     ])
def update_graph(xaxis_column_name, yaxis_column_name
# ,
#                  xaxis_type, yaxis_type
                 # ,
                 # year_value
                 ):
    
    #dff = df[df['Date'] == date_column_value]
    dff=df.copy()
    dfo = df[~df['Site'].isin([xaxis_column_name, yaxis_column_name])]
    dfox = dfo['EnteroCount'].groupby(df['Date']).mean()
    dfoy = dfo['FourDayRainTotal'].groupby(df['Date']).mean()

    return {
        'data': [
          go.Scatter(
            # x=dff[dff['Site'] == xaxis_column_name]['Value'],
            # y=dff[dff['Site'] == yaxis_column_name]['Value'],
            # text=dff[dff['Site'] == yaxis_column_name]['Country Name'],
            x=dfox,
            y=dfoy,
            #text=df[df['Site'] == yaxis_column_name]['Date'],
            mode='markers',
            name="All Other Sites",
            marker={
                'size': 7,
                'color':'black',
                'opacity': 1.0,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
        go.Scatter(
            # x=dff[dff['Site'] == xaxis_column_name]['Value'],
            # y=dff[dff['Site'] == yaxis_column_name]['Value'],
            # text=dff[dff['Site'] == yaxis_column_name]['Country Name'],
            x=dff[dff['Site'] == xaxis_column_name]['EnteroCount'],
            y=dff[dff['Site'] == xaxis_column_name]['FourDayRainTotal'],
            #text=df[df['Site'] == yaxis_column_name]['Date'],
            mode='markers',
            name = xaxis_column_name,
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ),
          go.Scatter(
            # x=dff[dff['Site'] == xaxis_column_name]['Value'],
            # y=dff[dff['Site'] == yaxis_column_name]['Value'],
            # text=dff[dff['Site'] == yaxis_column_name]['Country Name'],
            x=dff[dff['Site'] == yaxis_column_name]['EnteroCount'],
            y=dff[dff['Site'] == yaxis_column_name]['FourDayRainTotal'],
            #text=df[df['Site'] == yaxis_column_name]['Date'],
            mode='markers',
            name=yaxis_column_name,
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )
        ],
        'layout': go.Layout(
            xaxis={
                'title': 'EnteroCount',
                'type': 'log'
            },
            yaxis={
                'title': 'FourDayRainTotal',
                'type': 'log'
            },
            margin={'l': 40, 'b': 20, 't': 10, 'r': 0},
            hovermode='closest'
#            ,
#            legend=dict(orientation="h",)
        )
    }


if __name__ == '__main__':
    app.run_server()
