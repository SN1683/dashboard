import styles as page
import processing as processing
import plotly_express as px
from dash import Dash, dcc, html, callback, Output, Input





barchartdata = processing.generateBarchartdata(processing.data)
boxplotdata = processing.generateBoxplotdata(processing.data)
scatterplotdata = processing.generateScatterplotdata(processing.data)
problemNames = barchartdata["Problem"].unique()
scatterplot = processing.createScatterplot(scatterplotdata)

resultants = []
indices = []
paragraphs = [html.H3("Anomalous cases to investigate")]
with open('./anomalies.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        paragraphs.append(html.P(children=line))
# we create all the elements and put them in a list
# then we simply set the children attribute of the app.layout div to be elements
# this allows us to construct elements bit by bit, without making app layout wildly messy
elements = []

# we first add a header
elements.append(html.Section(children=(html.H1(children="Solver Analytics", style=page.topsectionh1style, ),
                                       html.P(
                                           children=page.topsectionh1text,
                                           style=page.introStyle),),
                             style=page.topsectionstyle, ))

# we then create a dropdown menu so the user can select a specific problem
elements.append(
    dcc.Dropdown(problemNames, 'csplib-problem001', id="barChartDropdown", placeholder="Select a problem",
                 style=page.dropdownStyle))
# I have left the bar chart in for now, we can get rid of it later if required
elements.append(dcc.Graph(id="barChart", style=page.barChartStyle))
# added a scatterplot to display performance across all problems at once
elements.append(dcc.Graph(id="Scatterplot", style=page.scatterplotstyle, figure=scatterplot))
# dropdowns for specifying the box plot graph
elements.append(dcc.Dropdown(boxplotdata["Problem"].unique(), 'csplib-prob001', id='problemDropdown'))
elements.append(dcc.Dropdown(boxplotdata["Parameters"].unique(), 'random01.param', id='parameterDropdown'))
elements.append(dcc.Dropdown(boxplotdata["Solver"].unique(), 'lingeling', id='solverDropdown'))

elements.append(dcc.Graph(id="boxPlot", style=page.barChartStyle))
elements.append(html.Section(children=paragraphs))
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


# callback for selecting the problem to display on the bar chart
@callback(Output('barChart', 'figure'),
          [Input('barChartDropdown', 'value')])
def update_barchart(problem):
    # depending on the problem name specified, return the appropriate barchart
    return px.bar(barchartdata, x=list(set(barchartdata["Solver"])),
                  y=barchartdata.loc[barchartdata["Problem"] == problem]["Solution Time"], title=problem, labels={
            "x": "Solvers",
            "y": "Average solution time (ms)"
        })

# callback for selecting problem, solver and parameters to be displayed on the box plot
@callback(Output('boxPlot', 'figure'),
          [Input('problemDropdown', 'value')], [Input('parameterDropdown', 'value')],
          [Input('solverDropdown', 'value')])
def update_boxplot(problem, parameter, solver):

    return px.box(boxplotdata,
                  y=boxplotdata.loc[
                      ((boxplotdata["Problem"] == problem) & (boxplotdata["Parameters"] == parameter) & (boxplotdata["Solver"] == solver))][
                      "Total Solution "
                      "Time"],
                  title=("Solving " + problem + " with parameter choice " + parameter + " and solver " + solver), labels={

            "y": "Solution Time (ms)"
        })


app.run_server(debug=True)
