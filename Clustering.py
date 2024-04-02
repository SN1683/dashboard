import pandas as pd
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import AnomalyDetector as ad
from sklearn.cluster import KMeans
import seaborn as sns


clusteringData = pd.DataFrame()
clusteringData = ad.generateDataFrame(ad.directory, clusteringData)
clusteringData = clusteringData.drop(['savilerowInfo.SavileRowClauseOut', 'savilerowInfo.SavileRowTimeOut', 'savilerowInfo.SavileRowTotalTime', 'savilerowInfo.SolverFailures', 'savilerowInfo.SolverSatisfiable', 'savilerowInfo.SolverTimeOut', 'savilerowInfo.SolverTotalTime'], axis=1)

def displaySilhouetteScores():
    K = range(3, 15)
    fits = []
    score = []

    for k in K:
        # train the model for current value of k on training data
        model = KMeans(n_clusters=k, random_state=0, n_init='auto').fit(clusteringData)

        # append the model to fits
        fits.append(model)

        # Append the silhouette score to scores
        score.append(silhouette_score(clusteringData, model.labels_, metric='euclidean'))

    sns.lineplot(x=K, y=score)
    plt.show()



kmeans = KMeans(n_clusters=7,random_state = 0, n_init='auto')
y = kmeans.fit_predict(clusteringData[clusteringData.columns.tolist()])

clusteringData['Cluster'] = y

print(clusteringData.head())

clusteringData.to_csv('./clusteringData.csv', header=clusteringData.columns.tolist(), index=None, sep=',', mode='w+')