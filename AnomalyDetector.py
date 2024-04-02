import os
import pandas as pd
import json
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest

DIRECTORY_NAME = "./features"
ITERATIONS = 10


def removeUnnecessaryKeys(statsdata):
    # all of these are kind of unnecessary for our purposes and would probably introduce undesirable noise into the sample
    unnecessaryKeys = ['computer', 'savilerowLogs', 'conjureVersion', 'essence', 'essenceParams', 'useExistingModels',
                       'savilerowVersion', 'savilerowOptions', 'solverOptions', 'solver', 'status', 'timestamp']
    for key in unnecessaryKeys:
        statsdata.pop(key)


def generateDataFrame(directory, featuresdata):
    # directory is the features directory
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        # a filename of BASE.fnz2feat.json has an equivalent labels file of BASE.stats.json but without the .eprime_
        statsfilename = filename.replace(".eprime_", "-")
        statsfilename = "./stats/" + statsfilename.replace("fnz2feat", "stats")
        # to avoid errors if for some reason the corresponding labels file does not exist
        if os.path.exists(statsfilename):
            with open(DIRECTORY_NAME + "/" + filename) as f:
                with open(statsfilename) as statsf:
                    jsonData = json.load(f)
                    statsdata = json.load(statsf)
                    # we should only include rows where stuff actually ran and we didn't get an error
                    if statsdata['status'] == "OK":
                        removeUnnecessaryKeys(statsdata)
                        # normalizing essentially undoes nesting of JSON and flattens it into columns of a dataframe
                        statsdf = pd.json_normalize(statsdata)
                        df = pd.DataFrame([jsonData])
                        # combine the columns of df (features) and statsdf (stats)
                        result = pd.concat([df, statsdf], axis=1)
                        # add the rows of the new dataframe to the overall dataframe
                        featuresdata = pd.concat([featuresdata, result], ignore_index=True)
    return featuresdata


def runModels(anomalyData):
    anomalousValues = anomalyData.copy(deep=True)
    # with standard hyperparameters
    forest = IsolationForest(n_estimators=50, max_samples='auto', contamination=float(0.01), max_features=1.0)
    lof = LocalOutlierFactor(n_neighbors=20, contamination=float(0.01))
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
def repeatAnalysis(iterations, combined, anomalyData):
    for i in range(iterations):
        # so it's easier to keep track of progress when executing hundreds of iterations
        if i % 10 == 0:
            print(str(int(i * 100 / iterations)) + "% complete")
        anomalies = runModels(anomalyData)
        # merging the new dataset with the previous anomalies to find the intersection
        combined.reset_index().merge(anomalies, how="inner",
                                     on=anomalyData.columns.tolist()).set_index('index')
        # merging creates annoying extra columns that mess with later merges, so we drop them
        to_drop = [x for x in combined if x.endswith('_y') or x.endswith('_x')]
        combined.drop(to_drop, axis=1, inplace=True)
    return combined

directory = os.fsencode(DIRECTORY_NAME)
if __name__ == '__main__':
    featuresdata = pd.DataFrame()
    featuresdata = generateDataFrame(directory, featuresdata)
    result = runModels(featuresdata)
    combined = result.copy(deep=True)
    combined = repeatAnalysis(ITERATIONS, combined, featuresdata)
    print(combined)
    combined[['d_int_vars', 'totalTime', 'savilerowInfo.SolverNodes']].to_csv('./anomalies.csv', header=['d_int_vars', 'totalTime', 'savilerowInfo.SolverNodes'], index=None, sep=',', mode='w+')
