# merge files for zip code 98951 to see what's available

import pandas as pd
import re
import os
import numpy as np
from datetime import datetime
# import master functions
import matching_functions as mf
pd.options.mode.chained_assignment = 'raise'

start=datetime.now()

WA_processdir='R:/FDA/2732 - FDA Tribal Tobacco Retailers/Technical/Task 2 - ' + \
            'Retailers List/Business Data/processed_data/WA'
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

fda_df = pd.read_excel(FDA_dir + '/input/Public retail data_original.xlsx')
fda_df= fda_df.loc[fda_df['Zip']==98951,:]

biz_df = pd.read_pickle(WA_processdir + "/BusinessInfo_short.pkl")
corp_df = pd.read_pickle(WA_processdir + "/Corporations_short.pkl")
doc_df = pd.read_pickle(WA_processdir + "/DocumentTypes_short.pkl")
gov_df = pd.read_pickle(WA_processdir + "/GoverningPersons_short.pkl")

# test if biz name is same in biz_df and corp_df

merge_df = biz_df.merge(corp_df, left_on='id', right_on='UBI')
