# %% Importing Packages
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.distributions.empirical_distribution import ECDF
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

# %% rugplot function

def upper_rugplot(data, height=.05, ax=None, **kwargs):
    from matplotlib.collections import LineCollection
    ax = ax or plt.gca()
    kwargs.setdefault("linewidth", 1)
    segs = np.stack((np.c_[data, data],
                     np.c_[np.ones_like(data), np.ones_like(data)-height]),
                    axis=-1)
    lc = LineCollection(segs, transform=ax.get_xaxis_transform(), **kwargs)
    ax.add_collection(lc)

# %% Selected Events
df_selected_events=pd.read_csv(wd+'\\Scripts\\NCEI_Selected_Events_CA_TX.csv',dtype={'CAMELS': str})
df_selected_events=pd.read_csv(wd+'\\Scripts\\NCEI_Selected_Events_CA_TX.csv',dtype={'CAMELS': str})
                 
           
# %% TX Events
ii=[2,3]   # choose indices for TX
df_selected_events_TX=df_selected_events.iloc[ii].reset_index(drop=True)

########################## Load Runoff

Nevents=len(df_selected_events)

df_qobs_flood_TX=pd.read_csv(wd+'\\Outputs\\Qobs_Basin_%s'%df_selected_events_TX.iloc[0]['CAMELS'])
df_qobs_flood_TX=df_qobs_flood_TX[df_qobs_flood_TX['Year']>2004].reset_index(drop=True)
df_qobs_flood_monthly_TX=df_qobs_flood_TX.groupby(['Year','Month']).mean().reset_index().drop(['Day'],axis=1)

df_flood_event_TX=df_qobs_flood_TX[(df_qobs_flood_TX['Year']>=df_selected_events_TX.iloc[0]['Start_Year']) 
                    & (df_qobs_flood_TX['Year']<=df_selected_events_TX.iloc[0]['End_Year'])
                    & (df_qobs_flood_TX['Month']>=df_selected_events_TX.iloc[0]['Start_Month'])
                    & (df_qobs_flood_TX['Month']<=df_selected_events_TX.iloc[0]['End_Month'])
                    & (df_qobs_flood_TX['Day']>=df_selected_events_TX.iloc[0]['Start_Day'])
                    & (df_qobs_flood_TX['Day']<=df_selected_events_TX.iloc[0]['End_Day'])]

df_flood_event_TX=df_flood_event_TX.reset_index(drop=True)

df_qobs_drought_TX=pd.read_csv(wd+'\\Outputs\\Qobs_Basin_%s'%df_selected_events_TX.iloc[1]['CAMELS'])
df_qobs_drought_TX=df_qobs_drought_TX[df_qobs_drought_TX['Year']>2004].reset_index(drop=True)

df_qobs_drought_monthly_TX=df_qobs_drought_TX.groupby(['Year','Month']).mean().reset_index().drop(['Day'],axis=1)
df_drought_event_TX=df_qobs_drought_monthly_TX[(df_qobs_drought_monthly_TX['Year']>=df_selected_events_TX.iloc[1]['Start_Year']) 
                    & (df_qobs_drought_monthly_TX['Year']<=df_selected_events_TX.iloc[1]['End_Year'])
                    & (df_qobs_drought_monthly_TX['Month']>=df_selected_events_TX.iloc[1]['Start_Month'])
                    & (df_qobs_drought_monthly_TX['Month']<=df_selected_events_TX.iloc[1]['End_Month'])]
                    
df_drought_event_TX=df_drought_event_TX.reset_index(drop=True)

#######################Calculate ECDF

df_tmp1=df_qobs_flood_TX.copy()
df_tmp1['Event']='Flood'
ecdf1=ECDF((df_tmp1.Qobs.values))
df_tmp1['ECDF']=ecdf1((df_tmp1.Qobs.values))

df_tmp1_selected_TX=df_tmp1[(df_tmp1['Year']>=df_selected_events_TX.iloc[0]['Start_Year']) 
                    & (df_tmp1['Year']<=df_selected_events_TX.iloc[0]['End_Year'])
                    & (df_tmp1['Month']>=df_selected_events_TX.iloc[0]['Start_Month'])
                    & (df_tmp1['Month']<=df_selected_events_TX.iloc[0]['End_Month'])
                    & (df_tmp1['Day']>=df_selected_events_TX.iloc[0]['Start_Day'])
                    & (df_tmp1['Day']<=df_selected_events_TX.iloc[0]['End_Day'])]



df_tmp2=df_qobs_drought_monthly_TX.copy()
df_tmp2['Event']='Drought'
ecdf2=ECDF(df_tmp2.Qobs.values)
df_tmp2['ECDF']=ecdf2(df_tmp2.Qobs.values)
df_tmp2_selected_TX=df_tmp2[(df_tmp2['Year']>=df_selected_events_TX.iloc[1]['Start_Year']) 
                    & (df_tmp2['Year']<=df_selected_events_TX.iloc[1]['End_Year'])
                    & (df_tmp2['Month']>=7)
                    & (df_tmp2['Month']<=9)
                    ]
            

df_qobs_all_TX=pd.concat([df_tmp1,df_tmp2],axis=0).reset_index(drop=True)

# %% CA Event
ii=[0,4]   # choose indices for CA
df_selected_events_CA=df_selected_events.iloc[ii].reset_index(drop=True)

########################## Load Runoff

Nevents=len(df_selected_events)

df_qobs_flood_CA=pd.read_csv(wd+'\\Outputs\\Qobs_Basin_%s'%df_selected_events_CA.iloc[0]['CAMELS'])
df_qobs_flood_CA=df_qobs_flood_CA[df_qobs_flood_CA['Year']>2004].reset_index(drop=True)
df_qobs_flood_monthly=df_qobs_flood_CA.groupby(['Year','Month']).mean().reset_index().drop(['Day'],axis=1)

df_flood_event_CA=df_qobs_flood_CA[(df_qobs_flood_CA['Year']>=df_selected_events_CA.iloc[0]['Start_Year']) 
                    & (df_qobs_flood_CA['Year']<=df_selected_events_CA.iloc[0]['End_Year'])
                    & (df_qobs_flood_CA['Month']>=df_selected_events_CA.iloc[0]['Start_Month'])
                    & (df_qobs_flood_CA['Month']<=df_selected_events_CA.iloc[0]['End_Month'])
                    & (df_qobs_flood_CA['Day']>=df_selected_events_CA.iloc[0]['Start_Day'])
                    & (df_qobs_flood_CA['Day']<=df_selected_events_CA.iloc[0]['End_Day'])]

df_flood_event_CA=df_flood_event_CA.reset_index(drop=True)

df_qobs_drought_CA=pd.read_csv(wd+'\\Outputs\\Qobs_Basin_%s'%df_selected_events_CA.iloc[1]['CAMELS'])
df_qobs_drought_CA=df_qobs_drought_CA[df_qobs_drought_CA['Year']>2004].reset_index(drop=True)

df_qobs_drought_monthly_CA=df_qobs_drought_CA.groupby(['Year','Month']).mean().reset_index().drop(['Day'],axis=1)
df_drought_event_CA=df_qobs_drought_monthly_CA[(df_qobs_drought_monthly_CA['Year']>=df_selected_events_TX.iloc[1]['Start_Year']) 
                    & (df_qobs_drought_monthly_CA['Year']<=df_selected_events_CA.iloc[1]['End_Year'])
                    & (df_qobs_drought_monthly_CA['Month']>=df_selected_events_CA.iloc[1]['Start_Month'])
                    & (df_qobs_drought_monthly_CA['Month']<=df_selected_events_CA.iloc[1]['End_Month'])]
                    
df_drought_event_CA=df_drought_event_CA.reset_index(drop=True)

#######################Calculate ECDF

df_tmp1=df_qobs_flood_CA.copy()
df_tmp1['Event']='Flood'
ecdf1=ECDF((df_tmp1.Qobs.values))
df_tmp1['ECDF']=ecdf1((df_tmp1.Qobs.values))

df_tmp1_selected_CA=df_tmp1[(df_tmp1['Year']>=df_selected_events_CA.iloc[0]['Start_Year']) 
                    & (df_tmp1['Year']<=df_selected_events_CA.iloc[0]['End_Year'])
                    & (df_tmp1['Month']>=df_selected_events_CA.iloc[0]['Start_Month'])
                    & (df_tmp1['Month']<=df_selected_events_CA.iloc[0]['End_Month'])
                    & (df_tmp1['Day']>=df_selected_events_CA.iloc[0]['Start_Day'])
                    & (df_tmp1['Day']<=df_selected_events_CA.iloc[0]['End_Day'])]



df_tmp2=df_qobs_drought_monthly_CA.copy()
df_tmp2['Event']='Drought'
ecdf2=ECDF(df_tmp2.Qobs.values)
df_tmp2['ECDF']=ecdf2(df_tmp2.Qobs.values)
df_tmp2_selected_CA=df_tmp2[(df_tmp2['Year']>=df_selected_events_TX.iloc[1]['Start_Year']) 
                    & (df_tmp2['Year']<=df_selected_events_TX.iloc[1]['End_Year'])
                    & (df_tmp2['Month']>=7)
                    & (df_tmp2['Month']<=9)
                    ]
            

df_qobs_all_CA=pd.concat([df_tmp1,df_tmp2],axis=0).reset_index(drop=True)

# %% Plot CDF with rugplot

myfontsize=30
fig, axes = plt.subplots(1,2,figsize=(15,15))
plt.rcParams.update({'font.size': myfontsize})


sns.set_style("whitegrid")
sns.set_theme()
axes=axes.ravel()
ax=axes[0]
sb=sns.ecdfplot(data=df_qobs_flood_TX, x="Qobs",
             ax=ax,color='darkblue',linewidth = 8,label='_nolegend_')
sns.rugplot(data=df_qobs_flood_TX, x="Qobs",ax=ax,
            color='darkblue',label='_nolegend_')

ax.scatter(x=df_tmp1_selected_TX.Qobs, y=df_tmp1_selected_TX.ECDF,
                marker='o',s=600,alpha=0.8,
                color='darkblue')

ax.set_xlabel('Daily Qobs ($m^3$/sec)',fontsize = myfontsize)
ax.set_ylabel('CDF',fontsize = myfontsize)
ax.tick_params(axis='x', labelsize=myfontsize)
ax.tick_params(axis='y', labelsize=myfontsize)

ax=ax.twiny()
sns.ecdfplot(data=df_qobs_drought_monthly_TX, 
             x="Qobs",color='darkred',
             ax=ax,linewidth = 8,label='_nolegend_')
upper_rugplot(df_qobs_drought_monthly_TX.Qobs.values, ax=ax,
              color='darkred',label='_nolegend_')

ax.scatter(x=df_tmp2_selected_TX.Qobs, y=df_tmp2_selected_TX.ECDF,
                marker='o',s=600,alpha=0.8,
                color='darkred')

ax.set_xlabel('Mean Monthly Qobs ($m^3$/sec)',fontsize = myfontsize,labelpad=20)
ax.tick_params(axis='x', labelsize=myfontsize)
ax.tick_params(axis='y', labelsize=myfontsize)
ax.legend(['Drought'],loc='center right',fontsize = myfontsize)

############################ CA Events
ax=axes[1]

sns.ecdfplot(data=df_qobs_flood_CA, x="Qobs",
             ax=ax,color='darkblue',linewidth = 8,label='_nolegend_')
sns.rugplot(data=df_qobs_flood_CA, x="Qobs",ax=ax,
            color='darkblue',label='_nolegend_')
ax.scatter(x=df_tmp1_selected_CA.Qobs, y=df_tmp1_selected_CA.ECDF,
                marker='o',s=600,alpha=0.8,
                color='darkblue')

ax.set_xlabel('Daily Qobs ($m^3$/sec)',fontsize = myfontsize)
ax.set_ylabel('',fontsize = myfontsize)
ax.tick_params(axis='x', labelsize=myfontsize)
ax.tick_params(axis='y', labelsize=myfontsize)
ax.legend(['Flood'],loc='center right',fontsize = myfontsize)

ax=ax.twiny()
sns.ecdfplot(data=df_qobs_drought_monthly_CA, 
             x="Qobs",color='darkred',
             ax=ax,linewidth = 8,label='_nolegend_')
upper_rugplot(df_qobs_drought_monthly_CA.Qobs.values, ax=ax,
              color='darkred',label='_nolegend_')

ax.scatter(x=df_tmp2_selected_CA.Qobs, y=df_tmp2_selected_CA.ECDF,
                marker='o',s=600,alpha=0.8,
                color='darkred')

ax.set_xlabel('Mean Monthly Qobs ($m^3$/sec)',fontsize = myfontsize,labelpad=20)
ax.tick_params(axis='x', labelsize=myfontsize)
ax.tick_params(axis='y', labelsize=myfontsize)
