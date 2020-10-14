import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ALL, State, MATCH
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import boto3
import itemSpecificCleanUp as iscu
import numpy as np
import seaborn as sns
import appGraphs as ag
import ast
import flask




# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = ["https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css",'https://codepen.io/chriddyp/pen/bWLwgP.css',
"https://code.jquery.com/jquery-3.2.1.min.js" ,"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"]

server = flask.Flask(__name__)
app = dash.Dash(external_stylesheets=external_stylesheets, server=server)
 
'''
s3 = boto3.client('s3')
s3.list_objects(Bucket = 'ebayfindingdata', Prefix = 'shopping/')

keys = [o['Key'] for o in s3.list_objects(Bucket = 'ebayfindingdata', Prefix = 'shopping')['Contents'] if '.csv' in o['Key']]
desc_keys = [o['Key'] for o in s3.list_objects(Bucket = 'ebayfindingdata', Prefix = 'description')['Contents'] if '.csv' in o['Key']]

df = pd.concat([pd.read_csv(s3.get_object(Bucket = 'ebayfindingdata', Key = k)['Body']) for k in keys[:2]])
desc_df = pd.concat([pd.read_csv(s3.get_object(Bucket = 'ebayfindingdata', Key = k)['Body']) for k in desc_keys[:2]])

df = df.join(desc_df.set_index('ItemID'), on = 'ItemID')

df = df[~df['ItemID'].duplicated()]
'''
df = pd.read_csv('data.csv')

df = cleanUpDf(df) 

available_indicators = ['Please Select...','ItemSpecifics-Type', 'ItemSpecifics-Brand', 'ItemSpecifics-Skill Level', 
'Condition', 'Model']


parent_hierarchy = ['ItemSpecifics-Brand','ItemSpecifics-Type', 'Model']
sunburst_fig = ag.sunburstFig(df, parent_hierarchy)
choropleth_fig = ag.choroplethFig(df)
scatter_fig = ag.scatterFig(df, "None")

app.layout = html.Div([
    # Row: Title
    html.Div([
        # Column: Title
        html.Div([
            html.H1("🎷🎷 Ebay Sax Listings 🎷🎷", className="text-center")
        ], className="col-md-12")
    ], className="row"),
    # Row: Scatter Chart + Selected Listing

    html.Div([
        # Scatter Graph and Dropdown
        html.Div([
            html.Div([
                html.H4([
                    "Scatter Chart",
                ], className="container_title"),
            ]),
            html.Div([
            # Dropdown Scatter Options
                html.Div([
                    dcc.Dropdown(
                        options = [{'label': x, 'value': x} for x in df['ItemSpecifics-Type'].unique() if x == x],
                        value = sorted([x for x in df['ItemSpecifics-Type'].unique() if x ==x]),
                        multi=True,
                        className = "col-md-6",
                        id = 'scatter-dropdown-type',
                        style = {'background':'rgb(53,53,53)', 'color':'white'}
                        
                    ),
                    dcc.Dropdown(
                        options = [{'label': x, 'value': x} for x in df['Condition'].unique() if x == x],
                        value = sorted([x for x in df['Condition'].unique() if x ==x]),
                        multi=True,
                        className = "col-md-6",
                        id = 'scatter-dropdown-condition',
                        style = {'background':'rgb(53,53,53)'}
                    ),
                ]),
                html.Div([
                    dcc.Dropdown(
                        options = [{'label': x, 'value': x} for x in df['ItemSpecifics-Brand'].unique() if x == x],
                        value = sorted([x for x in df['ItemSpecifics-Brand'].unique() if x ==x]),
                        multi=True,
                        className = "col-md-12",
                        id = 'scatter-dropdown-brand',
                        style = {'background':'rgb(53,53,53)'}
                    ),       
                ]),
            ], className = 'twelve columns pretty_container'),
            # Graph Dropdown
            html.Div([
                dcc.Graph(figure = scatter_fig, id = 'scatter-figure'),
                dcc.RadioItems(
                    id='scatter-color-selector',
                    options=[
                        {'label': 'Type', 'value': 'ItemSpecifics-Type'},
                        {'label': 'Brand', 'value': 'ItemSpecifics-Brand'},
                        {'label': 'Model', 'value': 'Model'},
                        {'label': 'Condition', 'value': 'Condition'},

                    ],
                    value='None',
                    labelStyle={'display': 'inline-block'},
                    style={"textAlign": "centre", 'margin-right': 10},
                )
            ], className = 'twelve columns pretty_container'),
        ], className = 'eight columns pretty_outer_container'),

        # Selected Sax Listing
        html.Div([
            html.Div([
                html.H4([
                    "Selected Sax Listing",
                ], className="container_title"),
            ]),
            html.Div([
                html.Div([
                    html.Button('<', id='left-image-click', n_clicks=0,style = dict(display='none')),
                    html.A(
                    id = 'saxophone-image'
                    ),
                    html.Button('>', id='right-image-click', n_clicks=0, style = dict(display='none'))],
                style={'textAlign': 'center'},
            ),
            ], className = 'twelve columns pretty_container'
            ),
        ], id = 'selected-sax-listing',
        className='four columns pretty_outer_container'),
    ], className = 'row'),     
    
    html.Div([
        html.Div([
            html.Div([
                html.H4([
                    "Sunburst Chart",
                ], className="container_title"),
            ]),
            # Sunburst Figure
            html.Div([
                dcc.Graph(figure = sunburst_fig, id = 'sunburst-figure')
            ],
            className='eight columns pretty_container'),
            # Sunburst Dropdown Options
            html.Div([
                html.Br(),
                html.H4('Add or Subtract Layers!'),
                html.Button('+', id='add-layer-button', n_clicks=0),
                html.Button('-', id='subtract-layer-button', n_clicks=0),
                html.Br(),
                html.H4('Select Layers!'),
                html.Div([
                    dcc.Dropdown(
                        id={
                            'type' : 'sunburst-layer-dropdown',
                            'index' : 1,  
                        },
                        options=[{'label': x, 'value': x} for x in available_indicators[1:]],
                        value='ItemSpecifics-Brand'
                    ),
                    dcc.Dropdown(
                        id={
                            'type' : 'sunburst-layer-dropdown',
                            'index' : 2,  
                        },
                        options=[{'label': x, 'value': x} for x in available_indicators],
                        value='ItemSpecifics-Type'
                    ),
                ], id = 'sunburst-drop-down',),
                dcc.RadioItems(
                    id='sunburst-color-selector',
                    options=[{'label': i, 'value': i} for i in ['Mean Price', 'Median Price', 'Count', 'None']],
                    value='None',
                    labelStyle={'display': 'inline-block'},
                    style={'marginBottom': '1em'}
                )
            ], className='four columns pretty_container'),
        ], className = 'six columns pretty_outer_container'),
        html.Div([
            html.Div([
                html.H4([
                    "World Map",
                ], className="container_title"),
            ]),
            html.Div([
                dcc.Graph(figure = choropleth_fig)
            ], className='twelve columns pretty_container'),
        ], className = 'six columns pretty_outer_container'),
    ], className="row"),

    # Row: Footer
    html.Div([
        html.Hr(),
        html.P([
            "Built with ",
            html.A("Dash", href="https://plot.ly/products/dash/"),
        ])      
    ], className="row",
        style={
            "textAlign": "center",
            "color": "Gray"
        })
], className="container-fluid")


@app.callback(Output('sunburst-drop-down', component_property='children'),
              [Input('add-layer-button', 'n_clicks'),
               Input('subtract-layer-button', 'n_clicks'),
               Input({'type': 'sunburst-layer-dropdown', 'index': ALL}, 'value')],
               [State('sunburst-drop-down','children')])
def updateSunburstDropDown(add, subtract, values, old_output):
    n_layers = 2 + add - subtract
    n_layers = min(n_layers, 5)
    n_layers = max(n_layers, 1)
    if n_layers > len(old_output):
        return old_output + [dcc.Dropdown(
                    id={
                        'type' : 'sunburst-layer-dropdown',
                        'index' : n_layers,},
                    options=[{'label': x, 'value': x} for x in available_indicators if x not in values],
                   )]

    else:
        return old_output[:n_layers]

@app.callback(Output({'type': 'sunburst-layer-dropdown', 'index': ALL}, 'options'),
            [Input({'type': 'sunburst-layer-dropdown', 'index': ALL}, 'value')])
def updateSunburstOptions(values):
    return [[{'label': x, 'value': x} for x in available_indicators if (x not in values) or (x == i)] for i in values]

@app.callback(Output('sunburst-figure', 'figure'),
              [Input({'type': 'sunburst-layer-dropdown', 'index': ALL}, 'value'),
               Input('sunburst-color-selector', 'value')])
def updateSunburst(values, color):
    parent_hierarchy = [x for x in values if x not in ['Please Select...', None]]
    return ag.sunburstFig(df, parent_hierarchy, color_agg = color)

@app.callback(Output('scatter-figure', 'figure'),
[Input('scatter-dropdown-type', 'value'),
Input('scatter-dropdown-brand', 'value'),
Input('scatter-dropdown-condition', 'value'),
Input('scatter-color-selector', 'value')
])
def updateScatter(types, brands, conditions, color):
    cond1 = df['ItemSpecifics-Type'].isin(types)
    cond2 = df['ItemSpecifics-Brand'].isin(brands)
    cond3 = df['Condition'].isin(conditions)
    return ag.scatterFig(df[(cond1)&(cond2)&(cond3)], color)


@app.callback(
    Output('selected-sax-listing', 'children'),
    [Input('scatter-figure', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return html.H4("Selected Sax Listing", className="text-center")
    df1 = df.loc[df['ItemID']==clickData['points'][0]['text']]

    fig_hist = ag.histogramFig(clickData['points'][0]['text'], df)


    children = [
        html.H4("Selected Sax Listing", className="text-center"),
        html.Div([
            html.Button('<', id='left-image-click', n_clicks=0),
            html.A(
                html.Img(
                    src = df1['PictureURL'].apply(ast.literal_eval).values[0][0],
                    style={'width': '30%'},  
                ),
            href = df1['PictureURL'].apply(ast.literal_eval).values[0][0],
            id='saxophone-image',
            ),
            html.Button('>', id='right-image-click', n_clicks=0)],
        style={'textAlign': 'center'},
        className = 'twelve columns pretty_container'
        ),
        html.Div([
            html.P(
                html.H5(df1['Title'].values[0]),
            ),
            dcc.Markdown(
                '''
                **Item ID:** {0} \n
                **Price:** ${1:20,.2f} \n
                **Condition:** {2} \n
                
                '''.format(df1['ItemID'].values[0],
                 df1['ConvertedCurrentPrice-value'].values[0],
                 df1['Condition'].values[0],
                 # df1['Description'].values[0]
                 )
            ),
            dcc.Graph(figure = fig_hist, id = 'hist-fig')
            
        ], className = 'twelve columns pretty_container')
    ]

    return children

@app.callback(
    Output('saxophone-image', 'children'),
    [Input('left-image-click', 'n_clicks'),
     Input('right-image-click', 'n_clicks'),
     Input('scatter-figure', 'clickData')]
)
def updateSaxImage(left, right, clickData):
    if clickData is None:
        return None
    df1 = df.loc[df['ItemID']==clickData['points'][0]['text']]

    image_arr = df1['PictureURL'].apply(ast.literal_eval).values[0]

    image = image_arr[(right - left) % len(image_arr)]
    
    return html.Img(
                    src = image,
                    style={'width': '30%'},   
                ),

def cleanUpDf(df):

    df.loc[~df['ItemSpecifics-Type'].isna(), 'ItemSpecifics-Type'] = df[~df['ItemSpecifics-Type'].isna()]['ItemSpecifics-Type'].apply(iscu.cleanUpType)
    df.loc[~df['ItemSpecifics-Brand'].isna(),'ItemSpecifics-Brand'] = df[~df['ItemSpecifics-Brand'].isna()]['ItemSpecifics-Brand'].apply(iscu.cleanUpBrand)
    df.loc[~df['ItemSpecifics-Skill Level'].isna(), 'ItemSpecifics-Skill Level'] = df[~df['ItemSpecifics-Skill Level'].isna()]['ItemSpecifics-Skill Level'].apply(iscu.cleanUpSkill)
    df['Condition'] = df['ConditionID'].apply(iscu.cleanUpCondition)


    df.loc[df['ItemSpecifics-Type'].isna(), 'ItemSpecifics-Type'] = df[df['ItemSpecifics-Type'].isna()]['Title'].apply(iscu.extractTypeFromTitle)
    df.loc[df['ItemSpecifics-Brand'].isna(),'ItemSpecifics-Brand'] = df[df['ItemSpecifics-Brand'].isna()]['Title'].apply(iscu.extractBrandFromTitle)

    df['Model'] = np.nan
    df.loc[df['ItemSpecifics-Brand']=='Selmer', 'Model'] = df.loc[df['ItemSpecifics-Brand']=='Selmer', 'Title'].apply(iscu.selmerModel)
    df.loc[df['ItemSpecifics-Brand']=='Yamaha', 'Model'] = df.loc[df['ItemSpecifics-Brand']=='Yamaha', 'Title'].apply(iscu.yamahaModel)
    df.loc[df['ItemSpecifics-Brand']=='Yanagisawa', 'Model'] = df.loc[df['ItemSpecifics-Brand']=='Yanagisawa', 'Title'].apply(iscu.yanagisawaModel)
    df.loc[~df['Model'].isna(), 'ItemSpecifics-Skill Level'] = iscu.extractSkillFromModel(df.loc[~df['Model'].isna()])

    return df

if __name__ == '__main__':
    app.run_server(debug=True)