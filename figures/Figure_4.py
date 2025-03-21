# %% Importing Packages
import os
import matplotlib.pyplot as plt
import pandas as pd
import shapefile as shp
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

metrics_list=['KGE','MAE','fallVB','winVB','sprVB','sumVB','q10VB','q90VB']
os.chdir(wd+'//Outputs')

# %% Spatial Plots Default-Best Ensemble-CSS

os.chdir(wd+'//Outputs')
metrics_list=['KGE','MAE','VARB','AVB','fallVB','winVB','sprVB','sumVB','q10VB','q90VB']

cal_metric=metrics_list[0]
df_skill_metric=pd.read_csv('Skill_Score_%s_Runoff_CAMELS_CLM-%s.csv'%(cal_metric,cal_metric))
df_skill_metric.columns=['NLDAS2','ERA5','Livneh','PRISM','Daymet',
                      'Basin_ID','Lat','Lon','Cluster']

df_metric_def=pd.read_csv('Default_%s_Runoff_CAMELS_CLM-%s.csv'%(cal_metric,cal_metric))
df_metric_def.columns=['NLDAS2','ERA5','Livneh','PRISM','Daymet',
                      'Basin_ID','Lat','Lon','Cluster']

df_metric_ens=pd.read_csv('Best_Ensemble_%s_Runoff_CAMELS_CLM-%s.csv'%(cal_metric,cal_metric))
df_metric_ens.columns=['NLDAS2','ERA5','Livneh','PRISM','Daymet',
                      'Basin_ID','Lat','Lon','Cluster']

clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']

###INPUT###
colorbar='YlGnBu_r'
###INPUT###

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


fig = plt.figure(figsize=(15, 15))
spec = fig.add_gridspec(5,3)
plt.rcParams.update({'font.size': 24}) 

df_features_cluster = pd.merge(df_features,df_cluster[['Num','Cluster']], on="Num")
df_features_cluster.rename(columns={'Gauge_Lat': 'LAT', 'Gauge_Lon': 'LON'}, inplace=True)

xlim = ([huc8_bounds[0]-2,  huc8_bounds[2]+1])
ylim = ([huc8_bounds[1]-1,  huc8_bounds[3]])

df_lat_lon=df_features_cluster[['LAT','LON']]


legend_orientation='vertical'
ii=-1
for forcing in ['NLDAS2','ERA5','Livneh','PRISM','Daymet']:
    ii=ii+1
    
    ############## Default ##############
    jj=0
    ax= fig.add_subplot(spec[ii,jj])
    gdf_data = gpd.GeoDataFrame(df_metric_def[forcing], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="2%",pad="-2%")
    # cax = divider.append_axes("bottom",size="5%",pad="20%")
    gdf_data.plot(column=forcing,ax=ax,zorder=3,markersize=100,
                    cmap=colorbar,legend=True,cax=cax,
                      categorical=False,vmin=-1,vmax=1,
                      legend_kwds={"orientation": legend_orientation})
        
    states_shp.plot(ax=ax, alpha=.1,edgecolor='black',legend=False)
    ax.tick_params(axis='both',direction='in', length=15, width=2,grid_alpha=0.5)
    if ii==0:
        ax.title.set_text('Default Parameters')
    ############## Best Ensemlbe ##############
    jj=1
    ax= fig.add_subplot(spec[ii,jj])
    gdf_data = gpd.GeoDataFrame(df_metric_ens[forcing], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="2%",pad="-2%")
    gdf_data.plot(column=forcing,ax=ax,zorder=3,markersize=100,
                    cmap=colorbar,legend=True,cax=cax,
                      categorical=False,vmin=-1,vmax=1,
                      legend_kwds={"orientation": legend_orientation})
      
    states_shp.plot(ax=ax, alpha=.1,edgecolor='black',legend=False)
    ax.tick_params(axis='both',direction='in', length=15, width=2,grid_alpha=0.5)
    if ii==0:
        ax.title.set_text('Default Parameters')
    
    ############## CSS ##############
    jj=2
    ax= fig.add_subplot(spec[ii,jj])
    gdf_data = gpd.GeoDataFrame(df_skill_metric[forcing], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right",size="2%",pad="-2%")
    gdf_data.plot(column=forcing,ax=ax,zorder=3,markersize=100,
                    cmap=colorbar,legend=True,cax=cax,
                      categorical=False,vmin=0,vmax=1,
                      legend_kwds={"orientation": legend_orientation})
    
    
    states_shp.plot(ax=ax, alpha=.1,edgecolor='black',legend=False)
    ax.tick_params(axis='both',direction='in', length=15, width=2,grid_alpha=0.5)
    if ii==0:
        ax.title.set_text('Default Parameters')



