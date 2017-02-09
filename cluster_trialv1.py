from __future__ import print_function

from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

url='http://www.basketball-reference.com/leagues/NBA_2017.html'
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from sklearn import cluster
from sklearn.decomposition import PCA
from sklearn import preprocessing
from sklearn.metrics import silhouette_samples, silhouette_score
from ggplot import *
#Create function to get Team shooting and Opponent shooting from season page
def SeasonYearShooting(years_list):
    year_urls={str(year):'http://www.basketball-reference.com/leagues/NBA_'
            +str(year)+'.html' for year in years_list}
    SeasonYearShooting={}
    for year, url in year_urls.items():
        print (year)
        html=urlopen(url)
        soup=BeautifulSoup(html,'lxml')
        #team shooting first
        teamheader=['Team','G','MP','FG%','Avg_Dist','FGA%2P','FGA%0_3','FGA%3_10','FGA%10_16','FGA%16<3','FGA%3P',
        'FG2P','FG%0_3','FG%3_10','FG%10_16','FG%16<3','FG%3P',
        'AST2P%','DUNKSFGA%','DUNKS_M','LAYFGA%','LAY_M','AST3PT$','CORNER3PA%','CORNER3P%','HEAVES_ATT','HEAVES_M']
        #Comment in html mess up regular table extraction, need to extract for comment 
        divfind=soup.find('div',{'id':'all_team_shooting'})
        comment=str(divfind.contents[5]) #location of the table in comment
        soup2=BeautifulSoup(comment,'lxml') #convert comment to beautifulsoup 
        table_team=soup2.find('table',{'id':'team_shooting'}) #find table
        team_rows=table_team.findAll('tr')[3:] #skip the first 3 rows because header
        #td is entries, get entries for each row
        team_shooting=[[td.getText() for td in team_rows[i].findAll('td')]
                        for i in range(len(team_rows))]
        divfind2=soup.find('div',{'id':'all_opponent_shooting'})
        stringer2=str(divfind2.contents[5])
        soup3=BeautifulSoup(stringer2,'lxml')       
        table_opp=soup3.find('table',{'id':'opponent_shooting'})
        opp_rows=table_opp.findAll('tr')[3:]
        opp_shooting=[[td.getText() for td in opp_rows[i].findAll('td')]
                        for i in range(len(opp_rows))]
        #convert to dataframe
        teamShootingDF=pd.DataFrame(team_shooting,columns=teamheader)
        oppheader=['Team','G','MP','FG%','Avg_Dist','FGA%2P','FGA%0_3','FGA%3_10','FGA%10_16','FGA%16<3','FGA%3P',
        'FG2P','FG%0_3','FG%3_10','FG%10_16','FG%16<3','FG%3P',
        'AST2P%','DUNKSFGA%','DUNKS_M','LAYFGA%','LAY_M','AST3PT$','CORNER3PA%','CORNER3P%']
        oppShootingDF=pd.DataFrame(opp_shooting,columns=oppheader)
        teamShootingDF[teamShootingDF.columns[1:]]=teamShootingDF[teamShootingDF.columns[1:]].astype(float)
        oppShootingDF[oppShootingDF.columns[1:]]=oppShootingDF[oppShootingDF.columns[1:]].astype(float)


        SeasonYearShooting[year]={'team': teamShootingDF,'opp':oppShootingDF}
    return SeasonYearShooting
years_list_Try=[2016,"2017"]

test1=SeasonYearShooting(years_list_Try)
print (test1)
print (type(test1))

#KMeans Cluster trial 
data1=test1['2016']['opp']
data=data1
print (data.dtypes)
x_cols=data.columns[2:]
print (x_cols)
data_scaled=preprocessing.scale(data[x_cols])
data[x_cols]=data_scaled

X=data_scaled
range_n_clusters = [2, 3, 4, 5, 6]

for n_clusters in range_n_clusters:
    # Create a subplot with 1 row and 2 columns
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(18, 7)

    # The 1st subplot is the silhouette plot
    # The silhouette coefficient can range from -1, 1 but in this example all
    # lie within [-0.1, 1]
    ax1.set_xlim([-0.1, 1])
    # The (n_clusters+1)*10 is for inserting blank space between silhouette
    # plots of individual clusters, to demarcate them clearly.
    ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

    # Initialize the clusterer with n_clusters value and a random generator
    # seed of 10 for reproducibility.
    clusterer = KMeans(n_clusters=n_clusters,random_state=1)

    cluster_labels = clusterer.fit_predict(X)

    # The silhouette_score gives the average value for all the samples.
    # This gives a perspective into the density and separation of the formed
    # clusters
    silhouette_avg = silhouette_score(X, cluster_labels)
    print("For n_clusters =", n_clusters,
          "The average silhouette_score is :", silhouette_avg)

    # Compute the silhouette scores for each sample
    sample_silhouette_values = silhouette_samples(X, cluster_labels)

    y_lower = 10
    for i in range(n_clusters):
        # Aggregate the silhouette scores for samples belonging to
        # cluster i, and sort them
        ith_cluster_silhouette_values = \
            sample_silhouette_values[cluster_labels == i]

        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = cm.spectral(float(i) / n_clusters)
        ax1.fill_betweenx(np.arange(y_lower, y_upper),
                          0, ith_cluster_silhouette_values,
                          facecolor=color, edgecolor=color, alpha=0.7)

        # Label the silhouette plots with their cluster numbers at the middle
        ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

        # Compute the new y_lower for next plot
        y_lower = y_upper + 10  # 10 for the 0 samples

    ax1.set_title("The silhouette plot for the various clusters.")
    ax1.set_xlabel("The silhouette coefficient values")
    ax1.set_ylabel("Cluster label")

    # The vertical line for average silhouette score of all the values
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

    ax1.set_yticks([])  # Clear the yaxis labels / ticks
    ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    # 2nd Plot showing the actual clusters formed
    colors = cm.spectral(cluster_labels.astype(float) / n_clusters)
    ax2.scatter(X[:, 0], X[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                c=colors)

    # Labeling the clusters
    centers = clusterer.cluster_centers_
    # Draw white circles at cluster centers
    ax2.scatter(centers[:, 0], centers[:, 1],
                marker='o', c="white", alpha=1, s=200)

    for i, c in enumerate(centers):
        ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1, s=50)

    ax2.set_title("The visualization of the clustered data.")
    ax2.set_xlabel("Feature space for the 1st feature")
    ax2.set_ylabel("Feature space for the 2nd feature")

    plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                  "with n_clusters = %d" % n_clusters),
                 fontsize=14, fontweight='bold')

    plt.show()