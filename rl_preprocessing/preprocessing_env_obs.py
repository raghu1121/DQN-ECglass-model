import pandas as pd
import glob
import itertools
import pytz
from pysolar import solar
import numpy as np
import json
import math
import datetime
import swifter

input = 'Input_preprocessing/'
output = 'Output_preprocessing/'
climates = {
    1: {'name': 'mannheim', 'code_name': 'DEU_01_TRY2010_Orig', 'lat': 49.52, 'long': 8.55, 'elevation': 100,
        'tz': pytz.timezone('Europe/Berlin'),
        'timezone': 'Europe/Berlin'},
    2: {'name': 'potsdam', 'code_name': 'DEU_04_TRY2010_Orig', 'lat': 52.38, 'long': 13.07, 'elevation': 81,
        'tz': pytz.timezone('Europe/Berlin'),
        'timezone': 'Europe/Berlin'},
    3: {'name': 'rostock', 'code_name': 'DEU_02_TRY2010_Orig', 'lat': 54.18, 'long': 12.08, 'elevation': 4,
        'tz': pytz.timezone('Europe/Berlin'),
        'timezone': 'Europe/Berlin'}
}

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
    # print(i,combination[0]+combination[1]+combination[2])


def getAltitude(time):
    return solar.get_altitude_fast(climates[climate]['lat'], climates[climate]['long'], time)


def getAzimuth(time):
    return solar.get_azimuth(climates[climate]['lat'], climates[climate]['long'], time, climates[climate]['elevation'])


# tz.localize(pd.Timestamp(time))
for climate in climates:
    dfs = []
    EC_files = sorted(glob.glob(input+'DGPe_EC/' + climates[climate]['code_name'] + '/*'))
    ill_files = sorted(glob.glob(input+'Eh_illFiles_EC/' + climates[climate]['code_name'] + '/*'))
    trnsys_files = sorted(glob.glob(input+'Trnsys_EC/' + climates[climate]['code_name'] + '/*'))
    weaDF = pd.read_csv(input+'weather/' + climates[climate]['name'] + '.wea', skiprows=6, usecols=[3, 4],
                        names=['dir', 'diff'], delimiter=' ')
    for EC_file, ill_file, trnsys_file in zip(EC_files, ill_files, trnsys_files):
        state = EC_file.split('.')[0].split('_')[-1]
        states = list(state)
        EC_df = pd.read_csv(EC_file, header=None, names=['m', 'd', 'h', 'DGP_1', 'DGP_2', 'DGP_3', 'DGP_4'],
                            engine='python')
        EC_df = EC_df.round({'DGP_1': 2, 'DGP_2': 2, 'DGP_3': 2, 'DGP_4': 2})
        ill_df = pd.read_csv(ill_file, header=None, usecols=[i for i in range(3, 15)],
                             names=['g' + str(x) for x in range(4, 16)])
        ill_df['T'] = states[0]
        ill_df['M'] = states[1]
        ill_df['D'] = states[2]
        g1_df = ill_df[['g4', 'g5', 'g6', 'g13', 'g14', 'g15']]
        g2_df = ill_df[['g7', 'g8', 'g9', 'g10', 'g11', 'g12']]
        ill_df['ill_G1'] = g1_df.mean(axis=1)
        ill_df['ill_G2'] = g2_df.mean(axis=1)
        ill_df = ill_df[['T', 'M', 'D', 'ill_G1', 'ill_G2']]
        ill_df = ill_df.astype({'ill_G1': int, 'ill_G2': int})
        trnsys_df = pd.read_csv(trnsys_file, header=None, usecols=[0, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17],
                                names=['Time', 'Q_Heat_kW', 'Q_Cool_kW', 'QSOLTR_kW', 'Q_INTGain_kW', 'PMV_1', 'PMV_2',
                                       'PMV_3', 'PMV_4', 'Occupancy', 'DimmFraction_G1', 'DimmFraction_G2'])
        trnsys_df = trnsys_df.round(
            {'Q_Heat_kW': 3, 'Q_Cool_kW': 3, 'QSOLTR_kW': 3, 'Q_INTGain_kW': 3, 'PMV_1': 2, 'PMV_2': 2, 'PMV_3': 2,
             'PMV_4': 2, 'DimmFraction_G1': 2, 'DimmFraction_G2': 2})
        list_dfs = [EC_df, ill_df, trnsys_df, weaDF]
        df = pd.concat(list_dfs, axis=1)
        df['action'] = actions[state]
        df = df.apply(pd.to_numeric)
        # print (df)
        dfs.append(df)

    comb_dfs = pd.concat(dfs)
    hour = comb_dfs['h'].apply(int)
    minute = ((comb_dfs['h'] - hour) * 60).apply(int)
    month = comb_dfs['m'].apply(int)

    comb_dfs['time'] = pd.to_datetime(('2015' + '-' + comb_dfs['m'].apply(str) + '-' + comb_dfs['d'].apply(
        str) + ' ' + hour.apply(str) + ':' + minute.apply(str)), format='%Y-%m-%d %H:%M:%S', errors='ignore')
    # comb_dfs['time'] = pd.to_datetime(comb_dfs['time'], format='%Y-%m-%d %H:%M:%S')
    comb_dfs['time'] = comb_dfs['time'].dt.tz_localize('GMT').dt.tz_convert(climates[climate]['timezone'])
    # print(comb_dfs['time'])
    comb_dfs['altitude'] = comb_dfs['time'].swifter.set_dask_scheduler('processes').set_npartitions(
        32).allow_dask_on_strings(
        enable=True).apply(getAltitude)
    comb_dfs = comb_dfs.reset_index()
    comb_dfs['azimuth'] = comb_dfs['time'].swifter.set_dask_scheduler('processes').set_npartitions(
        32).allow_dask_on_strings(
        enable=True).apply(getAzimuth)

    comb_dfs = comb_dfs.round({'altitude': 2, 'azimuth': 2})
    comb_dfs.to_csv(output+'env_comb_' + climates[climate]['name'] + '.csv', index=False)
    env_dfs = comb_dfs[
        ['altitude', 'azimuth', 'dir', 'diff', 'Occupancy', 'DGP_1', 'DGP_2', 'DGP_3', 'DGP_4', 'ill_G1', 'ill_G2',
         'PMV_1', 'PMV_2', 'PMV_3', 'PMV_4', 'Q_Heat_kW', 'Q_Cool_kW', 'QSOLTR_kW', 'Q_INTGain_kW', 'DimmFraction_G1',
         'DimmFraction_G2', 'action']]
    env_dfs.to_csv(output+'env_' + climates[climate]['name'] + '.csv', index=False)
    obs_dfs = comb_dfs[['altitude', 'azimuth', 'dir', 'diff', 'Occupancy']]
    obs_dfs = obs_dfs.drop_duplicates()
    obs_dfs.to_csv(output+'observations_' + climates[climate]['name'] + '.csv', index=False)
    # print(comb_dfs['Time'])
