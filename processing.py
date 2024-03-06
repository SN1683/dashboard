import pandas as pd
import plotly_express as px
import plotly.graph_objects as go

def generateBoxplotdata(data):
    boxplotdata = data.copy(deep=True)
    # get rid of all the rows which do not refer to time
    boxplotdata = boxplotdata.drop(
        boxplotdata[(boxplotdata.Options != "SavileRowTotalTime") & (boxplotdata.Options != "SolverTotalTime")].index)
    # the summing is for minion, so we sum the savile row and solver times
    boxplotdata = boxplotdata.groupby(['Problem', 'Essence', 'Parameters', 'Compact', 'Number', 'Model', 'Solver'])[
        'Time'].sum().reset_index(name="Total Solution Time")
    return boxplotdata


def generateScatterplotdata(data):
    # deep copying is useful so we do not alter the original dataset
    scatterplotdata = data.copy(deep=True)
    scatterplotdata = scatterplotdata.drop(
        scatterplotdata[
            (scatterplotdata.Options != "SavileRowTotalTime") & (scatterplotdata.Options != "SolverTotalTime")].index)
    # we dropped the same rows as above
    # but this time we take the mean time for each problem across all parameters
    scatterplotdata = scatterplotdata.groupby(['Problem', 'Solver'])[
        'Time'].mean().reset_index(name="Total Solution Time")
    return scatterplotdata


def generateBarchartdata(data):
    barchartdata = data.copy(deep=True)
    # this is deprecated now, we no longer have any use for the barchart
    return barchartdata.groupby(['Problem', 'Solver'])["Time"].mean().reset_index(name="Solution Time")


def createScatterplot(data):
    # plotting the average minion solution time against the lingeling solution time for each problem
    scatterplot = px.scatter(x=data.loc[data["Solver"] == "minion"]["Total Solution Time"],
                             y=data.loc[data["Solver"] == "lingeling"]["Total Solution Time"],
                             labels={"x": "Time taken by minion", "y": "Time taken by lingeling"},
                             hover_name=data["Problem"].unique(),)
    scatterplot.add_trace(
        go.Scatter(x=data.loc[data["Solver"] == "minion"]["Total Solution Time"], y=data.loc[data["Solver"] == "minion"]["Total Solution Time"], name="y = x")
    )
    # changing the axis ranges and adding a bit of styling
    scatterplot.update_xaxes(
        range=[0, max(data.loc[data["Solver"] == "minion"]["Total Solution Time"])],
        showline=True, linewidth=1, linecolor='black'
    )

    scatterplot.update_yaxes(
        range=[0, max(data.loc[data["Solver"] == "lingeling"]["Total Solution Time"])],
        showline=True, linewidth=1, linecolor='black'

    )
    return scatterplot


FILEPATH = "./infos.tsv"
LINE_TERMINATOR = '\n'
SEPARATOR = '\s+'

data = pd.read_csv(FILEPATH, lineterminator=LINE_TERMINATOR, sep=SEPARATOR)
