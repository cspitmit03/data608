#Cesar Espitia Data 608 Final Project

#Setup Environment
#   Dash framework used to develop website along with plotly objects
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import random
import pandas as pd
import numpy as np

#zipfile items loaded to be able to read large zip file from US data website without having user download the file.
import zipfile
pd.options.display.float_format = '{:20,.2f}'.format
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

#OPENNING DATASET
#   Please note that dataset may change, please go to usa spending to determine newest dataset and structure
#   Website with file download is located at
#   https://www.usaspending.gov/#/download_center/award_data_archive
url = urlopen("https://s3-us-gov-west-1.amazonaws.com/usaspending-monthly-downloads/2018_all_Contracts_Full_20180415.zip")
zf = ZipFile(BytesIO(url.read()))

#SET FILE Names (this may need to be reviewed when files change
csv1 = 'contracts_prime_transactions_1.csv'
csv2 = 'contracts_prime_transactions_2.csv'

#Dataset has over 1M records which is memory and time consuming.  In order to be able a random sample, the following sampling method was employed:
#   1. determine the number of lines
num_lines = sum(1 for l in zf.open(csv1))
#   2. Sample size - in this case ~10%
size = int(num_lines / 10)
#   3. The row indices to skip
skip_idx = random.sample(range(1, num_lines), num_lines - size)

#     4. Read in first part of the data.
temp1 = pd.read_csv(zf.open(csv1), skiprows=skip_idx, low_memory=False)

#REPEAT THE ABOVE FOR THE SECOND CSV FILE.
num_lines = sum(1 for l in zf.open(csv2))
size = int(num_lines / 10)
skip_idx = random.sample(range(1, num_lines), num_lines - size)
temp2 = pd.read_csv(zf.open(csv2), skiprows=skip_idx, low_memory=False)

#COMBINE BOTH INTO ONE MASSIVE DATAFRAME
FFdata = pd.concat([temp1, temp2])


#DATA CLEANUP
#   The data had a bit of incomplete cases as was determined by looking at the Award ID in the datase.  When the Award ID was equal to 't', this means the contract
#   was never awarded and in our case it considered an incomplete case and removed.
#   drop data that are negative values and those that do not have an award ID
df = FFdata[FFdata.award_id_piid != 't']
df = df[df.recipient_country_name == 'UNITED STATES']
#   The second clean up was based upon the actual value of the contract.  The contract had to have a value of at least $1 USD for it to be considered a part of this exercise.
df = df[df.base_and_exercised_options_value >0 ]


#select all minority columns plus agency awarding, contract value, state of recipient among other factors of interest
df1 = df.iloc[:,[8,9,20,22,41,76,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180]]


df1list = list(df1.iloc[:,5:24].columns.values)

df1 = df1.applymap(lambda x: 1 if x == 't' else x)
df1 = df1.applymap(lambda x: 0 if x == 'f' else x)

#convert t and f (True and False) to 1 and 0 and coerce to numeric for summation
cols = df1list
df1[cols] = df1[cols].apply(pd.to_numeric, errors='coerce', axis=1)
df1['sum']=df1.iloc[:,6:25].sum(axis=1)
df1 = df1.sort_values('sum', ascending=[False])
df1['minority'] = np.where(df1['sum']>0, 'Minority', 'Non-Minority')
df1['funding_agency_name'] = df1['funding_agency_name'].str.split('(', 1).str[0].str.title()+' ('+df1['funding_agency_name'].str.split('(', 1).str[1]
df2 = df1

#generate agency values for drop down list
agency_options = df1['funding_agency_name'].unique()



#Data for Graph 3
#   This data explaines what minority business obtained funds for the selected agency.
df2 = df2.iloc[:,0:25]
idx = list(df2.iloc[:,0:6].columns.values)
df3 = df2.set_index(idx)
df4 = df3.stack(dropna=False)
df4 = df4.reset_index()
df4 = df4[df4[0]>0]
df5 = df4.groupby(['funding_agency_name','recipient_state_name','level_6'])[["base_and_exercised_options_value"]].mean()
df5 = df5.reset_index()
df5['level_6'] = df5['level_6'].str.split('_', 2).str[0]+' '+df5['level_6'].str.split('_', 2).str[1]
df5['level_6'] = df5['level_6'].str.replace("women owned","woman owned")
df5['level_6'] = df5['level_6'].str.replace("other minority","minority owned")
df5['level_6'] = df5['level_6'].str.replace("american indian","native american")
df5['level_6'] = df5['level_6'].str.replace("indian tribe","native american")
df5['level_6'] = df5['level_6'].str.replace("tribally owned","native american")
#df5['level_6'] = df5['level_6'].str.title()
df5 = df5.sort_values(by=['base_and_exercised_options_value'], ascending=[False])
df5['level_6'] = df5['level_6'].str.title()

#Data for Graph 4
#   This data shows the overall spending by minority vs non-minority for all agencies in the dataset.
all = df1.iloc[:,[0,26]]
all = all.groupby(['minority']).sum()
all = all.reset_index()

#Data for Graph 5
#   This data shows the overall spending by minority vs non-minority for all agencies in the dataset.
allm = df1.iloc[:,[0,3,26]]
allm = allm.groupby(['funding_agency_name','minority']).sum()
allm = allm.reset_index()
allmt = allm.sort_values(by=['base_and_exercised_options_value','minority'],ascending=[False,False])[allm['base_and_exercised_options_value']>1000000]
allmt = pd.DataFrame(allmt['funding_agency_name'].unique())
allmt.columns = ['funding_agency_name']
allm = pd.merge(allmt, allm, on='funding_agency_name')
allm = allm.sort_values(by=['base_and_exercised_options_value'], ascending=[True])
allm = pd.merge(allm,allm.groupby(by=['funding_agency_name'])[['base_and_exercised_options_value']].sum().reset_index(), on='funding_agency_name')
allm.columns = ['funding_agency_name','minority','base_and_exercised_options_value','percentage']
allm['percentage'] =  round(allm['base_and_exercised_options_value']/allm['percentage'],2)

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'American Samoa': 'AS',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Marshall Islands': 'MH',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Micronesia': 'FM',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'NORTHERN MARIANA ISLANDS': 'MP',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Palau': 'PA',
    'Puerto Rico': 'PW',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Minor Outlying Islands': 'UM',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'VIRGIN ISLANDS OF THE U.S.': 'VI',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Guam': 'GU',
    'Wisconsin': 'WI',
    'ARMED FORCES - PACIFIC': 'AP',
    'Wyoming': 'WY'
}
us_state_abbrev = {k.upper() if isinstance(k, str) else k: v.upper() if isinstance(v, str) else v for k,v in us_state_abbrev.items()}

##Data for US Map
df1 = df1.dropna(subset=['recipient_state_name'])
df1['recipient_state_name'] = df1['recipient_state_name'].apply(lambda x: us_state_abbrev[x])
dfmap = df1[['funding_agency_name','minority','recipient_state_name','base_and_exercised_options_value']]
zz = dfmap.groupby(['funding_agency_name','minority','recipient_state_name'])[['base_and_exercised_options_value']].sum()
dfmap = dfmap.groupby(['funding_agency_name','minority','recipient_state_name'])[['base_and_exercised_options_value']].sum().unstack('minority')
dfmap.columns = ['Minority','Non-Minority']
dfmap = dfmap.fillna(0)
dfmap = dfmap.reset_index()


#create bins for bivariate map
z=pd.DataFrame(zz.groupby(by=['minority']).describe())
bins = [z.iloc[0,3],z.iloc[0,4],z.iloc[0,5],z.iloc[0,6],z.iloc[0,7]]
#bins = [z.iloc[0,7],z.iloc[0,6],z.iloc[0,5],z.iloc[0,4],z.iloc[0,3]]
#labels=[-4,-3,-2,-1]
#labels = [-1,-2,-3,-4]
labels = [1,2,3,4]
dfmap['biMx'] = pd.cut(dfmap['Minority'], bins=bins, labels = labels)

bins = [z.iloc[1,3],z.iloc[1,4],z.iloc[1,5],z.iloc[1,6],z.iloc[1,7]]
labels = [10,100,1000,10000]
#labels = [1,2,3,4]
dfmap['biNMx'] = pd.cut(dfmap['Non-Minority'], bins=bins, labels = labels)


dfmap['biMx']=pd.to_numeric(dfmap['biMx'])
dfmap['biNMx']=pd.to_numeric(dfmap['biNMx'])
dfmap[['biMx','biNMx']] = dfmap[['biMx','biNMx']].fillna(0)
dfmap['concat3']=dfmap.biMx*dfmap.biNMx



def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app = dash.Dash()

app.layout = html.Div([
    html.Div([
            html.H1(
                'Government Fund Allocations between Business Groups',
            ),
            html.H3(
                'Contract Values Awarded to Minority Owned Small Business (MOSB) Groups (Q3 2017 and Q1 2018)',
            )
            ], 
            style={'width': '100%', 'float': 'center', 'display': 'inline-block', 'borderBottom': 'thin grey solid',
        'padding': '5px 5px'}
            ),
    html.P(''),
    html.P(''),
    html.Div(
            [
            html.Div([
            html.H3('Introduction'),
            html.H6('Government contracts are a lucrative business in the US.  In 2017, the government spent $3.98 trillion (source: https://www.usaspending.gov/#/). The government spends billions in contracts across various agencies under the federal branch.  This does not include funds that are funnelled back to the states through state and local grants. These contracts include purchases of items (ammunition, machinery) to consulting services. Companies have the opportunity to submit bids in hopes of getting the some of these potentially lucrative contracts.'),    
            html.P(''),            
            html.P(''), 
            html.H6('The focus of this app is to highlight how underrepresented companies (Women, Native American, Disabled, Hispanic, African American among others) compare to larger predominantly Anglo owned and ran companies. Companies that are a part of this designation (i.e. had a callout column in the dataset) will be designed as minority owned and will be referred to as Minority and all others as Non-Minority.'),
            html.H6(''),
            html.H6('The original dataset had two files almost 1.5 GB in size.  The full dataset had the following information:'),
            html.Div(
            [
                    html.Table(
                        [
                            html.Tr( [html.Th("Recipient Designation"), html.Th("Count"), html.Th("All Options"), html.Th("Exercised Options")] )
                        ] +
                        [
                            html.Tr( [html.Td("Minority"), html.Td("185,995"), html.Td("2,495,650,514,426.82"), html.Td("18,922,884,624.12")] ),
                            html.Tr( [html.Td("Non-Minority"), html.Td("933,260"), html.Td("2,290,596,091,995.63"), html.Td("131,959,104,917.72")] )
                        ]
                    )
                    ],style={'width': '100%', 'align': 'center'}
                    ),
            html.P(''),
            html.H6('From above it can be seen that there is a $2.5 T in potential max contract sizes for minority designated businesses and $2.3 T for non-minority business which is close to a 50/50 split, however, the exercised value of the contracts shows $18.9 B in exercised max contract sizes for minority designated businesses and $132.0 B for non-minority business which is a 13/87 split. For the purpsoes of this app and analysis the actual exercised options will be used for this analysis. '),
            html.H6('In order to make it efficient and to reduce load times of the app, only 10% of the dataset was loaded directly in memory using the Zipfile functions in python.   US recipients were also only used to focus the analysis on a domestic-centric point of view.  This means that approximately 13-16 B worth of contracts will be used everytime the data is loaded.')
            ], className="seven columns"),
    
            html.Div([
            html.H3('Fig 1. Awarded Contracts for All Federal Agencies ($USD M)'),
            dcc.Graph(id='site-graph5')
            ], className="five columns"),
            ], className="row"),
    html.H3('Fig 2.  Contracts Awarded by Business Designation for Top 30 Agencies ($USD and % Percentage)'),
    html.Div(
            [
            html.Div([
            html.H3(' '),
            dcc.Graph(id='site-graph4')
            ], className="six columns"),
                    
            html.Div([
            html.H3(' '),
            dcc.Graph(id='site-graphpercent')
            ], className="six columns"),
            
            ], className="row"
            ),
    html.Div(
            [html.H3(' ')
            ], 
            style={'width': '100%', 'float': 'center', 'display': 'inline-block', 'borderBottom': 'thin grey solid',
                   'padding': '5px 5px'}
            ),
    html.H6('The above Figure 2 paints an interesting picture.  It can be hard to see on the left side of Figure 2 that the Department of Defense which spends the most on contracts has a unbalanced ratio of funds going to non-minority businesses.  By having the contract value (log scale) side-by-side with the percentage split, the disparity between awarding contracts between these groups becomes more apparent.  What is more intersting is that only 7 of the top 30 federal agencies gave 50% or more of the funds to MOSBs.  What is surpising is that NASA is an unablanced agency considering their outward PR campaign for diversity and inclusion and promoting STEM for all children.'),
    html.Div([
            html.H3(
                'Please select a funding agency to for review.',
            ),
            dcc.Dropdown(
            id="Agency",
            options=[{
                'label': i,
                'value': i
            } for i in agency_options],
            value=agency_options[1])
            ], 
            style={'width': '100%', 'float': 'center', 'display': 'inline-block', 'borderBottom': 'thin grey solid',
        'padding': '5px 5px'}
            ),   
    html.P(''), 
    html.H6('Figure 3 and Figure 4 show the specific agency data.  The pie chart shows the overall exercised vaues of the awarded contracts broken up by business designation.  The US map shows which company designation received most of the funds for this particular agency by state (binary minority vs non-minority) using data quartiles. Minority designated businesses were ranked with negative values and Non-Minority designated busiensses were ranked with positive values.'),
    html.H6('Figure 5 provides a glimpse into the average contract value by minoirty group for the selected agency. Companies that are a part of this designation (i.e. had a callout column in the dataset) will be designed as minority owned and will be referred to as Minority and all others as Non-Minority.  Figure 6 shows the overall distribution of all the awarded contracts for the selected agency, this view helps see the spread of the data in a similar form that a histogram may.'),
    html.Div(
            [
            html.Div([
            html.H3('Fig 3. Awarded Contracts for Selected Agency ($USD M)'),
            dcc.Graph(id='site-graphagencypie')
            ], className="six columns"),
    
            html.Div([
            html.H3('Fig 4. State Breakdown of MOSB Contract Awards for Selected Agency ($USD M)'),
            dcc.Graph(id='site-graphmap')
            ], className="six columns"),    

            ], className="row"),
    html.Div(
        [
        html.Div([
        html.H3('Fig 5. Average Contract Value per Minority Group Awarded for Selected Agency'),
        dcc.Graph(id='site-graph3')
        ], className="six columns"),

        html.Div([
        html.H3('Fig 6. Contract Value Box Plots per Business Designation ($ USD)'),
        dcc.Graph(id='site-graphBP')
        ], className="six columns"),    

        ], className="row"),
#   html.H3('Fig 5. Average Contract Value per Minority Group Awarded for Selected Agency'),
#   dcc.Graph(id='site-graph3'),
#   dcc.Graph(id='site-graphBP'),
#   dcc.Graph(id='site-graph4'),
#   dcc.Graph(id='site-graph5'),
#   dcc.Graph(id='site-graph2'),
#   dcc.Graph(id='table-container'),
#   dcc.Graph(id='site-graph'),
    html.P(''),
    html.H3('Conclusion'),
    html.H6('The information found in the USA spending website provided an interesting glimpse to the businesses practices of our federal government.  The funnel analysis from nation-wide to agency level also shows interesting trends that allows the user to draw their own conclusions of the practices of each agency.  Overall, the majority of US agencies show an unbalanced awarding beahvior of contracts to non-MOSBs.  Those that do award contracts to MOSBs are not the larger agencies (i.e. DOD, DOJ) but smaller ones.  This might be a function of just the availability of large companies that are designated MOSBs vs traditional companies like ARUP, Jacobs Engineering and can therefore skew the data indirectly.'),
    html.P(''),
    html.H3('Future Considerations'),
    html.H6('There is one caveat to the analysis, what is not availabel in the data is the submission process and determining how many applications from each business designation actually submitted a proposal.  This is important because if the information was available it could provide a weight to the information to further highlight the awarding behavior of the agencies.'),
    html.H6('In addition, the data does have other interesting data that could be used for analysis like what was purchased/contracted with the recipient, the NAICS code of the business, and even the sub-agency that ultimately was repsonsible for the oversight of the contract.'),
    html.P('Created by Cesar L. Espitia for Data 608 Spring 2018.  Final Project App Submission.')
])

    
@app.callback(
    dash.dependencies.Output('site-graphmap', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plot = dfmap[(dfmap['funding_agency_name'] == Agency)]
    
#    for col in dfmap.columns:
#        dfmap[col] = dfmap[col].astype(str)
    
    scl = [[0,"rgb(190,114,60)"],[0.25,"rgb(190,114,60)"],[0.5,"rgb(236,213,207)"],[0.75,"rgb(236,213,207)"],[1,"rgb(236,213,207)"]]
    
    #df_plot['text']=df['recipient_state_name] + ''Beef '+df['beef']+' Dairy '+df['dairy']
    
    data=[
            dict(
            type='choropleth',
            colorscale = scl,
            autocolorscale = False,
            #text = df_plot['text'],
            locations = df_plot['recipient_state_name'],
            z = df_plot['concat3'].astype(float),
            text = df_plot['concat3'],
            locationmode = 'USA-states',
            marker = dict(
                line = dict (
                    color = 'rgb(255,255,255)',
                    width = 2
                ) ),
            colorbar = dict(
                title = "Millions USD")
            )
            ]
    
    return {
        'data': data,
        'layout':
        go.Layout(
                dict(
                title = '',
                geo = dict(
                        scope='usa',
                        projection=dict( type='albers usa' ),
                        showlakes = True,
                        lakecolor = 'rgb(255, 255, 255)')
                        )
                )
    }

    
#This graph shows the value of funding for minority groups from the selected agency.
@app.callback(
    dash.dependencies.Output('site-graph3', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plot = df5[(df5['funding_agency_name'] == Agency)].groupby(by=['level_6'])[['base_and_exercised_options_value']].mean()
    df_plot = df_plot.reset_index()
    df_plot = df_plot.sort_values(by=['base_and_exercised_options_value'], ascending=[True])
    data=[
            go.Bar(x=df_plot['base_and_exercised_options_value'],
                   y=df_plot['level_6'],
                   orientation = 'h',
                   name='MOSBs',
                   marker = dict(
                            color = 'rgb(190,114,60)'
                            )
                   )
            ]    
    
    return {
        'data': data,
        'layout':
        go.Layout(
                barmode='stack',
                xaxis={'title': 'Contract Value (Log Scale)', 'type':'log'},
                height=600,
                margin={'l': 400, 'b': 50, 't': 10, 'r': 10}
            )
    }
        
#This is a box plot to show the distribution of each business designation for the agency.
@app.callback(
    dash.dependencies.Output('site-graphBP', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plotm = df1[(df1['minority'] == 'Minority') & (df1['funding_agency_name'] == Agency)]
    df_plotmn = df1[(df1['minority'] == 'Non-Minority')& (df1['funding_agency_name'] == Agency)]
    data=[
            go.Box(y=df_plotm['base_and_exercised_options_value'], 
                    #x=df_plotm['base_and_exercised_options_value'],
                     #orientation = 'h',
                     name='Minority',
                    boxpoints = 'all',
                    jitter = 0.3,
                    marker = dict(
                            color = 'rgb(190,114,60)'
                            ),
                            boxmean=True
                    ),
            go.Box(y=df_plotmn['base_and_exercised_options_value'], 
                    #x=df_plotmn['base_and_exercised_options_value'],
                     #orientation = 'h',
                     name='Non-Minority',
                    boxpoints = 'all',
                    jitter = 0.3,
                    marker = dict(
                            color = 'rgb(236,213,207)'
                            ),
                            boxmean=True
                    )
            ]    
    
    return {
        'data': data,
                'layout':
        go.Layout(
                yaxis={'title': 'Contract Value (Log Scale)', 'type':'log'},
                height=600,
                margin={'l': 100, 'b': 50, 't': 10, 'r': 10}
            )
    }
        
        
#top 30 agency chart
@app.callback(
    dash.dependencies.Output('site-graph4', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plotm = allm[(allm['minority'] == 'Minority')]
    df_plotmn = allm[(allm['minority'] == 'Non-Minority')]
    data=[
            go.Bar(y=df_plotm['funding_agency_name'], 
                    x=df_plotm['base_and_exercised_options_value'],
                     orientation = 'h',
                     name='Minority',
                    marker = dict(
                            color = 'rgb(190,114,60)'
                            )
                    ),
            go.Bar(y=df_plotmn['funding_agency_name'], 
                    x=df_plotmn['base_and_exercised_options_value'],
                     orientation = 'h',
                     name='Non-Minority',
                    marker = dict(
                            color = 'rgb(236,213,207)'
                            )
                    )
            ]    
    
    return {
        'data': data,
        'layout':
        go.Layout(
                barmode='stack',
                xaxis={'title': 'Contract Value (Log Scale)', 'type': 'log'},
                height=700,
                showlegend = False,
                margin={'l': 500, 'b': 50, 't': 10, 'r': 10}
            )
    }
        
#top 30 agency percentage graph
@app.callback(
    dash.dependencies.Output('site-graphpercent', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plotm = allm[(allm['minority'] == 'Minority')]
    df_plotmn = allm[(allm['minority'] == 'Non-Minority')]
    data=[
            go.Bar(y=df_plotm['funding_agency_name'], 
                    x=df_plotm['percentage'],
                     orientation = 'h',
                     name='Minority',
                    marker = dict(
                            color = 'rgb(190,114,60)'
                            )
                    ),
            go.Bar(y=df_plotmn['funding_agency_name'], 
                    x=df_plotmn['percentage'],
                     orientation = 'h',
                     name='Non-Minority',
                    marker = dict(
                            color = 'rgb(236,213,207)'
                            )
                    )
            ]    
    
    return {
        'data': data,
        'layout':
        go.Layout(
                barmode='stack',
                xaxis={'title': 'Percentage by Group'},
                yaxis=dict(showticklabels=False),
                height=700,
                margin={'l': 1, 'b': 50, 't': 10, 'r': 10}
            )
    }


@app.callback(
    dash.dependencies.Output('site-graph5', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plotm = all.copy()
    data=[

        go.Pie(labels=df_plotm['minority'], values=round(df_plotm['base_and_exercised_options_value']/1000000,0),
               hoverinfo='label+percent', textinfo='value',
               textfont=dict(size=20),
               marker=dict(colors=['rgb(190,114,60)', 'rgb(236,213,207)'],
                           ))
            ]    
    
    return {
        'data': data,
        'layout':
            go.Layout(
                    height=700
                    )
    }


#Agency selceted pie chart
@app.callback(
    dash.dependencies.Output('site-graphagencypie', 'figure'),
    [dash.dependencies.Input('Agency', 'value')])
def update_graph(Agency):
    df_plotm = allm[(allm['funding_agency_name'] == Agency)].groupby(by=['minority'])[['base_and_exercised_options_value']].sum()
    df_plotm = df_plotm.reset_index()
    #df1[['funding_agency_name','minority','recipient_state_name','base_and_all_options_value']]
    data=[

        go.Pie(labels=df_plotm['minority'], values=round(df_plotm['base_and_exercised_options_value']/1000000,2),
               hoverinfo='label+percent', textinfo='value',
               textfont=dict(size=20),
               marker=dict(colors=['rgb(190,114,60)','rgb(236,213,207)'],
                           ))
            ]    
    
    return {
        'data': data
    }

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


if __name__ == '__main__':
    app.run_server(debug=True)