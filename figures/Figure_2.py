# %% Importing Packages
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import geopandas as gpd
import cartopy.crs as ccrs
import contextily as cx
from matplotlib.colors import ListedColormap

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

# %% Plot Figure 
cluster_labels=['Northeast','Pacific','Az/NM','Rockies','Great Plains',
                  'Great Lakes','Southeast']

camel_path = r'Shapefiles\camels_epsg4326\camels_epsg4326.shp'
states_path = r'Shapefiles\cb_2015_us_state_500k\cb_2015_us_state_500k.shp'
counties_path = r'Shapefiles\cb_2015_us_county_500k\cb_2015_us_county_500k.shp'
camel_shp=gpd.read_file(camel_path)
camel_shp_selected = pd.merge(df_features_cluster, camel_shp, left_on=['Gauge_ID'],right_on=['GAGEID'], how='left')
states_shp=gpd.read_file(states_path)
counties_shp=gpd.read_file(counties_path)
camel_bounds = camel_shp.geometry.total_bounds

fig, axes = plt.subplots(1,1,figsize=(15,15))
plt.rcParams.update({'font.size': 26}) 


xlim = ([camel_bounds[0]-2,  camel_bounds[2]+2])
ylim = ([camel_bounds[1]-3,  camel_bounds[3]+1])

ax=axes  
ax.set_xlim(xlim)
ax.set_ylim(ylim)

######## Plot CAMELS basins
gdf_data= gpd.GeoDataFrame(camel_shp_selected.copy())
gdf_data.plot(column='Cluster',ax=ax,zorder=3,markersize=40,
                legend=True,categorical=True)

leg = ax.get_legend()
leg.set_title("Cluster")
for i, label in enumerate(cluster_labels):
    leg.get_texts()[i].set_text(label)




######## Plot CAMELS selected for high imapct events

selected_camels=['11266500','08175000']
df_selected=df_features_cluster[df_features_cluster['Gauge_ID'].isin(selected_camels)]
gdf_selected = gpd.GeoDataFrame(df_selected, geometry=gpd.points_from_xy(df_selected.LON, df_selected.LAT))
gdf_selected.plot(column='Cluster',ax=ax,zorder=3,markersize=200,
                 legend=False,color='black',marker='o')

states_shp.plot(ax=ax, alpha=.1,edgecolor='black')
# counties_shp.plot(ax=ax, alpha=.1,edgecolor='black')
# camel_shp.plot(ax=ax, alpha=.1,edgecolor='greenyellow')
ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.tick_params(axis='both',direction='in', length=15, width=2,grid_alpha=0.5)
ax.title.set_text('CAMELS Basins')
# for x, y, label in zip(df_selected.geometry.x, df_selected.geometry.y, df_selected.Gauge_ID):
#     ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")


# %% Stadia Maps
## Stamen stopped providing a base map service (October 2023)
## This was announced here: https://stamen.com/here-comes-the-future-of-stamen-maps/
## Their maps are now provided by Stadia: https://stadiamaps.com/stamen/

import geopandas
import geodatasets

df = geopandas.read_file(geodatasets.get_path("nybb"))
ax = df.plot(figsize=(10, 10), alpha=0.5, edgecolor="k")

# Old
#cx.add_basemap(ax, crs=df.crs, source=cx.providers.Stamen.Terrain)
# New
cx.add_basemap(ax, crs=df.crs, source='https://tiles.stadiamaps.com/tiles/stamen_terrain_background/{z}/{x}/{y}{r}.png?api_key=c4f76284-07c5-4ac3-bd1a-f8509649c993')



# %% Plot CAMELS
# Cartopy maps from Stadia

cluster_palette=['red','blue','olive','gold','magenta','peru','green']
cluster_labels=['Cluster 1-Northeast [104]','Cluster 2-Pacific [73]',
                'Cluster 3-AZ/NM [7]',
                'Cluster 4-Rockies [58]','Cluster 5-Great Plains [51]',
                  'Cluster 6-Midwest [66]','Cluster 7-Southeast [105]']


fig, axes = plt.subplots(1,1,figsize=(15,15))
plt.rcParams.update({'font.size': 20})
ax=axes
ax = plt.axes(projection=ccrs.PlateCarree()) # project using coordinate reference system (CRS) of street map

gdf_data= gpd.GeoDataFrame(camel_shp_selected)
gdf_data.plot(column='Cluster',ax=ax,markersize=40,
                legend=True,legend_kwds={'loc': 'lower right'}, 
                cmap=ListedColormap(cluster_palette),
                categorical=True,transform=ccrs.PlateCarree(),
                edgecolor="face", linewidth=0.4)

leg = ax.get_legend()
leg.set_title("Cluster [Number of Basins]")


for i, label in enumerate(cluster_labels):
    leg.get_texts()[i].set_text(label)


selected_camels=['11266500','08175000']
df_selected=df_features_cluster[df_features_cluster['Gauge_ID'].isin(selected_camels)]
gdf_selected = gpd.GeoDataFrame(df_selected, geometry=gpd.points_from_xy(df_selected.LON, df_selected.LAT))
gdf_selected.plot(column='Cluster',ax=ax,zorder=1,markersize=400,
                 legend=False,marker='*',
                 color='black',transform=ccrs.PlateCarree())

states_shp.plot(ax=ax, alpha=1,edgecolor='black')

cx.add_basemap(ax, crs=gdf_data.crs, source='https://tiles.stadiamaps.com/tiles/stamen_terrain_background/{z}/{x}/{y}{r}.png?api_key=c4f76284-07c5-4ac3-bd1a-f8509649c993')



# %% supplementary plots for the variables of camels 

cluster_palette=['red','blue','olive','gold','magenta','peru','green']
sns.set_style("whitegrid")
sns.set_theme()
sns.set(font_scale=3)


sb=sns.relplot(data=df_features_cluster, 
               x='ELEV', y='ARIDITY', 
            hue='Cluster', s=400,palette=cluster_palette,
            legend=False
            )


sb.set(xlabel ="Elevation (m)", ylabel = "Aridity",
        xlim=(-30,3700),ylim=(0,3.5),facecolor='whitesmoke')

# sb.set(rc={'figure.facecolor':'red'})

selected_camels=['11266500','08175000']
df_selected=df_features_cluster[df_features_cluster['Gauge_ID'].isin(selected_camels)]

axes = sb.axes.flatten()
for ax in axes:
    
    df_selected.plot.scatter( 
               x='ELEV', y='ARIDITY', 
            s=1200,marker='*',c='k',
            legend=False,ax=ax
            )

ax.set_xlabel('Elevation (m)')
ax.set_ylabel('Aridity')
