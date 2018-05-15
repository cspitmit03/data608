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
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from scipy.stats import gmean


df = pd.read_csv(
    "riverkeeper_data_2013.csv"
)
#categories = df['Site'].unique()
#categories.sort()
#mux = pd.MultiIndex.from_product([df['Date'].unique(), categories], names=('Date','Site'))
#df = df.set_index(['Date','Site']).reindex(mux, fill_value=0).swaplevel(0,1).reset_index()
df['EnteroCount'].replace(to_replace = "<1", value = 0, inplace = True)
df['EnteroCount'].replace(to_replace = "<10", value = 5, inplace = True)
df['EnteroCount'].replace(to_replace = ">2420", value = 2430, inplace = True)
df['EnteroCount'].replace(to_replace = ">24196", value = 24200, inplace = True)
df['EnteroCount'] = pd.to_numeric(df['EnteroCount'],errors='coerce')
df['EnteroCount'].fillna(0, inplace=True)
df['EPAsafe'] = np.where(df['EnteroCount']>=50, 'notsafe', 'safe')
#convert date column from series to datetime
#df['Date'] = pd.to_datetime(df['Date'],format='%m/%d/%Y')
df=df.sort_values(['EnteroCount'], ascending=[True])
date_options = df["Date"].unique()
df['geom'] = df.groupby('Site').EnteroCount.apply(lambda group: group.product() ** (1 / float(len(group))))
df['swim'] = np.where(
    (df.groupby('Site').EnteroCount.transform(max) > 110) |
    (df.groupby('Site').EnteroCount.transform(lambda group: gmean(group.nlargest(5))) > 30), 
    'unacceptable', 'acceptable')


app = dash.Dash()

app.layout = html.Div([
    html.H2("Site Launch Forecast"),
    html.Div(
        [
            dcc.Dropdown(
                id="Date",
                options=[{
                    'label': i,
                    'value': i
                } for i in date_options],
                value='Available Dates'),
#        dcc.DatePickerSingle(
#                id='Date',
#                date=date_options,
#                value=min(date_options)
#)
        ],
        style={'width': '25%',
               'display': 'inline-block'}),
    dcc.Graph(id='site-graph'),
])


@app.callback(
    dash.dependencies.Output('site-graph', 'figure'),
    [dash.dependencies.Input('Date', 'value')])
def update_graph(Date):
    if Date == min(date_options):
        df_plot = df.copy()
    else:
        df_plot = df[df['Date'] == Date]

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
    trace1 = go.Bar(y=df_plot.Site, 
                    x=df_plot.EnteroCount,
                     orientation = 'h',
                    marker = dict(color=color.tolist())
                    )

    return {
        'data': [trace1],
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
                        title='AXIS TITLE',
                        titlefont=dict(
                                family='Arial, sans-serif',
                                size=8,
                                color='lightgrey'
                                ),
                                showticklabels=True,
                                tickangle=0,
                                tickfont=dict(
                                        family='Old Standard TT, serif',
                                        size=14,
                                        color='black'
                                        )
                        )
            )
    }

if __name__ == '__main__':
    app.run_server(debug=True)