import pandas as pd

untrimmed_df = pd.read_csv('results_3387.csv', usecols=[1, 2, 4])
untrimmed_df[['DGP_1', 'DGP_2', 'DGP_3', 'DGP_4', 'ill_G1', 'ill_G2', 'PMV_1', 'PMV_2', 'PMV_3', 'PMV_4', 'Q_Heat_kW',
              'Q_Cool_kW', 'QSOLTR_kW']] = untrimmed_df['state'].str.strip('[]').str.split(pat=',', expand=True, n=12)
untrimmed_df[['altitude', 'azimuth', 'dir', 'diff', 'Occupancy']] = untrimmed_df['observation'].str.strip(
    '[]').str.split(pat=',', expand=True, n=4)
untrimmed_df['P_VC'] = 0
untrimmed_df['P_TC'] = 0
untrimmed_df['P_En'] = 0
untrimmed_df['intgain'] = 0

import itertools

combinations = []
combs = ['0', '1', '2', '3']
for subset in itertools.product(combs, repeat=3):
    combinations.append(subset)
actions = {}
dict = {}
for i, combination in zip(range(0, 64, 1), combinations):
    actions[combination[0] + combination[1] + combination[2]] = i
    dict[i] = combination[0] + ',' + combination[1] + ',' + combination[2]

untrimmed_df['action'] = untrimmed_df['action'].apply(int)
untrimmed_df['action'] = untrimmed_df['action'].map(dict)
untrimmed_df[['T', 'M', 'D']] = untrimmed_df['action'].str.split(pat=',', expand=True, n=2)
untrimmed_df['Time'] = pd.Series(range(1, 8760))
trimmed_df = untrimmed_df[
    ['Time', 'T', 'M', 'D', 'P_VC', 'P_TC', 'P_En', 'intgain', 'DGP_1', 'DGP_2', 'DGP_3', 'DGP_4', 'ill_G1', 'ill_G2']]
trimmed_df.to_csv('comfort_ctrl_3387.csv', index=False)
