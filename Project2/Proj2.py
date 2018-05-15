#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 07:59:36 2018

@author: cesare
"""

import datashader as ds
import datashader.transfer_functions as tf
import datashader.glyphs
from datashader import reductions
from datashader.core import bypixel
from datashader.utils import lnglat_to_meters as webm, export_image
from datashader.colors import colormap_select, Greys9, viridis, inferno
import copy


from pyproj import Proj, transform
import numpy as np
import pandas as pd
import urllib
import json
import datetime
import colorlover as cl

import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools

from shapely.geometry import Point, Polygon, shape
# In order to get shapley, you'll need to run [pip install shapely.geometry] from your terminal

from functools import partial

from IPython.display import GeoJSON


bk = pd.read_csv('PLUTO17v1.1/BK2017V11.csv')
bx = pd.read_csv('PLUTO17v1.1/BX2017V11.csv')
mn = pd.read_csv('PLUTO17v1.1/MN2017V11.csv')
qn = pd.read_csv('PLUTO17v1.1/QN2017V11.csv')
si = pd.read_csv('PLUTO17v1.1/SI2017V11.csv')

ny = pd.concat([bk, bx, mn, qn, si], ignore_index=True)

# Getting rid of some outliers
ny = ny[(ny['YearBuilt'] > 1850) & (ny['YearBuilt'] < 2020) & (ny['NumFloors'] != 0)]

ny.head()

wgs84 = Proj("+proj=longlat +ellps=GRS80 +datum=NAD83 +no_defs")
nyli = Proj("+proj=lcc +lat_1=40.66666666666666 +lat_2=41.03333333333333 +lat_0=40.16666666666666 +lon_0=-74 +x_0=300000 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs")
ny['XCoord'] = 0.3048*ny['XCoord']
ny['YCoord'] = 0.3048*ny['YCoord']
ny['lon'], ny['lat'] = transform(nyli, wgs84, ny['XCoord'].values, ny['YCoord'].values)

ny = ny[(ny['lon'] < -60) & (ny['lon'] > -100) & (ny['lat'] < 60) & (ny['lat'] > 20)]

#Defining some helper functions for DataShader
background = "black"
export = partial(export_image, background = background, export_path="export")
cm = partial(colormap_select, reverse=(background!="black"))

trace = go.Scatter(
    # I'm choosing BBL here because I know it's a unique key.
    x = ny.groupby('YearBuilt').count()['BBL'].index,
    y = ny.groupby('YearBuilt').count()['BBL']
)

layout = go.Layout(
    xaxis = dict(title = 'Year Built'),
    yaxis = dict(title = 'Number of Lots Built')
)

fig = go.Figure(data = [trace], layout = layout)

py.plot(fig, filename = 'ny-year-built')

# Start your answer here, inserting more cells as you go along
ny.head()

#analysis of floors
n=pd.DataFrame(list(ny['NumFloors'].describe().transpose()))
n['log']=pd.DataFrame(list(ny['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,1]]
n['step1']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep1']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,3]]
n['step3']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep3']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,5]]
n['step5']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep5']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,7]]
n['step7']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep7']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,9]]
n['step9']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep9']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))


ny2 = ny[ny.logFloor >= n.iloc[1,11]]
n['step11']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep11']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))


ny2 = ny[ny.logFloor >= n.iloc[1,13]]
n['step13']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep13']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,15]]
n['step15']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep15']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

ny2 = ny[ny.logFloor >= n.iloc[1,17]]
n['step17']=pd.DataFrame(list(ny2['NumFloors'].describe().transpose()))
n['logstep17']=pd.DataFrame(list(ny2['logFloor'].describe().transpose()))

n

#with this data we will bin based upon the following method: mean for first few slices, then std deviation as it coalesces at 11, 
#then the balance will be by 2x the std deviation due to the decreasing number of counts.

bins = [0, 5, 10, 21, 32, 43, 54, 76, 98, 119]
labels = ['0-5','6-10','11-21','22-32','33-43','44-54','55-76','77-98','99-119']
ny['binned'] = pd.cut(ny['NumFloors'], bins=bins, labels = labels)

#data is also binned by year to get a better view using only std

bins = [1851, 1870, 1899, 1928, 1957, 1986, 2017]
labels = ['1851+','1871+','1900+','1929+','1958+','1987+']
ny['yearbinned'] = pd.cut(ny['YearBuilt'], bins=bins, labels = labels)

data = ny.groupby(['yearbinned', 'binned']).size().reset_index(name='count')
data

x0 = data.loc[data['yearbinned']=='1851+']
x1 = data.loc[data['yearbinned']=='1871+']
x2 = data.loc[data['yearbinned']=='1900+']
x3 = data.loc[data['yearbinned']=='1929+']
x4 = data.loc[data['yearbinned']=='1958+']
x5 = data.loc[data['yearbinned']=='1987+']

import plotly.plotly as py
import cufflinks as cf
import pandas as pd
import numpy as np

df = pd.DataFrame({'a': np.random.randn(1000) + 1,
                   'b': np.random.randn(1000),
                   'c': np.random.randn(1000) - 1})

df.iplot(kind='histogram', filename='cufflinks/basic-histogram')








### question 2

bins = [0, 7440,10192,14931,3211277000]
labels = [1,2,3,4]
ny['biAL'] = pd.cut(ny['AssessLand'], bins=bins, labels = labels)

bins = [0, 23288,30370,45619,6877263000]
labels = [10,20,30,40]
ny['biAT'] = pd.cut(ny['AssessTot'], bins=bins, labels = labels)

ny['concat']=ny.biAL.str.cat(ny.biAT)

ny['biAL2']=pd.to_numeric(ny['biAL'])
ny['biAT2']=pd.to_numeric(ny['biAT'])
ny['concat2']=ny.biAL2+ny.biAT2


bins = [0, 7440,10192,14931,3211277000]
labels = ['a','b','c','d']
ny['biALc'] = pd.cut(ny['AssessLand'], bins=bins, labels = labels)

bins = [0, 23288,30370,45619,6877263000]
labels = ['1','2','3','4']
ny['biATc'] = pd.cut(ny['AssessTot'], bins=bins, labels = labels)


ny['concat3']=ny.biALc.str.cat(ny.biATc)

ny['new']=pd.factorize(ny['concat3'])

x0 = ny.loc[ny['ZipCode']==11365]


ny1 = ny[ny["NumFloors"] < 105] # There are erroneous entries with 114 and 119 stories.
ny1["YearBuilt"] = np.floor(ny1["YearBuilt"]/10)*10
ny10s = ny1[(ny1.NumFloors >= 10) & (ny1.NumFloors <= 20) & (ny1.YearBuilt < 1900)]
ny20s = ny1[(ny1.NumFloors >= 21) & (ny1.NumFloors <= 30)& (ny1.YearBuilt < 1920)]
ny30s = ny1[(ny1.NumFloors >= 31) & (ny1.NumFloors <= 61)& (ny1.YearBuilt < 1930)]
ny40s = ny1[(ny1.NumFloors >= 62) & (ny1.NumFloors <= 77) & (ny1.YearBuilt < 1970) & (ny1.YearBuilt > 1910)] 
#140 Franklin Street is listed as being built in 1910 and having 65 stories, but this doesn't match historical records
ny50s = ny1[(ny1.NumFloors >= 78) & (ny1.NumFloors <= 102) & (ny1.YearBuilt < 1970)]
ny60s = ny1[(ny1.NumFloors > 102)]