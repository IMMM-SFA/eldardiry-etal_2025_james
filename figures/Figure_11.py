
# %% Importing Packages
import os
import pandas as pd
import matplotlib.pyplot as plt
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


# %% Select Events
basin_id=11266500
df_best_metric_forcing=pd.read_csv(r'\Outputs\CAMELS_Best_Ensemble_Run_Metrics_Forcing.csv', sep = ',')
df_best_metric_forcing=df_best_metric_forcing[df_best_metric_forcing['Basin_ID']==basin_id]

# %% Read Ensemble-Parameters
forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']
metrics_list=['KGE','MAE','VARB',
         'AVB','fallVB','winVB','sprVB','sumVB',
         'q10VB','q90VB']

df_ensemble_par=pd.read_csv(wd+r'\Outputs\1500_ensemble_parameters.csv', sep = ',')
df_parameters_best_ensemble=pd.DataFrame(columns=forcing_list)

k=-1
for i in range(len(forcing_list)):
    forcing=forcing_list[i]
    for j in range(len(metrics_list)):
        metric=metrics_list[j]
        col=metric+'_'+forcing
        best_par=df_best_metric_forcing[col].values[0]
        
        k=k+1
        df_parameters_best_ensemble.loc[k,'Forcing']=forcing
        df_parameters_best_ensemble.loc[k,'Metric']=metric
        df_parameters_best_ensemble.loc[k,'fff']=df_ensemble_par[df_ensemble_par['Num']==best_par].fff.values[0]
        df_parameters_best_ensemble.loc[k,'theta_sat']=df_ensemble_par[df_ensemble_par['Num']==best_par]['theta_sat.1'].values[0]
        df_parameters_best_ensemble.loc[k,'d_max']=df_ensemble_par[df_ensemble_par['Num']==best_par].d_max.values[0]
        df_parameters_best_ensemble.loc[k,'theta_ini']=df_ensemble_par[df_ensemble_par['Num']==best_par].theta_ini.values[0]
        

  
# %% Heatmap for Sensitive Parameters
par_list=['fff','theta_sat','d_max','theta_ini']
par_list_names=['Surface Runoff Parameter ($\it {fff}$)','Soil Water (Ѳ$_{sat}$)','Dry Surface Layer Parameter (d$_{max}$)','Soil Evaporation Parameter (Ѳ$_{ini}$)']

fig, axes = plt.subplots(2,2,figsize=(15,15))
plt.rcParams.update({'font.size': 26}) 
axes=axes.ravel()
cmap = 'cividis'

for ii in range(4): 
    ax=axes[ii]
    
    df_par=df_parameters_best_ensemble[['Forcing','Metric',par_list[ii]]]
    tmp=df_par[par_list[ii]].values.reshape(5,10,order='C')
    df_plot=pd.DataFrame(tmp,columns=metrics_list,index=forcing_list).T
    sns.heatmap(df_plot, linewidths=.5, 
                ax=ax,cbar=True,cmap=cmap,annot=True)
                
    ax.set_facecolor('whitesmoke')
    ax.invert_yaxis()
    ax.set_xticks([0.5,1.5,2.5,3.5,4.5])
    if ii>1:
        ax.set_xticklabels(['NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'],rotation=45)
    else:
        ax.set_xticklabels('')
    
    if ii==0 or ii==2:    
        ax.set_yticklabels(['KGE','MAE', 'VARB','AVB','Fall VB', 'Winter VB', 'Spring VB', 'Summer VB',
                            'Q10 VB', 'Q90 VB'])
    else:
        ax.set_yticklabels('')
    
    ax.set_ylabel('')
    ax.set_title(par_list_names[ii])
    