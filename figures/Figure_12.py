# %% Importing Packages
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import shapefile as shp
import geopandas as gpd

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

# %% Load Metrics

# metrics to describe hydrograph or flow dynamics
metrics_1=['KGE','MAE','TRMSE','FDC']

# metrics for water balance and reservoir operations
metrics_2=['VB','VarB','fallVB','winVB','sprVB','sumVB','AVB']

#metrics for high and low flow for flood and drought applications
metrics_3=['q10VB','q90VB']

metrics_names=metrics_1+metrics_2+metrics_3

mm=0
metric=metrics_names[mm]



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

# %%  Plot Effect of Interaction Term
df_SS=pd.read_csv(wd+'/outputs/ANOVA_Interaction_%s_Runoff_CAMELS_NWLPD.csv'%metric, sep = '\t')
clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']
df_SS['pct_SSf']=df_SS['SSf']/(df_SS['SSp']+df_SS['SSf']+df_SS['SSpf'])*100
df_SS['pct_SSp']=df_SS['SSp']/(df_SS['SSp']+df_SS['SSf']+df_SS['SSpf'])*100
df_SS['pct_SSpf']=df_SS['SSpf']/(df_SS['SSp']+df_SS['SSf']+df_SS['SSpf'])*100
df_uc=pd.DataFrame([],columns=['Cluster','Forcing','Parametric','Interaction'])
for i in range(0,7):
    x=df_SS[df_SS['Cluster']==i+1]['pct_SSp']
    y=df_SS[df_SS['Cluster']==i+1]['pct_SSf']
    z=df_SS[df_SS['Cluster']==i+1]['pct_SSpf']
    
    condition = (z > x) & (z > y)
    # Count the number of rows that satisfy the condition
    count = condition.sum()  # This gives the total number of True values
    npar_forc=count  # cases when interaction dominate the uncertainty
    
    condition = (x > y) & (x > z)
    # Count the number of rows that satisfy the condition
    count = condition.sum()  # This gives the total number of True values
    npar=count  # cases when interaction dominate the uncertainty
    
    condition = (y > x) & (y > z)
    # Count the number of rows that satisfy the condition
    count = condition.sum()  # This gives the total number of True values
    nforc=count  # cases when interaction dominate the uncertainty
    
    df_uc.loc[i,'Cluster']=i+1
    df_uc.loc[i,'Forcing']=nforc
    df_uc.loc[i,'Parametric']=npar
    df_uc.loc[i,'Interaction']=npar_forc


# Set the figure size
plt.figure(figsize=(10, 6))

# Bar chart width
bar_width = 0.25

# Set positions of the bars
index = np.arange(len(df_uc['Cluster']))

# Plot each of the three columns as a separate set of bars
plt.bar(index - bar_width, df_uc['Parametric'], bar_width, label='Parametric', color='#003366')
plt.bar(index, df_uc['Forcing'], bar_width, label='Forcing', color='#9e1b32')
plt.bar(index + bar_width, df_uc['Interaction'], bar_width, label='Parametric x Forcing (Interaction)', color='grey')

# Labeling the axes and title
plt.xlabel('')
plt.ylabel('Number of Basins')
# plt.title('Uncertainty Dominant Factor')

# Customize the x-axis ticks to show Cluster numbers
plt.xticks(index, clusterName, rotation=45)  # Rotate x-axis labels by 45 degrees

# Add a legend
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()