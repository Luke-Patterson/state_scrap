# build a parser that predicts matches well
import pandas as pd
import os, sys
import numpy as np
import string
from wordfreq import word_frequency
sys.path.insert(0, 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master')

import functions.matching_functions as mf

sos_df=pd.read_excel('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'OK/OK_results.xlsx')
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df = pd.read_csv(FDA_dir + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='OK',:]

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
    'OK/OK_FDA_matches.csv',index=False)

# create match flag in df for QA'ing
# df=df.merge(match_df.loc[match_df['Name']!='No Match',['IMPAQ_ID','Filing Number','match']], on=['IMPAQ_ID','Filing Number'], how='left')
# df=df.merge(match_df.loc[match_df['Name']=='No Match',['IMPAQ_ID','match']], on=['IMPAQ_ID'], how='left')
# df['match_x'].update(df['match_y'])
# df['match']=df['match_x']
# df['match'].fillna('Not a Match',inplace=True)
# df.drop(columns=['match_x','match_y'], inplace=True)
# df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
#     'OK/scrapping_output_match_flag.csv',index=False)
