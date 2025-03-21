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



# %% Plot All Metrics (Spatial Maps)

# metrics to describe hydrograph or flow dynamics
metrics_1=['dKGE','dMAE','VarB']
# metrics for water balance and reservoir operations
metrics_2=['AVB','fallVB','winVB','sprVB','sumVB']
#metrics for high and low flow for flood and drought applications
metrics_3=['q10VB','q90VB']
metrics=metrics_1+metrics_2+metrics_3
metric_name=['KGE','MAE','Variance Volume Bias','Annual Volume Bias',
               'Fall Volume Bias','Winter Volume Bias',
               'Spring Volume Bias','Summer Volume Bias',
               'Q0-10 Volume Bias',
               'Q90-100 Volume Bias',
               ]
# fig, axes = plt.subplots(3,4,figsize=(15,15))
fig = plt.figure(figsize=(15, 15))
spec = fig.add_gridspec(4,3)
plt.rcParams.update({'font.size': 24})       
xlim = ([camel_bounds[0]-2,  camel_bounds[2]+2])
ylim = ([camel_bounds[1]-3,  camel_bounds[3]+1])


df_lat_lon=df_features_cluster[['LAT','LON']]

for i in range(len(metrics)):
    metric=metrics[i]
    df_SS=pd.read_csv('\\outputs\\ANOVA_Runoff_Metrics_NWLPD\\ANOVA_%s_Runoff_CAMELS_NWLPD.csv'%metric, sep = '\t')
    df_SS['pct_SSf_SSp']=df_SS['SSf']/(df_SS['SSp']+df_SS['SSf'])*100

    ii=i//3
    jj=i%3
    ax= fig.add_subplot(spec[ii,jj])
    # ax=axes[i]
    gdf_data = gpd.GeoDataFrame(df_SS['pct_SSf_SSp'], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="2%",pad="-2%")
    gdf_data.plot(column='pct_SSf_SSp',ax=ax,zorder=3,markersize=100,
                    cmap='seismic',legend=True,
                      cax=cax,categorical=False,vmin=0,vmax=100)
    
    states_shp.plot(ax=ax, alpha=.1,edgecolor='black')
    ax.tick_params(axis='both',direction='in', length=15, width=2,grid_alpha=0.5)
    ax.title.set_text('%s'%metric_name[i])


# %%  heat map for average UCI
i=10
ii=i//3
jj=i%3
ax= fig.add_subplot(spec[ii,jj])
clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']

df_cluster_metric_daily=pd.DataFrame([])
df_cluster_metric_monthly=pd.DataFrame([])
for i in range(len(metrics)):
    metric=metrics[i]
    df_SS=pd.read_csv('\\outputs\\ANOVA_Runoff_Metrics_NWLPD\\ANOVA_%s_Runoff_CAMELS_NWLPD.csv'%metric, sep = '\t')
    df_SS['pct_SSf_SSp']=df_SS['SSf']/(df_SS['SSp']+df_SS['SSf'])*100
    df_avg=df_SS.groupby(['Cluster']).mean()[['pct_SSf_SSp']]
    df_avg.columns=[metric]
    df_cluster_metric_daily=pd.concat([df_cluster_metric_daily,df_avg],axis=1)


df_cluster_metric_daily.columns=['KGE','MAE','VARB','AVB',
                                 'Fall VB','Winter VB','Spring VB','Summer VB',
                                 'Q10 VB','Q90 VB']
x_ticks=df_cluster_metric_daily.columns
y_ticks=clusterName
df_cluster_metric_daily.index=clusterName
hm=sns.heatmap(df_cluster_metric_daily,ax=ax,vmin=0,vmax=100,
            cmap='seismic',xticklabels=x_ticks,yticklabels=y_ticks,
            cbar=False) 
hm.set_xticklabels(hm.get_xticklabels(), rotation = 45,fontsize=20)
hm.set_yticklabels(hm.get_yticklabels(),fontsize=20)
ax.invert_yaxis()
# ax.get_xaxis().set_ticks([])  
ax.title.set_text('Average UCI')

