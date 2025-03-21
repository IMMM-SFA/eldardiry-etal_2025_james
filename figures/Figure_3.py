# %% Importing Packages
import os
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import shapefile as shp
import seaborn as sns
from sklearn.metrics import mean_squared_error


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

# %% Evaluation Metrics
n=len(df_features)
num_basin=n
# Forcing Data:
# 0-year
# 1-month
# 2-daily
# 3-hour
# 4-surface pressure (pa)
# 5-Tair (K)
# 6-Wind speed (m/s) 
# 7-specific humidity (kg/kg)
# 8-precip (mm/s)
# 9-shortwave (W/m2)
# 10-longwave (W/m2)

prism_dir=wd+'\\Datasets\\CAMELS_CLM_Forcing\\PRISM'


forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']
forcing=forcing_list[0]
forcing_dir=wd+'\\Datasets\\CAMELS_CLM_Forcing\\%s'%forcing


startYear=2005
endYear=2014

for forcing in forcing_list:
    forcing_dir='\\Datasets\\CAMELS_CLM_Forcing\\%s'%forcing
    df_precip= pd.DataFrame([]) 
    df_precip= pd.concat([df_precip,df_features_cluster[['Gauge_ID','LAT','LON','Cluster']]],axis=1)
    df_precip['Pavg']= np.nan
    df_precip['Pmax']= np.nan
    df_precip['Pmin']= np.nan
    df_precip['Pstd']= np.nan
    df_precip['Pcorr']= np.nan
    df_precip['Prmse']= np.nan
    
    df_temp= pd.DataFrame([]) 
    df_temp= pd.concat([df_temp,df_features_cluster[['Gauge_ID','LAT','LON','Cluster']]],axis=1)
    df_temp['Tavg']= np.nan
    df_temp['Tmax']= np.nan
    df_temp['Tmin']= np.nan
    df_temp['Tstd']= np.nan
    df_temp['Tcorr']= np.nan
    df_temp['Trmse']= np.nan

    for i in range(n): 
        
        gauge_id=df_features_cluster['Gauge_ID'].loc[i]
        
        print(i+1,'---> Reading %s Forcing for CAMELS %s....'%(forcing, gauge_id))
        
        fname='basin_'+gauge_id
        
        ######################### Reading PRISM as Reference ###############
        os.chdir(prism_dir)
        df_camels_prism=pd.read_csv(fname,sep=' ',header=None)            
        df_camels_prism.columns = ['Year','Month','Day','Hour','PSRF','Temp','Wind','SHUM','Precip','SRAD','LRAD']
                                                   
                                                    
        df_hourly_precip=df_camels_prism[['Year','Month','Day','Hour','Precip']]
        df_hourly_precip=df_hourly_precip[(df_hourly_precip['Year']>=startYear) & (df_hourly_precip['Year']<=endYear)]
        df_hourly_precip=df_hourly_precip.reset_index(drop=True)
        df_hourly_precip['Precip']=df_hourly_precip['Precip']*3600
        df_daily_precip_prism=df_hourly_precip.groupby(['Year','Month','Day'])['Precip'].sum().reset_index()
        
        
        df_hourly_temp=df_camels_prism[['Year','Month','Day','Hour','Temp']]
        df_hourly_temp=df_hourly_temp[(df_hourly_temp['Year']>=startYear) & (df_hourly_temp['Year']<=endYear)]
        df_hourly_temp=df_hourly_temp.reset_index(drop=True)
        df_hourly_temp['Temp']=df_hourly_temp['Temp']-273.15
        df_daily_temp_prism=df_hourly_temp.groupby(['Year','Month','Day'])['Temp'].mean().reset_index()
        
        
        ##################### Reading Forcing Variables #####################
        os.chdir(forcing_dir)
        df_camels_forcing=pd.read_csv(fname,sep=' ',header=None)            
        df_camels_forcing.columns = ['Year','Month','Day','Hour','PSRF','Temp','Wind','SHUM','Precip','SRAD','LRAD']
                                                   
                                                    
        df_hourly_precip=df_camels_forcing[['Year','Month','Day','Hour','Precip']]
        df_hourly_precip=df_hourly_precip[(df_hourly_precip['Year']>=startYear) & (df_hourly_precip['Year']<=endYear)]
        df_hourly_precip=df_hourly_precip.reset_index(drop=True)
        df_hourly_precip['Precip']=df_hourly_precip['Precip']*3600
        
        df_hourly_temp=df_camels_forcing[['Year','Month','Day','Hour','Temp']]
        df_hourly_temp=df_hourly_temp[(df_hourly_temp['Year']>=startYear) & (df_hourly_temp['Year']<=endYear)]
        df_hourly_temp=df_hourly_temp.reset_index(drop=True)
        df_hourly_temp['Temp']=df_hourly_temp['Temp']-273.15
        
        
        tmp=df_hourly_precip.groupby(['Year'])['Precip'].sum().reset_index()
        df_precip.loc[i,'Pavg']=tmp.Precip.mean()
        df_precip.loc[i,'Pmax']=tmp.Precip.max()
        df_precip.loc[i,'Pmin']=tmp.Precip.min()
        df_daily_precip=df_hourly_precip.groupby(['Year','Month','Day'])['Precip'].sum().reset_index()
        df_precip.loc[i,'Pstd']=tmp.Precip.std()
        df_precip.loc[i,'Pcorr']=np.corrcoef(df_daily_precip['Precip'].values,df_daily_precip_prism['Precip'].values)[0,1]
        df_precip.loc[i,'Prmse'] = mean_squared_error(df_daily_precip_prism['Precip'].values, df_daily_precip['Precip'].values)
        
        
        
        tmp=df_hourly_temp.groupby(['Year'])['Temp'].mean().reset_index()
        df_temp.loc[i,'Tavg']=tmp.Temp.mean()
        df_temp.loc[i,'Tmax']=tmp.Temp.max()
        df_temp.loc[i,'Tmin']=tmp.Temp.min()
        df_daily_temp=df_hourly_temp.groupby(['Year','Month','Day'])['Temp'].mean().reset_index()
        df_temp.loc[i,'Tstd']=tmp.Temp.std()
        df_temp.loc[i,'Tcorr']=np.corrcoef(df_daily_temp['Temp'].values,df_daily_temp_prism['Temp'].values)[0,1]
        df_temp.loc[i,'Trmse'] = mean_squared_error(df_daily_temp_prism['Temp'].values, df_daily_temp['Temp'].values)
        

    # Save the metrics in CSV files    
    os.chdir(wd+'\\Outputs')
    
    df_precip.to_csv("CAMELS_%s_Annual_Precip_2005_2014.csv"%forcing, sep = ',')
    df_temp.to_csv("CAMELS_%s_Annual_Temp_2005_2014.csv"%forcing, sep = ',')
    del df_precip
    del df_temp


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


# %% Calculate matrix for Spatial plots
os.chdir('\\Outputs')
forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']

clusterName=['Northeast','Pacific','AZ/NM','Rockies','Great Plains','Great Lakes','Southeast']

df_precip_all=pd.DataFrame([])
for forcing in forcing_list:
    df_precip=pd.read_csv("CAMELS_%s_Annual_Precip_2005_2014.csv"%forcing,index_col=0,dtype={'Gauge_ID': str})
    df_precip['Forcing']=forcing
    df_precip_all=pd.concat([df_precip_all,df_precip],axis=0)

df_precip_all_cluster=df_precip_all.groupby(['Cluster','Forcing']).mean().reset_index()

df_pavg_all=pd.DataFrame([])
for forcing in forcing_list:
    df_precip=pd.read_csv("CAMELS_%s_Annual_Precip_2005_2014.csv"%forcing,index_col=0,dtype={'Gauge_ID': str})
    tmp=df_precip.groupby(['Cluster'])['Pavg'].mean().reset_index()    
    tmp.columns=['Cluster',forcing]
    df_pavg_all=pd.concat([df_pavg_all,tmp[[forcing]]],axis=1)

df_pavg_all['Cluster']=clusterName
df_pavg_all.index=df_pavg_all.Cluster
df_pavg_all=df_pavg_all.drop('Cluster',axis=1)

df_tavg_all=pd.DataFrame([])
for forcing in forcing_list:
    df_temp=pd.read_csv("CAMELS_%s_Annual_Temp_2005_2014.csv"%forcing,index_col=0,dtype={'Gauge_ID': str})
    tmp=df_temp.groupby(['Cluster'])['Tavg'].mean().reset_index()    
    tmp.columns=['Cluster',forcing]
    df_tavg_all=pd.concat([df_tavg_all,tmp[[forcing]]],axis=1)

df_tavg_all['Cluster']=clusterName
df_tavg_all.index=df_tavg_all.Cluster
df_tavg_all=df_tavg_all.drop('Cluster',axis=1)


# %% Spatial Maps and Heatmap for both Precip and Temp
os.chdir(wd+'\\Outputs')

forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']
forcing='NLDAS2'
df_precip=pd.read_csv("CAMELS_%s_Annual_Precip_2005_2014.csv"%forcing,index_col=0,dtype={'Gauge_ID': str})
df_temp=pd.read_csv("CAMELS_%s_Annual_Temp_2005_2014.csv"%forcing,index_col=0,dtype={'Gauge_ID': str})



fig, axes = plt.subplots(2,1,figsize=(15,15))
plt.rcParams.update({'font.size': 24})       
axes=axes.ravel()


########################### PAVG ###########################       
ax=axes[0]

gdf_data = gpd.GeoDataFrame(df_precip['Pavg'], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
states_shp.plot(ax=ax, alpha=.1,edgecolor='black',legend=False)

divider = make_axes_locatable(ax)
cax = divider.append_axes("right",size="2%",pad="2%")
gdf_data.plot(column='Pavg',ax=ax,zorder=3,markersize=100,
                cmap='RdYlBu',legend=True,
                  cax=cax,categorical=False, vmin=350,vmax=3000)
ax.title.set_text('Total Annual Precipitation (mm)')

xlim = ([huc8_bounds[0]-3,  huc8_bounds[2]+1])
ylim = ([huc8_bounds[1]-2,  huc8_bounds[3]])
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_facecolor('whitesmoke')

############################ PAVG ###########################

ins = ax.inset_axes([0.03, 0.06, 0.36, 0.24])
df_pavg_all.index=[1,2,3,4,5,6,7]
df_pavg_all.columns=['N','W','L','P','D']
sns.heatmap(df_pavg_all.T,
            ax=ins,cmap='RdYlBu',cbar=False,yticklabels=['N','W','L','P','D'],
            xticklabels=[1,2,3,4,5,6,7],
            vmin=350,vmax=3000,linewidth=.5) 

ins.set_ylabel('')
ins.set_xlabel('')
ins.invert_yaxis()
ins.set_xticklabels([1,2,3,4,5,6,7], fontsize = 16,fontweight="bold")
ins.set_yticklabels(['N','W','L','P','D'], fontsize = 16,fontweight="bold")
for spine in ins.spines.values():
    spine.set(visible=True,lw=.8, edgecolor="black")


########################### TAVG ###########################
ax=axes[1]
gdf_data = gpd.GeoDataFrame(df_temp['Tavg'], geometry=gpd.points_from_xy(df_lat_lon.LON, df_lat_lon.LAT))
states_shp.plot(ax=ax, alpha=.1,edgecolor='black',legend=False)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right",size="2%",pad="2%")
gdf_data.plot(column='Tavg',ax=ax,zorder=3,markersize=100,
                cmap='RdYlBu_r',legend=True,
                  cax=cax,categorical=False,vmin=-2,vmax=25)

ax.title.set_text('Average Temperature (℃)')

ax.set_facecolor('whitesmoke')


# ########################### TAVG ###########################

ins = ax.inset_axes([0.03, 0.06, 0.36, 0.24])
df_tavg_all.index=[1,2,3,4,5,6,7]
df_tavg_all.columns=['N','W','L','P','D']

sns.heatmap(df_tavg_all.T,
            ax=ins,cmap='RdYlBu_r',cbar=False,yticklabels=['N','W','L','P','D'],
            xticklabels=[1,2,3,4,5,6,7],
            vmin=-2,vmax=25,linewidth=.5) 

ins.invert_yaxis()
ins.set_ylabel('')
ins.set_xlabel('')
ins.set_xticklabels([1,2,3,4,5,6,7], fontsize = 16,fontweight="bold")
ins.set_yticklabels(['N','W','L','P','D'], fontsize = 16,fontweight="bold")
for spine in ins.spines.values():
    spine.set(visible=True,lw=.8, edgecolor="black")