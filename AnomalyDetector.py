import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
import processing

# set how many times to recreate and retest the models
ITERATIONS = 20

anomalyData = processing.data.copy(deep=True)


# using sklearn label encoder to transform all non numeric columns into numeric ones
def numericizeColumns(anomalyData):
    encoder = LabelEncoder()
    for column in anomalyData.columns:
        # this checks if the column contains only numeric datatypes
        if not np.issubdtype(anomalyData[column].dtype, np.number):
            encoder.fit(anomalyData[column])
            anomalyData[column] = encoder.transform(anomalyData[column])


# create and run the two models and get a combined result
def runModels(anomalyData):
    anomalousValues = anomalyData.copy(deep=True)
    # with standard hyperparameters
    forest = IsolationForest(n_estimators=50, max_samples='auto', contamination=float(0.1), max_features=1.0)
    lof = LocalOutlierFactor(n_neighbors=20)
    forest.fit(anomalyData)
    lof.fit(anomalyData)
    anomalousValues['scores'] = forest.decision_function(anomalyData)
    anomalousValues['forest_anomaly'] = forest.predict(anomalyData)
    anomalousValues['lof_anomaly'] = lof.fit_predict(anomalyData)
    # create a dataframe of all the rows which both the Isolation Forest and the LOF think are suspicious
    anomalousValues = anomalousValues.loc[
        (anomalousValues["forest_anomaly"] == -1) & (anomalousValues["lof_anomaly"] == -1)]
    return anomalousValues


# carry out the analysis multiple times
def repeatAnalysis(iterations, combined):
    for i in range(iterations):
        # so it's easier to keep track of progress when executing hundreds of iterations
        if i % 10 == 0:
            print(str(int(i * 100 / ITERATIONS)) + "% complete")
        anomalies = runModels(anomalyData)
        # merging the new dataset with the previous anomalies to find the intersection
        combined.reset_index().merge(anomalies, how="inner",
                                     on=["Problem", "Essence", "Parameters", "Compact", "Number", "Model", "Solver",
                                         "Options", "Time"]).set_index('index')
        # merging creates annoying extra columns that mess with later merges, so we drop them
        to_drop = [x for x in combined if x.endswith('_y') or x.endswith('_x')]
        combined.drop(to_drop, axis=1, inplace=True)
    return combined


def writetoFile(indices):
    strings = []
    # get all the indices of the anomalous rows
    for idx in indices:
        # find the equivalent row in the original dataset
        # we cannot use anomalyData as this has had all its labels and values changed
        row = processing.data.iloc[idx]
        resultStr = ""
        # add a nicely formatted string version of each row to an array
        for col in processing.data.columns.values.tolist():
            resultStr = resultStr + col + " : " + str(row[col]) + ", "
        strings.append(resultStr)
    # write the whole thing to a results file
    with open('./anomalies.txt', 'w') as f:
        f.write('\n'.join(strings))



numericizeColumns(anomalyData)
result = runModels(anomalyData)
combined = result.copy(deep=True)
combined = repeatAnalysis(ITERATIONS, combined)
indices = combined.index
writetoFile(indices)
print(combined)
