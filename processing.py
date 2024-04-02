import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, dash_table
import styles as page


def generateBoxplotdata(data):
    boxplotdata = data.copy(deep=True)
    # get rid of all the rows which do not refer to time
    boxplotdata = boxplotdata.drop(
        boxplotdata[(boxplotdata.Options != "SavileRowTotalTime") & (boxplotdata.Options != "SolverTotalTime")].index)
    # the summing is for minion, so we sum the savile row and solver times
    boxplotdata = boxplotdata.groupby(['Problem', 'Essence', 'Parameters', 'Compact', 'Number', 'Model', 'Solver'])[
        'Time'].sum().reset_index(name="Total Solution Time")
    return boxplotdata


def generateBoxPlot(elements):
    elements.append(html.H4(children="Select problem class", style=page.h4style))
    elements.append(dcc.Dropdown(boxplotdata["Problem"].unique(), 'csplib-prob001', id='problemDropdown', style=page.dropdownStyle))
    elements.append(html.H4(children="Select a model for the run configuration", style=page.h4style))
    elements.append(dcc.Dropdown(boxplotdata["Model"].unique(), 'model.eprime', id='modelDropdown', style=page.dropdownStyle))
    elements.append(html.H4(children="Select a solver for the run configuration", style=page.h4style))
    elements.append(dcc.Dropdown(boxplotdata["Solver"].unique(), 'lingeling', id='solverDropdown', style=page.dropdownStyle))
    elements.append(dcc.Graph(id="boxPlot", style=page.boxplotStyle))
    elements.append(html.P(children=["-" for i in range(2000)], style=page.lineStyle))


def generateScatterplotdata(data):
    # deep copying is useful so we do not alter the original dataset
    scatterplotdata = data.copy(deep=True)
    scatterplotdata = scatterplotdata.drop(
        scatterplotdata[
            (scatterplotdata.Options != "SavileRowTotalTime") & (scatterplotdata.Options != "SolverTotalTime")].index)
    # we dropped the same rows as above
    # but this time we take the mean time for each problem across all parameters
    # scatterplotdata = scatterplotdata.groupby(['Problem', 'Solver'])[
    #     'Time'].mean().reset_index(name="Total Solution Time")

    return scatterplotdata


def generateScatterplot(elements):
    # added a scatterplot to display performance across all problems at once

    elements.append(html.H4(children="Select problem class", style=page.h4style))
    elements.append(dcc.Dropdown(scatterplotdata["Problem"].unique(), 'csplib-prob001', id='scatterproblemDropdown', style=page.dropdownStyle))
    elements.append(html.H4(children="Select model for x axis configuration", style=page.h4style))
    elements.append(dcc.Dropdown(scatterplotdata["Model"].unique(), 'model.eprime', id='scattermodelDropdown1', style=page.dropdownStyle))
    elements.append(html.H4(children="Select solver for x axis configuration", style=page.h4style))
    elements.append(dcc.Dropdown(scatterplotdata["Solver"].unique(), 'lingeling', id='scattersolverDropdown1', style=page.dropdownStyle))
    elements.append(html.H4(children="Select model for y axis configuration", style=page.h4style))
    elements.append(dcc.Dropdown(scatterplotdata["Model"].unique(), 'model.eprime', id='scattermodelDropdown2', style=page.dropdownStyle))
    elements.append(html.H4(children="Select solver for y axis configuration", style=page.h4style))
    elements.append(dcc.Dropdown(scatterplotdata["Solver"].unique(), 'lingeling', id='scattersolverDropdown2', style=page.dropdownStyle))
    elements.append(html.H4(children="Select what output you want plotted", style=page.h4style))
    elements.append(dcc.Dropdown(scatterplotdata["Options"].unique(), 'SavileRowTotalTime', id='scattertimeDropdown', style=page.dropdownStyle))
    elements.append(dcc.Graph(id="scatterplot", style=page.scatterplotstyle))
    elements.append(html.P(children=["-" for i in range(2000)], style=page.lineStyle))



def generateClusterPlot(elements):
    data = pd.read_csv('./clusteringData.csv')
    data = data.drop(data[(data['totalTime'] > 500) & (data['savilerowInfo.SolverNodes'] > 10000000)].index)
    color_map = {0: 'red', 1: 'blue', 2: 'green', 3: 'pink', 4: 'black', 5: 'purple', 6: 'cyan'}
    colors = data['Cluster'].map(color_map)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['totalTime'],
        y=data['savilerowInfo.SolverNodes'],
        mode='markers',
        marker=dict(color=colors),
        customdata=data['d_int_vars']
    ))
    fig.update_traces(
        hovertemplate="<br>".join([
            "totalTime: %{x}",
            "savilerowInfo.SolverNodes: %{y}",
            "d_int_vars: %{customdata}",
        ])
    )
    fig.update_xaxes(title='Total Time')
    fig.update_yaxes(title='Solver Nodes')
    elements.append(html.H2(children="Results clustered by similarity of features", style=page.h2style))
    elements.append(dcc.Graph(id="clusterPlot", figure=fig))
    elements.append(html.P(children=["-" for i in range(2000)], style=page.lineStyle))

def generateAnomalyTable(elements):
    anomalyData = pd.read_csv('./anomalies.csv')
    elements.append(html.H2(children="The most anomalous results with their features", style=page.h2style))
    elements.append(dash_table.DataTable(anomalyData.to_dict('records'), style_table=page.tableStyle))


def generateVBSdata(model, solver, data):
    df = pd.DataFrame(columns=['Model', 'Solver', 'Total Time'])
    df.loc[0] = ['02_compact.eprime', 'chuffed', 7404031.23]
    meantime = data.loc[((data["Model"] == model) & (data["Solver"] == solver) & (data["Problem"] == "csplib-prob001")), 'Total Solution Time'].mean()
    df.loc[1] = [model, solver, meantime * 10**5]
    df.loc[2] = ['02_compact.eprime', 'cplex', 367704000.00]
    return df


def generateVBSChart(elements):
    data = boxplotdata.copy(deep=True)
    elements.append(html.H2(children="Comparing performance to virtual best and worst solvers", style=page.h2style))
    elements.append(html.H4(children="Select model for configuration", style=page.h4style))
    elements.append(dcc.Dropdown(data["Model"].unique(), 'model.eprime', id='VBSModelDropdown',
                                 style=page.dropdownStyle))
    elements.append(html.H4(children="Select solver for configuration", style=page.h4style))
    elements.append(dcc.Dropdown(data["Solver"].unique(), 'lingeling', id='VBSSolverDropdown',
                                 style=page.dropdownStyle))
    elements.append(dcc.Graph(id="VBSPlot", style=page.lineStyle))
    elements.append(html.P(children=["-" for i in range(2000)], style=page.lineStyle))

FILEPATH = "./infos.tsv"
LINE_TERMINATOR = '\n'
SEPARATOR = '\s+'

data = pd.read_csv(FILEPATH, lineterminator=LINE_TERMINATOR, sep=SEPARATOR)
boxplotdata = generateBoxplotdata(data)
scatterplotdata = generateScatterplotdata(data)
bleh = generateVBSdata('model.eprime', 'minion', boxplotdata)