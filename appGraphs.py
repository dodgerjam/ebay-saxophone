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
    branchvalues="total"))

    fig.update_layout(
        title = "Brand, Type, Price Sunburst Chart"
    )

    if color_agg == 'None':
        return fig
    
    else:

        fig.update_traces(marker = dict(
        colors = color,
        colorscale = 'Purp'),
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
        colorscale = 'purp',
        locationmode = 'country names',
        marker_line_width = 0.4,
        
    ))
    fig.update_layout(
    title_text = "Number of Saxes Manufactured in each Country",
    geo=dict(
        #showframe=False,
        showcoastlines=False,
        projection_type="orthographic",
        showocean=True, oceancolor="#7b7d8d",
        showlakes=True, lakecolor="#7b7d8d",
    ),
    )
    return fig

def histogramFig(df):

    df["ConvertedCurrentPrice-value(LOG)"] = df["ConvertedCurrentPrice-value"].apply(np.log10)

    order = df['ItemSpecifics-Type'].value_counts().index.values
    df.groupby("ItemSpecifics-Type")["ConvertedCurrentPrice-value(LOG)"].apply(list).loc[order]

    data = df.groupby("ItemSpecifics-Type")["ConvertedCurrentPrice-value(LOG)"].apply(list).loc[order].values
    types = order
    colors = sns.color_palette("Purples", len(df['ItemSpecifics-Type'].value_counts().values)).as_hex()[::-1]
    fig = go.Figure()
    for data_line, color, sax in zip(data, colors, types):
        fig.add_trace(go.Violin(x=data_line, line_color=color, name = sax))
    fig.update_traces(orientation='h', side='positive', width=3, points=False)
    fig.update_layout(xaxis_showgrid=False, xaxis_zeroline=False)
    fig.update_layout(plot_bgcolor='#7b7d8d')
    fig.update_xaxes(
            title="Price",
            tickvals=[np.log10(x) for x in (100,500,1000, 5000, 10000)],
            ticktext=["$100", "$500", "$1k", "$5k", "$10k"],
        )
    fig.update_layout(title = 'Distribution of Price for Sax Types',
    )
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
        ))
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
                "<extra></extra>"
            ))
        fig = go.Figure(data = data) 
        return fig