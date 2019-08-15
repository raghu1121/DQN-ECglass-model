import pandas as pd

name='Potsdam'
df =pd.read_csv('inputs/'+name+'_DGP')

df['ID'] = df['ID'].str.replace("__","_")
df['ID'] = df['ID'].drop_duplicates()
df= df[['ID','DGP']]
df.to_csv('outputs/'+name+'_dgp.csv',sep=' ',header=None,index=None)
print(df)