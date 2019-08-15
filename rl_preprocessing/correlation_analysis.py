import pandas as pd
import seaborn as sbn
import matplotlib.pyplot as plt
climates = {
    1: {'name': 'mannheim', 'code_name': 'DEU_01_TRY2010_Orig'},
    2: {'name': 'potsdam', 'code_name': 'DEU_04_TRY2010_Orig'},
    3: {'name': 'rostock', 'code_name': 'DEU_02_TRY2010_Orig'}
}
for climate in climates:
    dfE=pd.read_csv('Output_preprocessing/env_'+climates[climate]['name']+'.csv',usecols=[4,5,6,7,8,21])
    dfS=pd.read_csv('Output_preprocessing_dgps/S_env_'+climates[climate]['name']+'.csv',usecols=[4,5,6,7,8,21])
    dfE = dfE[dfE['Occupancy']==1 ]
    dfE = dfE[dfE['action']==0]
    dfS = dfS[dfS['Occupancy'] == 1 ]
    dfS = dfS[ dfS['action'] == 0]
    print(climates[climate]['name'])
    print(dfE.size)
    # enhanced_glare=dfE[(dfE['DGP_1']>dfS['DGP_1']) & ((dfE['DGP_1'] >0.4) & (dfS['DGP_1'] < 0.4))]

    # print('enhanced_glare.size  '+enhanced_glare.size)
    # print(enhanced_glare.size/dfE.size)
    print(dfE.corrwith(dfS))

    ax=sbn.scatterplot(x=dfS['DGP_1'],y=dfE['DGP_1'])
    ax.set_xlim([0,1])
    plt.show()