import pandas as pd
import glob
import itertools
import pytz
from pysolar import solar
import json
import math
import datetime

# Mannheim data
station = 'mannheim'
lat = 49.52
long = 8.55
elevation = 100
tz = pytz.timezone('Europe/Berlin')

# combining all the states
combinations = []
combs = ['0', '1', '2', '3']
for subset in itertools.product(combs, repeat=3):
    combinations.append(subset)

# dictionary of actions, total 64 (0 to 63)
actions = {}
dict = {}
for i, combination in zip(range(0, 64, 1), combinations):
    actions[combination[0] + combination[1] + combination[2]] = i
    dict[i] = combination[0] + combination[1] + combination[2]
    # print(i, combination[0] + combination[1] + combination[2])

with open('action_mapping.json', 'w') as f:
    json.dump(dict, f)
    
# combining all the DGP files
files = glob.glob('EC/DGP_Ev_EC_*')
dfs = []
# adding weather data
weaDF = pd.read_csv('weather/mannheim.wea', skiprows=6, usecols=[3, 4], names=['dir', 'diff'], delimiter=' ')
for file in files:
    state = file.split('_')[3].split('.')[0]
    df = pd.read_csv(file, header=None, names=['m', 'd', 'h', 'v1', 'v2', 'v3', 'v4'])
    df['action'] = actions[state]
    list_dfs = [df, weaDF]
    df = pd.concat(list_dfs, axis=1)
    df['Time']=pd.Series(range(1,8761))
    # print(state,type(state))
    states=list(state)
    df['T']=states[0]
    df['M'] = states[1]
    df['D']=states[2]
    # print(df)
    dfs.append(df)

comb_dfs = pd.concat(dfs)
comb_dfs = comb_dfs.sort_values(by=['m', 'd', 'h', 'action'])

# filter values with dir or diff > 50
comb_dfs = comb_dfs[(comb_dfs['diff'] > 50) | (comb_dfs['dir'] > 50)]

hour = comb_dfs['h'].apply(int)
minute = ((comb_dfs['h'] - hour) * 60).apply(int)
time = pd.to_datetime(
    (comb_dfs['m'].apply(str) + ' ' + comb_dfs['d'].apply(str) + ' ' + hour.apply(str) + ':' + minute.apply(str)),
    format='%m %d %H:%M', errors='ignore')
comb_dfs['time'] = time

altitude = []
azimuth = []
for time1 in comb_dfs['time'].values.tolist():
    temp_tm = pd.Timestamp(time1)
    # time2 = pd.Timestamp(time1, tz=tz)
    time2 = tz.localize(temp_tm)
    alt = solar.GetAltitudeFast(lat, long, time2)
    try:
        azi = solar.GetAzimuthFast(lat, long, time2)
    except ValueError:
        pass
        # print(time2, alt)
    altitude.append(alt)
    azimuth.append(azi)

comb_dfs['altitude'] = altitude
comb_dfs['azimuth'] = azimuth
comb_dfs = comb_dfs.round({'altitude': 2, 'azimuth': 2,'v1':4, 'v2':4, 'v3':4, 'v4':4})
comb_dfs=comb_dfs.astype({'dir':int,'diff':int,'action':int})
comb_filtered_dfs = comb_dfs[['altitude', 'azimuth', 'dir', 'diff', 'v1', 'v2', 'v3', 'v4', 'action','Time','T','M','D']]
comb_filtered_dfs=comb_filtered_dfs.apply(pd.to_numeric)
# comb_dfs.to_csv('observations.csv', index=False)
# print(comb_filtered_dfs)
filename='rewards_baseline'
results_df=pd.read_csv(filename+'.csv')

# results_df[['altitude', 'azimuth', 'dir', 'diff']]=pd.DataFrame(results_df['self.observation'].str.strip('[]').str.split().values.tolist())
results_df[['v1', 'v2', 'v3', 'v4']]=pd.DataFrame(results_df['self.state'].str.strip('[]').str.split(',').values.tolist())
# results_df[['v1', 'v2', 'v3', 'v4']]=pd.DataFrame(results_df['self.state'].str.strip('[]').str.split(',').str.strip('\'\'').values.tolist())
results_df[['altitude', 'azimuth', 'dir', 'diff']]=pd.DataFrame(results_df['self.observation'].str.strip('[]').str.split(',').values.tolist())

results_df=results_df[['altitude', 'azimuth', 'dir', 'diff', 'v1', 'v2', 'v3', 'v4', 'action']]
results_df=results_df.apply(pd.to_numeric)
results_df=results_df.astype({'dir':int,'diff':int,'action':int})
results_df = results_df.round({'altitude': 2, 'azimuth': 2,'v1':4, 'v2':4, 'v3':4, 'v4':4})
# print(results_df)

# result=pd.concat([comb_filtered_dfs,results_df],axis=1,join='inner')
result=results_df.merge(comb_filtered_dfs)
# result.to_csv('result.csv')
result=result.rename(index=str,columns={'v1':'DGP_1', 'v2':'DGP_2', 'v3':'DGP_3', 'v4':'DGP_4'})
result['P_VC']=0
result['P_TC']=0
result['P_En']=0
result['intgain']=0
result=result[['Time','T','M','D','P_VC','P_TC','P_En','intgain','DGP_1', 'DGP_2', 'DGP_3', 'DGP_4']]
result=result.sort_values(by='Time')
# result.to_csv('result.csv',index=False)
# # print(result)
#result=pd.read_csv('result.csv')
ctrl=pd.read_csv('EC_CtrlRad1.txt')
ill_dfs=[]
illfiles = glob.glob('illfiles/ill_EC_*')
for file in illfiles:
    state = file.split('_')[2].split('.')[0]
    ill_df = pd.read_csv(file, header=None, names=['g'+str(x) for x in range(1,16)])
    ill_df['Time']=pd.Series(range(1,8761))
    states = list(state)
    ill_df['T'] = states[0]
    ill_df['M'] = states[1]
    ill_df['D']=states[2]
    g1_df=ill_df[['g4','g5','g6','g13','g14','g15']]
    g2_df = ill_df[['g7', 'g8','g9','g10','g11','g12']]
    ill_df['ill_G1']=g1_df.mean(axis=1)
    ill_df['ill_G2'] = g2_df.mean(axis=1)
    ill_df=ill_df[['Time','T','M','D','ill_G1','ill_G2']]
    ill_df=ill_df.apply(pd.to_numeric)
    ill_dfs.append(ill_df)
    # print(ill_df.merge(result))
    # print(ill_df)
ill_comb_dfs = pd.concat(ill_dfs)
result=result.apply(pd.to_numeric)
result=result.merge(ill_comb_dfs)
ctrl=ctrl.apply(pd.to_numeric)

ctrl.loc[ctrl.Time.isin(result.Time),ctrl.columns]=result[result.columns].values
ctrl=ctrl.astype({'Time':int,'T':int,'M':int,'D':int,'P_VC':int,'P_TC':int,'P_En':int,'intgain':int,' ill_G1':int,' ill_G2':int})
ctrl = ctrl.round({'DGP_1':2, ' DGP_2':2, ' DGP_3':2, ' DGP_4':2})
print(ctrl)
ctrl.to_csv(filename+'_ctrl.csv',index=False)
# print(result)