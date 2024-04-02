import styles as page
import processing as processing
import plotly_express as px
from dash import Dash, html, callback, Output, Input
import plotly.graph_objects as go

elements = []

# we first add a header
elements.append(html.Section(children=(html.H1(children="Solver Analytics", style=page.topsectionh1style, ),
                                       html.P(
                                           children="Comparing solver performance across different problem classes",
                                           style=page.introStyle),),
                             style=page.topsectionstyle, ))
processing.generateScatterplot(elements)
processing.generateBoxPlot(elements)
processing.generateClusterPlot(elements)
processing.generateVBSChart(elements)
processing.generateAnomalyTable(elements)
# a footer section
elements.append(html.Section(
    children=[html.P(["A Vertically Integrated Project by Samvit Nagpal, University of St Andrews, 2024", html.Br(),
                      "Under the supervision of Ozgur Akgun"], style=page.footerTextStyle)], style=page.footerStyle))

app = Dash(meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])

app.layout = html.Div(
    children=elements, style=page.body,
)


# callback for selecting problem, solver and parameters to be displayed on the box plot
@callback(Output('boxPlot', 'figure'),
          [Input('problemDropdown', 'value')], [Input('modelDropdown', 'value')],
          [Input('solverDropdown', 'value')])
def update_boxplot(problem, model, solver):
    return px.box(processing.boxplotdata,
                  y=processing.boxplotdata.loc[
                      ((processing.boxplotdata["Problem"] == problem) & (processing.boxplotdata["Model"] == model) & (
                              processing.boxplotdata["Solver"] == solver))][
                      "Total Solution Time"],
                  title=("Solving " + problem + " with model " + model + " and solver " + solver), labels={

            "y": "Solution Time (ms)"
        })


@callback(Output('scatterplot', 'figure'),
          [Input('problemDropdown', 'value')], [Input('scattermodelDropdown1', 'value')],
          [Input('scattersolverDropdown1', 'value')], [Input('scattermodelDropdown2', 'value')],
          [Input('scattersolverDropdown2', 'value')], [Input('scattertimeDropdown', 'value')])
def update_Scatterplot(problem, model1, solver1, model2, solver2, time):
    scatterplot = px.scatter(x=processing.scatterplotdata.loc[
        (processing.scatterplotdata["Problem"] == problem) & (processing.scatterplotdata["Solver"] == solver1) & (
                    processing.scatterplotdata["Model"] == model1) & (processing.scatterplotdata["Options"] == time)][
        "Time"],
                             y=processing.scatterplotdata.loc[(processing.scatterplotdata["Problem"] == problem) & (
                                         processing.scatterplotdata["Solver"] == solver2) & (processing.scatterplotdata[
                                                                                                 "Model"] == model2) & (
                                                                          processing.scatterplotdata[
                                                                              "Options"] == time)]["Time"],
                             labels={"x": "Time taken by " + solver1, "y": "Time taken by " + solver2})
    scatterplot.add_trace(
        go.Scatter(x=processing.scatterplotdata.loc[processing.scatterplotdata["Solver"] == "minion"]["Time"],
                   y=processing.scatterplotdata.loc[processing.scatterplotdata["Solver"] == "minion"]["Time"],
                   name="y = x")
    )
    # changing the axis ranges and adding a bit of styling
    scatterplot.update_xaxes(
        range=[0, max(processing.scatterplotdata.loc[(processing.scatterplotdata["Problem"] == problem) & (
                    processing.scatterplotdata["Solver"] == solver1) & (
                                                                 processing.scatterplotdata["Model"] == model1) & (
                                                                 processing.scatterplotdata["Options"] == time)][
                          "Time"])],
        showline=True, linewidth=1, linecolor='black'
    )

    scatterplot.update_yaxes(
        range=[0, max(processing.scatterplotdata.loc[(processing.scatterplotdata["Problem"] == problem) & (
                    processing.scatterplotdata["Solver"] == solver2) & (
                                                                 processing.scatterplotdata["Model"] == model2) & (
                                                                 processing.scatterplotdata["Options"] == time)][
                          "Time"])],
        showline=True, linewidth=1, linecolor='black'

    )
    return scatterplot

@callback(Output('VBSPlot', 'figure'),
          [Input('VBSModelDropdown', 'value')], [Input('VBSSolverDropdown', 'value')],)
def update_VBSplot(model, solver):
    df = processing.generateVBSdata(model, solver, processing.boxplotdata)
    return px.bar(df,
                  y='Total Time',
                  title=("Comparing the performance of " + model + " and " + solver + " to the best and worst"), labels={
            "x": "Best Configuration, Selected Configuration, Worst Configuration",
            "y": "Solution Time (ms)"
        })


app.run_server(debug=True)
