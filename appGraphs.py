import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.stats import percentileofscore

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
        fig = go.Figure(data = go.Scattergl(
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
def getBinValues(step, x):
    minbin = step*int(min(x)//step)
    maxbin = step*int((max(x)//step) +1)
    return minbin, maxbin

def getBins(x):

    if max(x) - min(x) > 10_000:
        minbin, maxbin = getBinValues(500, x)
        return range(minbin, maxbin, 500)

    if max(x) - min(x) > 4000:
        minbin, maxbin = getBinValues(200, x)
        return range(minbin, maxbin, 200)

    if max(x) - min(x) > 2000:
        minbin, maxbin = getBinValues(100, x)
        return range(minbin, maxbin, 100)

    if max(x) - min(x) > 1000:
        minbin, maxbin = getBinValues(50, x)
        return range(minbin, maxbin, 50)

    else:
        minbin, maxbin = getBinValues(10, x)
        return range(minbin, maxbin, 10)


def histogramFig(itemID, df):

    saxtype = df[df['ItemID']==itemID]['ItemSpecifics-Type'].values[0]
    brand = df[df['ItemID']==itemID]['ItemSpecifics-Brand'].values[0]
    price = df[df['ItemID']==itemID]['ConvertedCurrentPrice-value'].values[0]

    cond1 = df['ItemSpecifics-Type']== saxtype
    cond2 = df['ItemSpecifics-Brand']== brand

    x = df[(cond1) & (cond2)]['ConvertedCurrentPrice-value'].values

    bins = getBins(x)
    colors = ['rgb(53,53,53)' for i in bins]
    colors[np.digitize(price, bins)-1] = 'rgb(254,192,54)'

    fig = go.Figure(go.Histogram(
        x = x,
        cumulative_enabled = True,
        xbins = dict(
                start = bins[0],
                end = bins[-1],
                size = bins[1]-bins[0],
        ),
        marker = dict(
                    color = colors,
                    line = dict(
                        color = 'rgb(254,192,54)',
                        width = 0.5
                        )
        )

    ))

    fig.update_layout(
                title = f"{brand} - {saxtype} ",
                template = "plotly_dark",
                #paper_bgcolor='rgba(0,0,0,0)'
            )
    percentile = int(percentileofscore(x, price))

    cmap = sns.diverging_palette(133, 10, as_cmap=True)
    text_color = cmap(percentile/100)
    fig.update_layout(
            annotations=[
                dict(
                    x= bins[int(len(bins)*0.1)],
                    y= len(x)*1.1,
                    text=f"{percentile}%",
                    xref="x",
                    yref="y",
                    showarrow = False,
                    font=dict(
                            size=30,
                            color=f"rgba{text_color}"
                            ),

                ),])

    return fig