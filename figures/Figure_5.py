
# %% Importing Packages
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# %% Define Working Directory
cwd = os.getcwd()
os.chdir(r'PATH/TO/WORKING/DIRECTORY')
wd = os.getcwd()

# %% Reading CAMELS Features
df_features=pd.read_csv('Datasets\\camel_all_features.csv',dtype={'Gauge_ID': str})
df_cluster=pd.read_csv('Datasets\\camel_clustering_id.csv')
df_cluster=df_cluster.rename(columns={'Cluster_7':'Cluster'})    
df_features_cluster = pd.merge(df_features,df_cluster[['Num','Cluster']], on="Num")
df_features_cluster.rename(columns={'Gauge_Lat': 'LAT', 'Gauge_Lon': 'LON'}, inplace=True)
df_camels_area=pd.read_csv('CAMELS_Area.csv',dtype={'Gauge_ID': str})
basin_area=df_camels_area.Area

metrics_list=['KGE','MAE','fallVB','winVB','sprVB','sumVB','q10VB','q90VB']
os.chdir(wd+'//Outputs')
# %% Heatmap of median or mean CSS
metrics_list=['KGE','MAE','VARB','AVB','fallVB','winVB','sprVB','sumVB','q10VB','q90VB']

df_css_aggregate=pd.DataFrame([])
for i in range(0,10):
    cal_metric=metrics_list[i]
    df_skill_metric=pd.read_csv('Skill_Score_%s_Runoff_CAMELS_CLM-%s.csv'%(cal_metric,cal_metric))
    df_skill_metric.columns=['NLDAS2','ERA5','Livneh','PRISM','Daymet',
                          'Basin_ID','Lat','Lon','Cluster']
    df_skill_metric=df_skill_metric.drop(['Lat','Lon','Basin_ID'],axis=1)
    
    df_css_aggregate_metric=df_skill_metric.groupby(['Cluster']).mean().reset_index()
    df_css_aggregate_metric['Metric']=cal_metric
    df_css_aggregate=pd.concat([df_css_aggregate,df_css_aggregate_metric])

df_css_aggregate=df_css_aggregate.reset_index(drop=True)
df_css_aggregate_conus=df_css_aggregate.groupby('Metric').mean()
df_css_aggregate_conus.drop(['Cluster'],axis=1,inplace=True)
df_css_aggregate_conus=df_css_aggregate_conus.reindex(metrics_list)

#################################
fig, axes = plt.subplots(2,4,figsize=(15,15))
plt.rcParams.update({'font.size': 26}) 
axes=axes.ravel()
# fig.patch.set_facecolor('#F0F0F0')

clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']
Ncluster=7
# cmap = sns.diverging_palette(35, 250, as_cmap=True)
# cmap=sns.color_palette("vlag_r", as_cmap=True)
# cmap=sns.color_palette("Blues", as_cmap=True)
# cmap = 'YlGnBu'
cmap = 'YlGnBu_r'
min_cbar=0
max_cbar=1
k=0
for ii in range(Ncluster): 
    ax=axes[k]
    
    cluster=(ii+1)
    df_css_aggregate_cluster=df_css_aggregate[df_css_aggregate.Cluster == cluster]
    df_css_aggregate_cluster.set_index('Metric',inplace=True)
    df_css_aggregate_cluster.drop(['Cluster'],axis=1,inplace=True)

    sns.heatmap(df_css_aggregate_cluster, linewidths=.5, 
                ax=ax,cbar=False,cmap=cmap,vmin=min_cbar,vmax=max_cbar)
                
    ax.set_facecolor('whitesmoke')
    ax.invert_yaxis()
    ax.set_xticks([0.5,1.5,2.5,3.5,4.5])
    if k>3:
        ax.set_xticklabels(['NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
    else:
        ax.set_xticklabels('')
    
    if k==0 or k==4:    
        ax.set_yticklabels(['KGE','MAE', 'VARB','AVB','Fall VB', 'Winter VB', 'Spring VB', 'Summer VB',
                            'Q10 VB', 'Q90 VB'])
    else:
        ax.set_yticklabels('')
    
    ax.set_ylabel('')
    ax.set_title(clusterName[ii])
    k=k+1


ax=axes[7]


sns.heatmap(df_css_aggregate_conus, linewidths=.5, 
            ax=ax,fmt = '',cbar=False,cbar_kws={"orientation": "vertical"},
            cmap=cmap,vmin=min_cbar,vmax=max_cbar)
            
ax.set_facecolor('whitesmoke')
ax.invert_yaxis()
ax.set_xticks([0.5,1.5,2.5,3.5,4.5])
ax.set_xticklabels(['NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
# ax.set_yticklabels(['KGE','MAE', 'VARB','AVB','Fall VB', 'Winter VB', 'Spring VB', 'Summer VB',
#                     'Q10 VB', 'Q90 VB'])
ax.set_yticklabels('')
ax.set_ylabel('')
ax.set_title('CONUS')

###################### CONUS Median or Mean CSS ######################
fig, axes = plt.subplots(1,1,figsize=(15,15))
plt.rcParams.update({'font.size': 32}) 

clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']
Ncluster=7
# cmap = sns.diverging_palette(35, 250, as_cmap=True)
# cmap=sns.color_palette("vlag_r", as_cmap=True)
cmap = 'YlGnBu_r'
min_cbar=0
max_cbar=1


ax=axes


sns.heatmap(df_css_aggregate_conus, linewidths=.5, 
            ax=ax,fmt = '',cbar=True,cbar_kws={"orientation": "vertical"},
            cmap=cmap,vmin=min_cbar,vmax=max_cbar)
            
ax.set_facecolor('whitesmoke')
ax.invert_yaxis()
ax.set_xticks([0.5,1.5,2.5,3.5,4.5])
ax.set_xticklabels(['NLDAS2', 'ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
ax.set_yticklabels(['KGE','MAE', 'VARB','AVB','Fall VB', 'Winter VB', 'Spring VB', 'Summer VB',
                    'Q10 VB', 'Q90 VB'])

ax.set_ylabel('')
ax.set_title('CONUS')



