# select candidate records to match with FDA list for SD
# build a parser that predicts matches well
import pandas as pd
import os, sys
import numpy as np
import string
from wordfreq import word_frequency
sys.path.insert(0, 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master')

import functions.matching_functions as mf

sos_df=pd.read_excel('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'SD/SD_results.xlsx')
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df = pd.read_csv(FDA_dir + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='SD',:]
import pdb; pdb.set_trace()
# run for all stores
for i,fda_row in fda_df.iterrows():
    temp_sos = sos_df.loc[sos_df['IMPAQ_ID'] == fda_row['IMPAQ_ID']]
    if temp_sos.empty == False:
        out = mf.name_match_scoring(fda_row, temp_sos, fda_colname='DBA Name_update',
            sos_colname = 'Name', id_var='IMPAQ_ID')
        if out.name_score.max() > .99:
            match = temp_sos.loc[out.name_score.idxmax(),:]
            fda_df.loc[i,'SoS_record'] = match['Filing Number'].astype('str')
            fda_df.loc[i,'entity'] = match['Name']
            fda_df.loc[i,'agent_name'] = match.Owner
            fda_df.loc[i,'agent_address'] = ''
            fda_df.loc[i,'agent_city'] = match['Owner City_x']
            fda_df.loc[i,'agent_state'] = match['Owner State_x']
            fda_df.loc[i,'agent_zip'] = ''

fda_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'SD/SD_FDA_matches.csv',index=False)
