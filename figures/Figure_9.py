# %% Importing Packages
import os
import pandas as pd
import matplotlib.pyplot as plt

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
ii=[0,4]   # choose indices for CA
start_dry_mon=4
end_dry_mon=start_dry_mon+2

df_selected_events=df_selected_events.iloc[ii].reset_index(drop=True)

flood_title='%d Flood Event at CAMELS %s (%s)'%(df_selected_events.Start_Year[0],df_selected_events.CAMELS[0],df_selected_events.State[0])
drought_title1='%d Drought Event (Jan-Mar) at CAMELS %s (%s)'%(df_selected_events.Start_Year[1],df_selected_events.CAMELS[1],df_selected_events.State[1])
drought_title2='%d Drought Event (Jul-Sep) at CAMELS %s (%s)'%(df_selected_events.Start_Year[1],df_selected_events.CAMELS[1],df_selected_events.State[1])

# %% Load Metrics

Nevents=len(df_selected_events)

df_best_kge_daymet=pd.read_csv(wd+'\\Scripts\\CLM_CAMELS_Daymet_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_livneh=pd.read_csv(wd+'\\Scripts\\CLM_CAMELS_Livneh_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_nldas=pd.read_csv(wd+'\\Scripts\\CLM_CAMELS_NLDAS_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_wrf=pd.read_csv(wd+'\\Scripts\\CLM_CAMELS_WRF_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_prism=pd.read_csv(wd+'\\Scripts\\CLM_CAMELS_PRISM_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge=pd.concat([df_best_kge_nldas,df_best_kge_wrf['Ensemble_Run'],
                       df_best_kge_livneh['Ensemble_Run'],df_best_kge_prism['Ensemble_Run'],
                       df_best_kge_daymet['Ensemble_Run']],axis=1)

df_best_kge.columns=['Basin_ID','NLDAS2','WRF','Livneh','PRISM','Daymet']

df_best_kge_selected=df_best_kge[(df_best_kge['Basin_ID']=='08175000')
                                 | (df_best_kge['Basin_ID']=='11266500')].reset_index(drop=True)


forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']

df_runoff_TVB_3MON=pd.DataFrame([])   # Jan-Mar

df_TVB_best_3MON=pd.DataFrame([])

df_runoff_TVB=pd.DataFrame([])      # flood event
df_runoff_TVB_best=pd.DataFrame([])      # flood event
df_runoff_PFB=pd.DataFrame([])      # flood event
for i in range(Nevents):
    for j in range(len(forcing_list)):
        forcing=forcing_list[j]
        
        basinID=df_selected_events.loc[i]['CAMELS']
        state=df_selected_events.loc[i]['State']
        event=df_selected_events.loc[i]['Event']
        start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
        end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])
        
        print(i,'reading CLM runoff (%s) for %s event in %s state'%(forcing,event,state))
        os.chdir(wd+'\\Outputs\\Selected_Events_CA_TX\\Runoff\\')
        
        df_event=pd.read_csv('%s_Runoff_%s_%s_%s_%s_%s.csv'%(forcing,event,state,basinID,start_date,end_date))
        best_par=df_best_kge[df_best_kge['Basin_ID']==basinID][forcing].values[0]

        if event=='Drought':
            df_event_monthly=df_event.groupby(['Year','Month']).sum().reset_index().drop(['Day'],axis=1)
            qobs_mon=df_event_monthly.Qobs
            
            
            df_event_3mon=df_event_monthly[(df_event_monthly['Month']>=start_dry_mon) & (df_event_monthly['Month']<=end_dry_mon)]
            
            df_event_3mon=df_event_3mon.groupby(['Year']).sum().reset_index().drop(['Month'],axis=1)
            qobs_3mon=df_event_3mon.Qobs
            
            df1=df_event_3mon.iloc[:, 2:]
            df2=df_event_3mon.iloc[:, 0:2]
            df_TVB_tmp=df1.sub(df2['Qobs'], axis=0)
            df1_best=df1[['Qsim_%03d'%best_par]]
            df_TVB_tmp_best=df_TVB_tmp[['Qsim_%03d'%best_par]]
            
            #### 3-MON
            df_TVB=pd.DataFrame(df_TVB_tmp.iloc[0].values,columns=['TVB'])
            df_TVB['State']=state
            df_TVB['Event']=event
            df_TVB['Forcing']=forcing
            df_TVB['Run']=df_TVB_tmp.columns
            df_TVB=df_TVB.reset_index(drop=True)
            df_runoff_TVB_3MON=pd.concat([df_runoff_TVB_3MON,df_TVB],axis=0).reset_index(drop=True)
            
            df_TVB_best=pd.DataFrame(df_TVB_tmp_best.iloc[0].values,columns=['TVB'])
            df_TVB_best['State']=state
            df_TVB_best['Event']=event
            df_TVB_best['Forcing']=forcing
            df_TVB_best=df_TVB_best.reset_index(drop=True)
            df_TVB_best_3MON=pd.concat([df_TVB_best_3MON,df_TVB_best],axis=0).reset_index(drop=True)
            
            
           
        else:
            qobs_tot=df_event.iloc[:, 3].sum(axis=0)
            qobs_max=df_event.iloc[:, 3].max(axis=0)
            
            df_runoff=df_event.iloc[:, 4:]
            df_TVB_tmp=pd.DataFrame(df_runoff.sum(axis=0)-qobs_tot, columns=['TVB'])
            df_TVB_tmp['State']=state
            df_TVB_tmp['Event']=event
            df_TVB_tmp['Forcing']=forcing
            df_TVB_tmp['Run']=df_TVB_tmp.index
            df_TVB_tmp=df_TVB_tmp.reset_index(drop=True)
            df_runoff_TVB=pd.concat([df_runoff_TVB,df_TVB_tmp],axis=0).reset_index(drop=True)
            
            df_TVB_best=pd.DataFrame(df_runoff[['Qsim_%03d'%best_par]].sum(axis=0)-qobs_tot, columns=['TVB'])
            df_TVB_best['State']=state
            df_TVB_best['Event']=event
            df_TVB_best['Forcing']=forcing
            df_TVB_best=df_TVB_best.reset_index(drop=True)
            df_runoff_TVB_best=pd.concat([df_runoff_TVB_best,df_TVB_best],axis=0).reset_index(drop=True)
            
            
            
            
            df_PFB_tmp=pd.DataFrame(df_runoff.max(axis=0)-qobs_max, columns=['PFB'])
            df_PFB_tmp['Forcing']=forcing
            df_PFB_tmp['State']=state
            df_PFB_tmp['Event']=event
            df_PFB_tmp['Forcing']=forcing
            df_PFB_tmp=df_PFB_tmp.reset_index(drop=True)
            df_runoff_PFB=pd.concat([df_runoff_PFB,df_PFB_tmp],axis=0).reset_index(drop=True)
# %% Evaluation Metrics for forcing variables

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


forcing_dir=r'\Datasets\CAMELS_CLM_Forcing\Selected_Events_CA_TX'
df_selected_events=pd.read_csv(wd+'\\Scripts\\NCEI_Selected_Events_CA_TX.csv',dtype={'CAMELS': str})
df_selected_events=df_selected_events.iloc[ii].reset_index(drop=True)
Nevents=len(df_selected_events)

forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']
col_names=['year','month','day','hour','pressure','T','wind',
           'SH','precip','SW','LW']

df_forcing_all=pd.DataFrame([])

df_forcing_all_3MON=pd.DataFrame([])

for i in range(Nevents):
    basinID=df_selected_events.loc[i]['CAMELS']
    state=df_selected_events.loc[i]['State']
    event=df_selected_events.loc[i]['Event']
    start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
    end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])
    
    
    for j in range(len(forcing_list)):
        forcing=forcing_list[j]
        print(i,'reading CLM Forcing (%s) for %s event in %s state'%(forcing,event,state))
        os.chdir(wd+'\\Datasets\\CAMELS_CLM_Forcing\\Selected_Events_CA_TX\\')
        df_forcing_basin=pd.read_csv('basin_%s_%s'%(basinID,forcing),header=None,sep=' ')
        df_forcing_basin.columns=col_names
        
        if event=='Drought':
            df_forcing_event_3MON=df_forcing_basin[(df_forcing_basin['year']>=df_selected_events.loc[i]['Start_Year']) 
                                & (df_forcing_basin['year']<=df_selected_events.loc[i]['End_Year'])
                                & (df_forcing_basin['month']>=start_dry_mon)
                                & (df_forcing_basin['month']<=end_dry_mon)
                                & (df_forcing_basin['day']>=df_selected_events.loc[i]['Start_Day'])
                                & (df_forcing_basin['day']<=df_selected_events.loc[i]['End_Day'])]
        
           
            df_forcing_event_3MON['Forcing']=forcing
            df_forcing_event_3MON['State']=state
            df_forcing_event_3MON['Event']=event
            df_forcing_all_3MON=pd.concat([df_forcing_all_3MON,df_forcing_event_3MON])
            
            
           
        else:    
            df_forcing_event=df_forcing_basin[(df_forcing_basin['year']>=df_selected_events.loc[i]['Start_Year']) 
                                & (df_forcing_basin['year']<=df_selected_events.loc[i]['End_Year'])
                                & (df_forcing_basin['month']>=df_selected_events.loc[i]['Start_Month'])
                                & (df_forcing_basin['month']<=df_selected_events.loc[i]['End_Month'])
                                & (df_forcing_basin['day']>=df_selected_events.loc[i]['Start_Day'])
                                & (df_forcing_basin['day']<=df_selected_events.loc[i]['End_Day'])]
            df_forcing_event['Forcing']=forcing
            df_forcing_event['State']=state
            df_forcing_event['Event']=event
            df_forcing_all=pd.concat([df_forcing_all,df_forcing_event])

    
df_forcing_all_3MON=df_forcing_all_3MON.reset_index(drop=True)
df_forcing_all=df_forcing_all.reset_index(drop=True)

# %% ET

df_selected_events=pd.read_csv(wd+'\\Scripts\\NCEI_Selected_Events_CA_TX.csv',dtype={'CAMELS': str})
df_selected_events=df_selected_events.iloc[ii].reset_index(drop=True)
Nevents=len(df_selected_events)

# ET for best ensemble run
df_best_kge_daymet=pd.read_csv('\\CLM_CAMELS_Daymet_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_livneh=pd.read_csv('\\CLM_CAMELS_Livneh_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_nldas=pd.read_csv('\\CLM_CAMELS_NLDAS_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_wrf=pd.read_csv('\\CLM_CAMELS_WRF_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge_prism=pd.read_csv('\\CLM_CAMELS_PRISM_Best_KGE_Index.csv',dtype={'Basin_ID': str})
df_best_kge=pd.concat([df_best_kge_nldas,df_best_kge_wrf['Ensemble_Run'],
                       df_best_kge_livneh['Ensemble_Run'],df_best_kge_prism['Ensemble_Run'],
                       df_best_kge_daymet['Ensemble_Run']],axis=1)

df_best_kge.columns=['Basin_ID','NLDAS2','WRF','Livneh','PRISM','Daymet']
forcing_list=['NLDAS2','WRF','Livneh','PRISM','Daymet']

df_ET_all=pd.DataFrame([])
df_ET_all_best=pd.DataFrame([])
df_ET_all_3MON=pd.DataFrame([])
df_ET_all_3MON_best=pd.DataFrame([])

for i in range(Nevents):
    for j in range(len(forcing_list)):
        forcing=forcing_list[j]
        basinID=df_selected_events.loc[i]['CAMELS']
        state=df_selected_events.loc[i]['State']
        event=df_selected_events.loc[i]['Event']
        start_date= '%04d%02d%02d'%(df_selected_events.loc[i]['Start_Year'],df_selected_events.loc[i]['Start_Month'],df_selected_events.loc[i]['Start_Day'])
        end_date= '%04d%02d%02d'%(df_selected_events.loc[i]['End_Year'],df_selected_events.loc[i]['End_Month'],df_selected_events.loc[i]['End_Day'])
        
        print(i,'reading ET (%s) for %s event in %s state'%(forcing,event,state))
    
        os.chdir('\\Outputs\\Selected_Events_CA_TX\\ET\\')
        
        df_event=pd.read_csv('%s_ET_%s_%s_%s_%s_%s.csv'%(forcing,event,state,basinID,start_date,end_date))
        best_par=df_best_kge[df_best_kge['Basin_ID']==basinID][forcing].values[0]

        if event=='Drought':
            
            ##### 3-MON
            df_ET_event_JM=df_event[(df_event['Month']<=start_dry_mon) & 
                                    (df_event['Month']<=end_dry_mon)]
            
            df_et=df_ET_event_JM.iloc[:, 3:]
            df_ET_tmp=pd.DataFrame(df_et.sum(axis=0), columns=['ET'])
                    
            df_ET_tmp['Forcing']=forcing
            df_ET_tmp['State']=state
            df_ET_tmp['Event']=event
            df_ET_tmp['Run']=df_et.columns
            df_ET_all_3MON=pd.concat([df_ET_all_3MON,df_ET_tmp])
            
            df_ET_tmp=pd.DataFrame(df_et[['ETsim_%03d'%best_par]].sum(axis=0), columns=['ET'])
            df_ET_tmp['State']=state
            df_ET_tmp['Event']=event
            df_ET_tmp['Forcing']=forcing
            df_ET_tmp=df_ET_tmp.reset_index(drop=True)
            df_ET_all_3MON_best=pd.concat([df_ET_all_3MON_best,df_ET_tmp],axis=0).reset_index(drop=True)
            
            
            #### Jul-Sep
            df_ET_event_JS=df_event[(df_event['Month']<=7) & 
                                    (df_event['Month']<=9)]
            df_et=df_ET_event_JS.iloc[:, 3:]
            df_ET_tmp=pd.DataFrame(df_et.sum(axis=0), columns=['ET'])
                                
          
            
        else:
            df_et=df_event.iloc[:, 3:]
            df_ET_tmp=pd.DataFrame(df_et.sum(axis=0), columns=['ET'])
            df_ET_tmp['State']=state
            df_ET_tmp['Event']=event
            df_ET_tmp['Forcing']=forcing
            df_ET_tmp['Run']=df_ET_tmp.index
            
            df_ET_tmp=df_ET_tmp.reset_index(drop=True)
            df_ET_all=pd.concat([df_ET_all,df_ET_tmp],axis=0).reset_index(drop=True)
            
            # df_ET_all_best=df_ET_all.iloc['ETsim_%03d'%best_par]
            
            df_ET_tmp=pd.DataFrame(df_et[['ETsim_%03d'%best_par]].sum(axis=0), columns=['ET'])
            df_ET_tmp['State']=state
            df_ET_tmp['Event']=event
            df_ET_tmp['Forcing']=forcing
            df_ET_tmp=df_ET_tmp.reset_index(drop=True)
            df_ET_all_best=pd.concat([df_ET_all_best,df_ET_tmp],axis=0).reset_index(drop=True)
            

df_ET_all_3MON['ET']=df_ET_all_3MON['ET']*3600*24        
df_ET_all_3MON_best['ET']=df_ET_all_3MON_best['ET']*3600*24        
df_ET_all['ET']=df_ET_all['ET']*3600*24        
df_ET_all_best['ET']=df_ET_all_best['ET']*3600*24        
    
  
# %% Aggregate TVB and Precipitation

# flood event
df_precip=df_forcing_all[['year','month','day','hour','precip','Forcing']] 
df_daily_precip=df_precip.groupby(['Forcing'])['precip'].sum().reset_index()
df_daily_precip['precip']=df_daily_precip['precip']*3600  # convert mm/sec to mm/hour then the summation to mm/day

df_tmp=df_runoff_TVB[['Forcing','TVB']]
df_tmp['TVB']=df_tmp['TVB'].abs()
df_runoff_TVBmin=df_tmp.groupby(['Forcing'])['TVB'].min().reset_index()

# drought event
df_precip=df_forcing_all_3MON[['year','month','day','hour','precip','Forcing']] 
df_daily_precip_3MON=df_precip.groupby(['Forcing'])['precip'].sum().reset_index()
df_daily_precip_3MON['precip']=df_daily_precip_3MON['precip']*3600  # convert mm/sec to mm/hour then the summation to mm/day

df_tmp=df_runoff_TVB_3MON[['Forcing','TVB']]
df_tmp['TVB']=df_tmp['TVB'].abs()
df_runoff_TVBmin_3MON=df_tmp.groupby(['Forcing'])['TVB'].min().reset_index()

df_precip=df_forcing_all_3MON[['year','month','day','hour','precip','Forcing']] 
df_daily_precip_3MON=df_precip.groupby(['Forcing'])['precip'].sum().reset_index()
df_daily_precip_3MON['precip']=df_daily_precip_3MON['precip']*3600  # convert mm/sec to mm/hour then the summation to mm/day

df_tmp=df_runoff_TVB_3MON[['Forcing','TVB']]
df_tmp['TVB']=df_tmp['TVB'].abs()
df_runoff_TVBmin_3MON=df_tmp.groupby(['Forcing'])['TVB'].min().reset_index()

# %% Plot of Runoff-ET-Precip
############################# subplots
# fig, axes = plt.subplots(2,2,figsize=(15,15),width_ratios=[2, 1])
fig = plt.figure(figsize=(15, 15))
spec = fig.add_gridspec(2,1)
plt.rcParams.update({'font.size': 24}) 

ax= fig.add_subplot(spec[0, :])

runoff_color='steelblue'
et_color='indianred'
best_color='silver'
prec_color='blue'


y1=df_runoff_TVB[df_runoff_TVB['Forcing']=='NLDAS2'].TVB.to_numpy()
y2=df_runoff_TVB[df_runoff_TVB['Forcing']=='WRF'].TVB.to_numpy()
y3=df_runoff_TVB[df_runoff_TVB['Forcing']=='Livneh'].TVB.to_numpy()
y4=df_runoff_TVB[df_runoff_TVB['Forcing']=='PRISM'].TVB.to_numpy()
y5=df_runoff_TVB[df_runoff_TVB['Forcing']=='Daymet'].TVB.to_numpy()
medians = df_runoff_TVB.groupby('Forcing',sort=False)['TVB'].median()
quartile1=df_runoff_TVB.groupby('Forcing',sort=False)['TVB'].quantile(0.25) 
quartile3=df_runoff_TVB.groupby('Forcing',sort=False)['TVB'].quantile(0.75)

data_to_plot = [y1, y2, y3, y4,y5]
xpos = [0.75,2.75,4.75,6.75,8.75]
vp1=ax.violinplot(data_to_plot,positions=xpos,
                  showextrema=True,showmedians=False)

for pc in vp1['bodies']:
    pc.set_facecolor(runoff_color)
    pc.set_edgecolor('black')
    pc.set_alpha(1)
    # pc.set_linewidth(3)

for partname in ('cbars', 'cmins', 'cmaxes'):
    vp = vp1[partname]
    vp.set_edgecolor("black")
    vp.set_linewidth(1)
    
# add median value as a point
ax.scatter(xpos, medians, marker='o', color='white', s=60, zorder=3)
# Add boxplot-like vertical lines to show the first and third quartile
ax.vlines(xpos, quartile1, quartile3, color='k', linestyle='-', lw=6)

# TVB for best KGE run
y = df_runoff_TVB_best.TVB.values
x=xpos
ax.plot(x, y, 'X', markersize=20,alpha=0.9,color=best_color)    


# Axes properties 
ax.set_xticks([1,3,5,7,9])
# ax.set_xticklabels(['NLDAS2', 'TGW', 'Livneh', 'PRISM', 'Daymet'])
ax.set_ylabel('TVB (m3/sec)', color = runoff_color)
ax.tick_params(axis ='y', labelcolor = runoff_color)
ax.spines['left'].set_color(runoff_color)
ax.spines['left'].set_linewidth(5)
# ax.set_ylim([-1500,2000])
ax.set_xlim([-0.0,9.75])
ax.set_title(flood_title)
ax.hlines(y=0.0,xmin=-1,xmax=10, linewidth=2, linestyle='--',color='grey')
ax.set_facecolor('whitesmoke')

######################### Right y-axis
ax=ax.twinx()

y1=df_ET_all[df_ET_all['Forcing']=='NLDAS2'].ET.to_numpy()
y2=df_ET_all[df_ET_all['Forcing']=='WRF'].ET.to_numpy()
y3=df_ET_all[df_ET_all['Forcing']=='Livneh'].ET.to_numpy()
y4=df_ET_all[df_ET_all['Forcing']=='PRISM'].ET.to_numpy()
y5=df_ET_all[df_ET_all['Forcing']=='Daymet'].ET.to_numpy()
data_to_plot = [y1, y2, y3, y4,y5]
medians = df_ET_all.groupby('Forcing',sort=False)['ET'].median()
quartile1=df_ET_all.groupby('Forcing',sort=False)['ET'].quantile(0.25) 
quartile3=df_ET_all.groupby('Forcing',sort=False)['ET'].quantile(0.75)

xpos=[1.25,3.25,5.25,7.25,9.25]
vp2=ax.violinplot(data_to_plot,positions=xpos)

for pc in vp2['bodies']:
    pc.set_facecolor(et_color)
    pc.set_edgecolor('black')
    pc.set_alpha(1)
    
for partname in ('cbars', 'cmins', 'cmaxes'):
    vp = vp2[partname]
    vp.set_edgecolor("black")
    vp.set_linewidth(1)    

# add median value as a point
ax.scatter(xpos, medians, marker='o', color='white', s=40, zorder=3)
# Add boxplot-like vertical lines to show the first and third quartile
ax.vlines(xpos, quartile1, quartile3, color='k', linestyle='-', lw=6)

## total event precipitation
y = [df_daily_precip.precip[2],df_daily_precip.precip[4],df_daily_precip.precip[1],df_daily_precip.precip[3],df_daily_precip.precip[0]]
x=xpos
ax.plot(x, y, 'o', markersize=20,alpha=1,color=prec_color)    

# ET for best KGE run
y = df_ET_all_best.ET.values
x=xpos
ax.plot(x, y, 'X', markersize=20,alpha=0.9,color=best_color)    


# Axes properties 
ax.set_xticks([1,3,5,7,9])
# ax.set_xticklabels(['NLDAS2', 'TGW', 'Livneh', 'PRISM', 'Daymet'])
ax.set_xticklabels('')
ax.set_ylabel('ET (mm)', color = et_color)
ax.tick_params(axis ='y', labelcolor = et_color)
ax.spines['right'].set_color(et_color)
ax.spines['right'].set_linewidth(5)
ax.spines['bottom'].set_linewidth(3)
ax.spines['top'].set_linewidth(3)



########################################################################################
# ax=axes[2]
ax= fig.add_subplot(spec[1, :])

y1=df_runoff_TVB_3MON[df_runoff_TVB_3MON['Forcing']=='NLDAS2'].TVB.to_numpy()
y2=df_runoff_TVB_3MON[df_runoff_TVB_3MON['Forcing']=='WRF'].TVB.to_numpy()
y3=df_runoff_TVB_3MON[df_runoff_TVB_3MON['Forcing']=='Livneh'].TVB.to_numpy()
y4=df_runoff_TVB_3MON[df_runoff_TVB_3MON['Forcing']=='PRISM'].TVB.to_numpy()
y5=df_runoff_TVB_3MON[df_runoff_TVB_3MON['Forcing']=='Daymet'].TVB.to_numpy()
data_to_plot = [y1, y2, y3, y4,y5]
medians = df_runoff_TVB_3MON.groupby('Forcing',sort=False)['TVB'].median()
quartile1=df_runoff_TVB_3MON.groupby('Forcing',sort=False)['TVB'].quantile(0.25) 
quartile3=df_runoff_TVB_3MON.groupby('Forcing',sort=False)['TVB'].quantile(0.75)


# xpos = [0.4,2.4,4.4,6.4,8.4]
xpos = [0.75,2.75,4.75,6.75,8.75]
vp1=ax.violinplot(data_to_plot,positions=xpos,widths=0.3)

for pc in vp1['bodies']:
    pc.set_facecolor(runoff_color)
    pc.set_edgecolor('black')
    pc.set_alpha(1)

for partname in ('cbars', 'cmins', 'cmaxes'):
    vp = vp1[partname]
    vp.set_edgecolor("black")
    vp.set_linewidth(1)


# add median value as a point
ax.scatter(xpos, medians, marker='o', color='white', s=60, zorder=3)
# Add boxplot-like vertical lines to show the first and third quartile
ax.vlines(xpos, quartile1, quartile3, color='k', linestyle='-', lw=6)

y = df_TVB_best_3MON.TVB.values
x=xpos
ax.plot(x, y, 'X', markersize=20,alpha=1,color=best_color)    

ax.set_ylabel('TVB (m3/sec)', color = runoff_color)
ax.tick_params(axis ='y', labelcolor = runoff_color)
ax.spines['left'].set_color(runoff_color)
ax.spines['left'].set_linewidth(5)
# ax.set_ylim([-1500,2000])
ax.set_title(drought_title1)
ax.hlines(y=0.0,xmin=-1,xmax=10, linewidth=2, linestyle='--',color='grey')
ax.set_facecolor('whitesmoke')
ax.set_xlim([-0.0,9.75])

ax=ax.twinx()

y1=df_ET_all_3MON[df_ET_all_3MON['Forcing']=='NLDAS2'].ET.to_numpy()
y2=df_ET_all_3MON[df_ET_all_3MON['Forcing']=='WRF'].ET.to_numpy()
y3=df_ET_all_3MON[df_ET_all_3MON['Forcing']=='Livneh'].ET.to_numpy()
y4=df_ET_all_3MON[df_ET_all_3MON['Forcing']=='PRISM'].ET.to_numpy()
y5=df_ET_all_3MON[df_ET_all_3MON['Forcing']=='Daymet'].ET.to_numpy()
data_to_plot = [y1, y2, y3, y4,y5]
medians = df_ET_all_3MON.groupby('Forcing',sort=False)['ET'].median()
quartile1=df_ET_all_3MON.groupby('Forcing',sort=False)['ET'].quantile(0.25) 
quartile3=df_ET_all_3MON.groupby('Forcing',sort=False)['ET'].quantile(0.75)



xpos=[1.25,3.25,5.25,7.25,9.25]
vp2=ax.violinplot(data_to_plot,positions=xpos,widths=0.3)

for pc in vp2['bodies']:
    pc.set_facecolor(et_color)
    pc.set_edgecolor('black')
    pc.set_alpha(1)

for partname in ('cbars', 'cmins', 'cmaxes'):
    vp = vp2[partname]
    vp.set_edgecolor("black")
    vp.set_linewidth(1)
 
# add median value as a point
ax.scatter(xpos, medians, marker='o', color='white', s=60, zorder=3)
# Add boxplot-like vertical lines to show the first and third quartile
ax.vlines(xpos, quartile1, quartile3, color='k', linestyle='-', lw=6)

    
y = [df_daily_precip_3MON.precip[2],df_daily_precip_3MON.precip[4],df_daily_precip_3MON.precip[1],df_daily_precip_3MON.precip[3],df_daily_precip_3MON.precip[0]]
x=xpos
ax.plot(x, y, 'o', markersize=20,alpha=1,color=prec_color)    

# ET for best KGE run
y = df_ET_all_3MON_best.ET.values
x=xpos
ax.plot(x, y, 'X', markersize=20,alpha=0.9,color=best_color)    


ax.set_xticklabels('')
ax.set_ylabel('ET (mm)', color = et_color)
ax.tick_params(axis ='y', labelcolor = et_color)
ax.spines['right'].set_color(et_color)
ax.spines['right'].set_linewidth(5)
ax.spines['bottom'].set_linewidth(3)
ax.spines['top'].set_linewidth(3)



ax.set_xticks([1,3,5,7,9])
ax.set_xticklabels(['NLDAS2', 'WRF-ERA5', 'Livneh', 'PRISM', 'Daymet'])
ax.set_ylabel('ET (mm)', color = et_color)


ax.legend(['ET','','','','','','',
           '','','','Total Precipitation','Best Ensemble Run'],
          loc='upper center', bbox_to_anchor=(1.2,0.5),
          fancybox=True, shadow=False, ncol=3,facecolor='whitesmoke')


