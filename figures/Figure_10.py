# %% Importing Packages
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
# %% USer Defined Functions
# % Drought Classes
def drought_class(SRI):
    if (SRI<=-0.5) and (SRI>=-0.7):
        drought='D0'
    elif (SRI<-0.7) and (SRI>=-1.2):
        drought='D1'
    elif (SRI<-1.2) and (SRI>=-1.5):
        drought='D2'
    elif (SRI<-1.5) and (SRI>=-1.9):
        drought='D3'    
    elif (SRI<-1.9):
        drought='D4'
    elif (SRI<=0) and (SRI>-0.5):
        drought='N'
    elif math.isnan(SRI):   
        drought='NA'
    else: 
        drought='N'
    return drought 


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

# %% Select Events
df_selected_events=pd.read_csv(wd+'\\Scripts\\NCEI_Selected_Events_CA_TX.csv',dtype={'CAMELS': str})

# ii=[2,3]   # choose indices for TX
ii=[3,4]   # choose indices for drought in TX and CA
df_selected_events=df_selected_events.iloc[ii].reset_index(drop=True)

drought_title_TX1='TX %d Drought at CAMELS %s [September]'%(df_selected_events.Start_Year[0],df_selected_events.CAMELS[0])
drought_title_TX2='TX %d Drought at CAMELS %s [KGE Metric]'%(df_selected_events.Start_Year[0],df_selected_events.CAMELS[0])

drought_title_CA1='CA %d Drought at CAMELS %s [January]'%(df_selected_events.Start_Year[1],df_selected_events.CAMELS[1])
drought_title_CA2='CA %d Drought at CAMELS %s [KGE Metric]'%(df_selected_events.Start_Year[1],df_selected_events.CAMELS[1])





  
# %%  Heatmap for SRI
forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']
metrics=['KGE','MAE','VARB',
         'AVB','fallVB','winVB','sprVB','sumVB',
         'q10VB','q90VB']

selected_metric=['KGE']

myfontsize=25
fig, axes = plt.subplots(2,2,figsize=(15,15))
plt.rcParams.update({'font.size': myfontsize})

axes=axes.ravel()


##########################################################
ax=axes[0]


### Select Months and State

i=0  # Texas
driest_month=6
basinID=df_selected_events.loc[i]['CAMELS']
state=df_selected_events.loc[i]['State']
event=df_selected_events.loc[i]['Event']
start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])

df_drought_selected_month=pd.DataFrame([],columns=['Metric','NLDAS2','WRF','Livneh','PRISM','Daymet'])
for jj in range(0,len(metrics)):
    metric=metrics[jj]
    df_drought_forcing=pd.read_csv(r'\Outputs\Selected_Events_CA_TX\SRI\Drought_Class_%s_%s_%s_%s_%s_%s.csv'%(metric,event,state,basinID,start_date,end_date), sep = ',')
    df_tmp=df_drought_forcing[df_drought_forcing.index==driest_month-1].reset_index(drop=True)    
    df_tmp['Metric']=metric
    df_drought_selected_month=pd.concat([df_drought_selected_month,df_tmp],axis=0)

df_drought_selected_month=df_drought_selected_month.reset_index(drop=True)    
df_drought_selected_month.index=df_drought_selected_month.Metric
df_drought_selected_month=df_drought_selected_month[['USGS','NLDAS2','WRF','Livneh','PRISM','Daymet']]


df_drought_class=df_drought_selected_month.applymap(drought_class)
labels=df_drought_class

sns.heatmap(df_drought_selected_month, annot=labels, linewidths=.5, 
            ax=ax,fmt = '',cbar=True,vmin=-2,vmax=0,
            cbar_kws=dict(ticks=[-1.9,-1.5,-1.2,-0.7,-0.5,0]))
            


ax.set_facecolor('whitesmoke')
ax.invert_yaxis()
ax.set_yticklabels(metrics,rotation=0)
ax.set_xticklabels(['USGS','NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
ax.set_yticklabels(['KGE','MAE', 'VARB','AVB','Fall VB', 'Winter VB', 'Spring VB', 'Summer VB',
                    'Q10 VB', 'Q90 VB'])
ax.set_ylabel('')
ax.set_title(drought_title_TX1)

##########################################################
ax=axes[1]
### Select Months and State

i=1  # California
driest_month=4
basinID=df_selected_events.loc[i]['CAMELS']
state=df_selected_events.loc[i]['State']
event=df_selected_events.loc[i]['Event']
start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])

df_drought_selected_month=pd.DataFrame([],columns=['Metric','NLDAS2','WRF','Livneh','PRISM','Daymet'])
for jj in range(0,len(metrics)):
    metric=metrics[jj]
    df_drought_forcing=pd.read_csv(wd+r'\Outputs\Selected_Events_CA_TX\SRI\Drought_Class_%s_%s_%s_%s_%s_%s.csv'%(metric,event,state,basinID,start_date,end_date), sep = ',')
    df_tmp=df_drought_forcing[df_drought_forcing.index==driest_month-1].reset_index(drop=True)    
    df_tmp['Metric']=metric
    df_drought_selected_month=pd.concat([df_drought_selected_month,df_tmp],axis=0)

df_drought_selected_month=df_drought_selected_month.reset_index(drop=True)    
df_drought_selected_month.index=df_drought_selected_month.Metric
df_drought_selected_month=df_drought_selected_month[['USGS','NLDAS2','WRF','Livneh','PRISM','Daymet']]
df_drought_class=df_drought_selected_month.applymap(drought_class)
labels=df_drought_class

sns.heatmap(df_drought_selected_month, annot=labels, linewidths=.5, 
            ax=ax,fmt = '',cbar=True,vmin=-2,vmax=0,
            cbar_kws=dict(ticks=[-1.9,-1.5,-1.2,-0.7,-0.5,0]))


ax.set_facecolor('whitesmoke')
ax.invert_yaxis()
ax.set_yticklabels(metrics,rotation=0)
ax.set_xticklabels(['USGS','NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
ax.set_yticklabels(['KGE','MAE', 'VARB','AVB','Fall VB', 'Winter VB', 'Spring VB', 'Summer VB',
                    'Q10 VB', 'Q90 VB'])
ax.set_ylabel('')
ax.set_title(drought_title_CA1)

########################################################
ax=axes[2]
i=0  # Texas
jj=0  #Selected Metric
basinID=df_selected_events.loc[i]['CAMELS']
state=df_selected_events.loc[i]['State']
event=df_selected_events.loc[i]['Event']
start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])

df_drought_event=pd.DataFrame([],columns=['Month','NLDAS2','WRF','Livneh','PRISM','Daymet'])
metric=metrics[jj]
df_drought_forcing=pd.read_csv(wd+r'\Outputs\Selected_Events_CA_TX\SRI\Drought_Class_%s_%s_%s_%s_%s_%s.csv'%(metric,event,state,basinID,start_date,end_date), sep = ',')


df_drought_forcing=df_drought_forcing[['USGS','NLDAS2','WRF','Livneh','PRISM','Daymet']]
df_drought_class=df_drought_forcing.applymap(drought_class)
df_drought_class['Month']=np.arange(1,13)
df_drought_class.set_index('Month',inplace=True)

labels=df_drought_class
df_drought_forcing
sns.heatmap(df_drought_forcing, annot=labels, linewidths=.5, 
            ax=ax,fmt = '',cbar=True,vmin=-2,vmax=0,
            cbar_kws=dict(ticks=[-1.9,-1.5,-1.2,-0.7,-0.5,0]))
ax.set_facecolor('whitesmoke')
ax.invert_yaxis()
ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr',
                    'May','Jun','Jul',
                    'Aug','Sep','Oct',
                    'Nov','Dec'],rotation=0)
ax.set_xticklabels(['USGS','NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
ax.set_ylabel('')
ax.set_title(drought_title_TX2)

########################################################
ax=axes[3]
i=1  # Texas
jj=0  #Selected Metric
basinID=df_selected_events.loc[i]['CAMELS']
state=df_selected_events.loc[i]['State']
event=df_selected_events.loc[i]['Event']
start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])

df_drought_event=pd.DataFrame([],columns=['Month','NLDAS2','WRF','Livneh','PRISM','Daymet'])
metric=metrics[jj]
df_drought_forcing=pd.read_csv(wd+r'\Outputs\Selected_Events_CA_TX\SRI\Drought_Class_%s_%s_%s_%s_%s_%s.csv'%(metric,event,state,basinID,start_date,end_date), sep = ',')


df_drought_forcing=df_drought_forcing[['USGS','NLDAS2','WRF','Livneh','PRISM','Daymet']]
df_drought_class=df_drought_forcing.applymap(drought_class)
df_drought_class['Month']=np.arange(1,13)
df_drought_class.set_index('Month',inplace=True)
labels=df_drought_class
df_drought_forcing
sns.heatmap(df_drought_forcing, annot=labels, linewidths=.5, 
            ax=ax,fmt = '',cbar=True,vmin=-2,vmax=0,
            cbar_kws=dict(ticks=[-1.9,-1.5,-1.2,-0.7,-0.5,0]))
ax.set_facecolor('whitesmoke')
ax.invert_yaxis()
ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr',
                    'May','Jun','Jul',
                    'Aug','Sep','Oct',
                    'Nov','Dec'],rotation=0)
ax.set_xticklabels(['USGS','NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
ax.set_ylabel('')
ax.set_title(drought_title_CA2)