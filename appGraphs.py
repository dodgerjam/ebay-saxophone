import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def sunburstFig(df, parent_hierarchy, color_agg = 'Mean Price',):
    # df1 = df.groupby(['ItemSpecifics-Brand','ItemSpecifics-Type', 'Model'])['ConvertedCurrentPrice-value'].median().reset_index()
    values = []
    ids = []
    labels = []
    parents = []
    color = []

    for i in range(len(parent_hierarchy) , 0, -1):

        if color_agg == 'Mean Price':
            df1 = df.groupby(parent_hierarchy[:i])['ConvertedCurrentPrice-value'].mean().reset_index()
        elif color_agg == 'Median Price':
            df1 = df.groupby(parent_hierarchy[:i])['ConvertedCurrentPrice-value'].median().reset_index()
        else:
            df1 = df.groupby(parent_hierarchy[:i])['ConvertedCurrentPrice-value'].size().reset_index()

        values +=  df.groupby(parent_hierarchy[:i]).size().values.tolist()
        ids += df1.apply(lambda x: ' - '.join([str(x[col]) for col in parent_hierarchy[:i]]), axis=1).values.tolist()
        labels += df1[parent_hierarchy[i-1]].values.tolist()
        parents += df1.apply(lambda x: ' - '.join([str(x[col]) for col in parent_hierarchy[:i-1]]), axis=1).values.tolist()
        color += df1['ConvertedCurrentPrice-value'].values.tolist()
    
    fig = go.Figure(data = go.Sunburst(
    ids = ids,
    values = values,
    parents = parents,
    labels = labels,
    hovertemplate =
    '<i>Count</i>: %{value}'
    "<extra></extra>",
    branchvalues="total",))

    fig.update_layout(
        plot_bgcolor='rgb(0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        template = "plotly_dark",
    )

    if color_agg == 'None':
        return fig
    
    else:

        fig.update_traces(marker = dict(
        colors = color,
        colorscale = 'inferno'),
        hovertemplate=
                "<b>%{label}</b><br>" +
                color_agg + ": %{color:$,.0f}<br>" +
                "Count: %{value}<br>" 
                "<extra></extra>",
        )

        fig.update_layout(coloraxis_colorbar=dict(
            title=color_agg))
        
        return fig

def choroplethFig(df):
    fig = go.Figure(data = go.Choropleth(
        locations = df['ItemSpecifics-Country/Region of Manufacture'].value_counts().index,
        z =  df['ItemSpecifics-Country/Region of Manufacture'].value_counts().values,
        colorscale = 'inferno',
        locationmode = 'country names',
        marker_line_width = 0.4,
        
    ))
    fig.update_layout(
    geo=dict(
        #showframe=False,
        showcoastlines=False,
        projection_type="orthographic",
        showocean=True, oceancolor="#7b7d8d",
        showlakes=True, lakecolor="#7b7d8d",
    ),
    )
    fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            template = "plotly_dark",
        )
    fig.update_geos(bgcolor='rgba(0,0,0,0)')
    return fig

def scatterFig(df_filter, color):
    if color == 'None':
        fig = go.Figure(data = go.Scatter(
            x = df_filter['EndTime'],
            y = df_filter['ConvertedCurrentPrice-value'],
            text = df_filter['ItemID'],
            hovertemplate = "<b>%{text}</b><br><br>" +
                "Price: %{y:$,.0f}<br>" +
                "<extra></extra>",
            mode='markers', 
            marker=dict(
                color='rgb(254,192,54)',
                size=3,)
                
        ))
        fig.update_layout(
            template = "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    else:
        data = []
        for c in df_filter[color].unique():
            data.append(go.Scatter(
                x = df_filter[df_filter[color]==c]['EndTime'],
                y = df_filter[df_filter[color]==c]['ConvertedCurrentPrice-value'],
                mode = 'markers',
                name = c,
                text = df_filter[df_filter[color]==c]['ItemID'],
                hovertemplate = "<b>%{text}</b><br><br>" +
                "Price: %{y:$,.0f}<br>" +
                "<extra></extra>",
                marker=dict(
                size=3,)
            ))
        fig = go.Figure(data = data) 
        fig.update_layout(
            template = "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return fig