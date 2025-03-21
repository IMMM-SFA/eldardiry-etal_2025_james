# %% Importing Packages
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import shapefile as shp
import seaborn as sns
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable


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


# %% Load ANOVA Results and normalize results 

# metrics to describe hydrograph or flow dynamics
metrics_1=['dKGE','dMAE','VarB']
# metrics for water balance and reservoir operations
metrics_2=['AVB','fallVB','winVB','sprVB','sumVB']

#metrics for high and low flow for flood and drought applications
metrics_3=['q10VB','q90VB']

metrics=metrics_1+metrics_2+metrics_3


# Load AVG Runoff
df_camels_avg_runoff=pd.read_csv('\\outputs\\CLM_CAMELS_USGS_AVG_Daily_Runoff.csv',dtype={'Gauge_ID': str})   
df_cluster_metric_daily=pd.DataFrame([])
df_cluster_metric_daily_UCtot_avg=pd.DataFrame([])
df_cluster_metric_daily_UCtot_std=pd.DataFrame([])
df_cluster_metric_daily_UCtot_q75=pd.DataFrame([])
df_cluster_metric_daily_UCtot_q25=pd.DataFrame([])
df_cluster_metric_daily_UCtot_q50=pd.DataFrame([])
df_metric_daily_UCtot=pd.DataFrame([])
for i in range(len(metrics)):
    metric=metrics[i]
    
    df_SS=pd.read_csv('\\outputs\\ANOVA_Runoff_Metrics_NWLPD\\ANOVA_%s_Runoff_CAMELS_NWLPD.csv'%metric, sep = '\t',dtype={'Gauge_ID': str})
    df_SS['pct_SSf_SSp']=df_SS['SSf']/(df_SS['SSp']+df_SS['SSf'])*100
    
    df_avg=df_SS.groupby(['Cluster']).mean()[['pct_SSf_SSp']]
    df_avg.columns=[metric]
    df_cluster_metric_daily=pd.concat([df_cluster_metric_daily,df_avg],axis=1)
    
    df_SS['UCtot']=(df_SS['SSp']+df_SS['SSf'])
    df_avg=df_SS.groupby(['Cluster']).mean()[['UCtot']]
    df_avg.columns=[metric]
    df_cluster_metric_daily_UCtot_avg=pd.concat([df_cluster_metric_daily_UCtot_avg,df_avg],axis=1)
    
    df_std=df_SS.groupby(['Cluster']).std()[['UCtot']]
    df_std.columns=[metric]
    df_cluster_metric_daily_UCtot_std=pd.concat([df_cluster_metric_daily_UCtot_std,df_std],axis=1)
    
    df_q25=df_SS.groupby(['Cluster']).quantile(q=0.25,numeric_only=True)[['UCtot']]
    df_q25.columns=[metric]
    df_cluster_metric_daily_UCtot_q25=pd.concat([df_cluster_metric_daily_UCtot_q25,df_q25],axis=1)
    
    df_q75=df_SS.groupby(['Cluster']).quantile(q=0.75,numeric_only=True)[['UCtot']]
    df_q75.columns=[metric]
    df_cluster_metric_daily_UCtot_q75=pd.concat([df_cluster_metric_daily_UCtot_q75,df_q75],axis=1)
    
    df_q50=df_SS.groupby(['Cluster']).quantile(q=0.50,numeric_only=True)[['UCtot']]
    df_q50.columns=[metric]
    df_cluster_metric_daily_UCtot_q50=pd.concat([df_cluster_metric_daily_UCtot_q50,df_q50],axis=1)
    
    
    tmp=df_SS[['Gauge_ID','Cluster','UCtot']]
    tmp['Metric']=metric
    df_metric_daily_UCtot=pd.concat([df_metric_daily_UCtot,tmp],axis=0)

df_metric_daily_UCtot=df_metric_daily_UCtot.reset_index(drop=True)
  
# %% Quantiles 
clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']
   
col_names=['KGE','MAE','VARB','AVB',
        'Fall VB','Winter VB','Spring VB','Summer VB',
        'Q10 VB','Q90 VB']
df_cluster_metric_daily_UCtot_avg.columns=col_names
df_cluster_metric_daily_UCtot_std.columns=col_names
df_cluster_metric_daily_UCtot_q75.columns=col_names
df_cluster_metric_daily_UCtot_q25.columns=col_names
df_cluster_metric_daily_UCtot_q50.columns=col_names


df_cluster_metric_daily_UCtot_avg.index=clusterName
df_cluster_metric_daily_UCtot_avg_log= np.log10(df_cluster_metric_daily_UCtot_avg)

df_cluster_metric_daily_UCtot_std.index=clusterName
df_cluster_metric_daily_UCtot_std_log= np.log10(df_cluster_metric_daily_UCtot_std)

df_cluster_metric_daily_UCtot_q25.index=clusterName
df_cluster_metric_daily_UCtot_q25_log= np.log10(df_cluster_metric_daily_UCtot_q25)

df_cluster_metric_daily_UCtot_q75.index=clusterName
df_cluster_metric_daily_UCtot_q75_log= np.log10(df_cluster_metric_daily_UCtot_q75)


df_cluster_metric_daily_UCtot_q50.index=clusterName
df_cluster_metric_daily_UCtot_q50_log= np.log10(df_cluster_metric_daily_UCtot_q50)

# Interquartile Rage (IQR)
df_cluster_metric_daily_UCtot_iqr_log= df_cluster_metric_daily_UCtot_q75_log-df_cluster_metric_daily_UCtot_q25_log

df_cluster_metric_daily_UCtot_cv_log=df_cluster_metric_daily_UCtot_iqr_log.divide(df_cluster_metric_daily_UCtot_avg_log)






# %% Load Shapefiles
camel_path = r'Shapefiles\camels_epsg4326\camels_epsg4326.shp'
states_path = r'Shapefiles\cb_2015_us_state_500k\cb_2015_us_state_500k.shp'
counties_path = r'Shapefiles\cb_2015_us_county_500k\cb_2015_us_county_500k.shp'
camel_shp=gpd.read_file(camel_path)
huc8_path = r'Shapefiles\HUC8_CONUS\HUC8_US.shp'
sf = shp.Reader(huc8_path)
huc8_shp=gpd.read_file(huc8_path)
camel_shp=camel_shp.to_crs(epsg=4326)
states_shp=gpd.read_file(states_path)
huc8_bounds = huc8_shp.geometry.total_bounds
camel_bounds = camel_shp.geometry.total_bounds
xlim = ([huc8_bounds[0]-2,  huc8_bounds[2]+1])
ylim = ([huc8_bounds[1]-1,  huc8_bounds[3]])
df_lat_lon=df_features_cluster[['LAT','LON']]


# %% Spatial Plot and Heatmap for Total UC
fig = plt.figure(figsize=(15, 15))
spec = fig.add_gridspec(2,2)
plt.rcParams.update({'font.size': 24}) 

# fig, axes = plt.subplots(2,2,figsize=(15,15))
# plt.rcParams.update({'font.size': 26})       
# axes=axes.ravel()

metrics_labels=['KGE','MAE','VARB','AVB',
        'Fall VB','Winter VB','Spring VB','Summer VB',
        'Q10 VB','Q90 VB']


# ax=axes[0]
ax= fig.add_subplot(spec[0,0])
metric='dKGE'
df_metric_daily_UCtot_KGE=df_metric_daily_UCtot[df_metric_daily_UCtot['Metric']==metric].reset_index(drop=True)
gdf_data = gpd.GeoDataFrame(df_metric_daily_UCtot_KGE['UCtot'], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
gdf_data['logUCtot'] = np.log10(gdf_data['UCtot'])
states_shp.plot(ax=ax, alpha=.1,edgecolor='black',legend=False)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
# ax.set_facecolor('whitesmoke')
divider = make_axes_locatable(ax)
cax = divider.append_axes("right",size="2%",pad="2%")
gdf_data.plot(column='logUCtot',ax=ax,zorder=3,markersize=100,
                cmap='YlGnBu',legend=True,vmin=1,vmax=11,
                  cax=cax,categorical=False)
ax.title.set_text('Total Uncertainty [KGE]')

# ax=axes[1]
ax= fig.add_subplot(spec[0,1])
metric='AVB'
df_metric_daily_UCtot_AVB=df_metric_daily_UCtot[df_metric_daily_UCtot['Metric']==metric].reset_index(drop=True)
gdf_data = gpd.GeoDataFrame(df_metric_daily_UCtot_AVB['UCtot'], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
gdf_data['logUCtot'] = np.log10(gdf_data['UCtot'])
states_shp.plot(ax=ax,alpha=.1,edgecolor='black',legend=False)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
# ax.set_facecolor('whitesmoke')
divider = make_axes_locatable(ax)
cax = divider.append_axes("right",size="2%",pad="2%")
gdf_data.plot(column='logUCtot',ax=ax,zorder=3,markersize=100,
                cmap='YlGnBu',legend=True,vmin=1,vmax=11,
                  cax=cax,categorical=False)
ax.title.set_text('Total Uncertainty [AVB]')

# ax=axes[2]
ax= fig.add_subplot(spec[1,0])
sns.heatmap(df_cluster_metric_daily_UCtot_q50_log,
            ax=ax,cmap='YlGnBu',
            vmin=1,vmax=12) 

ax.invert_yaxis()
ax.title.set_text('Median (Q50)')

# ax=axes[3]
ax= fig.add_subplot(spec[1,1])
sns.heatmap(df_cluster_metric_daily_UCtot_iqr_log,
            ax=ax,cmap='YlGnBu',
            vmin=0,vmax=3) 

ax.invert_yaxis()
ax.get_yaxis().set_ticks([])  
ax.title.set_text('Interquartile Range (Q75-Q25)')
