#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 08:57:22 2018

@author: cesare
For Data 608 Project 4

"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from scipy.stats import gmean


df = pd.read_csv(
    "riverkeeper_data_2013.csv", parse_dates=['Date']
)
df['Date']=df['Date'].dt.strftime('%Y-%m-%d')
df['EnteroCount'].replace(to_replace = "<1", value = 0, inplace = True)
df['EnteroCount'].replace(to_replace = "<10", value = 5, inplace = True)
df['EnteroCount'].replace(to_replace = ">2420", value = 2430, inplace = True)
df['EnteroCount'].replace(to_replace = ">24196", value = 24200, inplace = True)
df['EnteroCount'] = pd.to_numeric(df['EnteroCount'],errors='coerce')
df['EnteroCount'].fillna(0, inplace=True)
df['EPAsafe'] = np.where(df['EnteroCount']>=50, 'notsafe', 'safe')

#convert date column from series to datetime
df=df.sort_values(['EnteroCount'], ascending=[False])
#df2 = df.sort_value(['Date'], ascending=[True])
date_options = df['Date'].unique()
date_options.sort()
#df['geom'] = df.groupby('Site').EnteroCount.apply(lambda group: group.product() ** (1 / float(len(group))))
df['swim'] = np.where(
    (df.groupby('Site').EnteroCount.transform(max) > 110) |
    (df.groupby('Site').EnteroCount.transform(lambda group: gmean(group.nlargest(5))) > 30), 
    'unacceptable', 'acceptable')


app = dash.Dash()

app.layout = html.Div([
        html.P('Please pick a date from below.  Note that sites colored in green are recommended launch sites.  Overall this are far and few.'),
        html.P('EPA Line shows the EPA Guideline acceptable values, the Mean line is just the average count on that particular day.'),
    html.Div(
        [
            dcc.Dropdown(
                id="Date",
                options=[{
                    'label': i,
                    'value': i
                } for i in date_options],
                value='Available Dates')
#        dcc.DatePickerSingle(
#                id='Date',
#                date=date_options,
#                value=min(date_options)
#)
        ],

        style={'width': '25%',
               'display': 'inline-block'}),
    dcc.Graph(id='site-graph'),
    html.P('Created by Cesar L. Espitia for Data 608 Spring 2018.  Project 4 Submission Question 1.')
])


@app.callback(
    dash.dependencies.Output('site-graph', 'figure'),
    [dash.dependencies.Input('Date', 'value')])
def update_graph(Date):
    if Date == min(date_options):
        df_plot = df.copy()
    else:
        df_plot = df[df['Date'] == Date]
        df_date = df_plot.groupby('Date').mean()
        df_date['Date']=df_date.index
        df_date = pd.merge(df_date, df_plot, on='Date')
        df_date['oneten']=110
        
#    pv = pd.pivot_table(
#        df_plot,
#        index=['Date'],
#        columns=["Site"],
#        values=['EnteroCount'],
#        aggfunc=sum,
#        fill_value=0)
#    myy = df_plot.EnteroCount
    myy = df_plot.swim
    color = np.array(['rgb(255,255,255)']*myy.shape[0])
    color[myy=='acceptable']='rgb(0, 204, 0)'
    color[myy=='unacceptable']='rgb(204,204, 205)'    
#    color[myy<=110]='rgb(0, 204, 0)'
#    color[myy>110]='rgb(204,204, 205)'
    data=[
            go.Bar(y=df_plot.Site, 
                    x=df_plot.EnteroCount,
                     orientation = 'h',
                     name='DailySiteCounts',
                    marker = dict(color=color.tolist())
                    ),
            go.Scatter(y=df_date.Site,
                    x=df_date.EnteroCount_x,
                    name='MeanEnteroCount'
            ),
            go.Scatter(y=df_date.Site,
                    x=df_date.oneten,
                    name='EPALine',
            )]    
    
    return {
        'data': data,
        'layout':
        go.Layout(
            title='EnterCount Information for {}'.format(Date),
            barmode='stack',
            autosize=False,
            width=1000,
            height=700,
            margin=go.Margin(
                    l=300,
                    r=50,
                    b=100,
                    t=100,
                    pad=4
                    ),  
            xaxis=dict(
                    title='EnteroCounts',
                    titlefont=dict(
                            family='Arial, sans-serif',
                            size=20,
                            color='lightgrey'
                            )
                    ),
                yaxis=dict(
                    title='Launch Site',
                    titlefont=dict(
                            family='Arial, sans-serif',
                            size=20,
                            color='lightgrey'
                            )
                        )
            )
    }

if __name__ == '__main__':
    app.run_server(debug=True)