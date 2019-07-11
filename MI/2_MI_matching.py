# take scraping output and determine matches
import os, sys
from os.path import dirname, join, abspath
abs_path = "C:/Users/lpatterson/AnacondaProjects/Tribal_Master"
sys.path.insert(0, abs_path)
import functions.matching_functions as mf
import functions.cleaning_functions as cf
import pandas as pd
import numpy as np
import usaddress as usa

# load data
sos_df = pd.read_csv(abs_path + '/step_4_work/MI/MI_candidate_records.csv')
sos_df = sos_df.append(pd.read_csv(abs_path + '/step_4_work/MI/MI_candidate_records_pt2.csv'),
    ignore_index=True, sort=False)
fda_df = pd.read_csv(abs_path + "/step_3_work/output/full_retailer_list.csv")
fda_df = fda_df.loc[[i in sos_df.IMPAQ_ID.values for i in fda_df.IMPAQ_ID.values]]

# clean up some of the columns for sos_df
sos_df.columns = [i.replace(':','') for i in sos_df.columns]
sos_df['Entity Name']=''
name_cols=[i for i in sos_df.columns if 'The name of the' in i]
for i in name_cols:
    sos_df[i]=sos_df[i].fillna('')
    sos_df.loc[sos_df['Entity Name']=='','Entity Name'] = \
        sos_df.loc[sos_df['Entity Name']=='', i]
# address parser for agent address
def try_tag(str):
    try:
        s=usa.tag(str)
        if 'StreetNamePostType' in s[0]:
            s[0]['StreetNamePostType'] = mf.normalizeStreetSuffixes(
                s[0]['StreetNamePostType'].lower())
        return(s[0])
    except:
        return('')

# clean and standardize data set for comparison with FDA
first=True
for i, fda_row in fda_df.iterrows():
    temp_sos = sos_df.loc[sos_df['IMPAQ_ID'] == fda_row['IMPAQ_ID']]
    print(i)
    if temp_sos.empty == False:
        out = mf.name_match_scoring(fda_row, temp_sos, fda_colname='DBA Name_update',
            sos_colname = 'Entity Name', id_var='IMPAQ_ID')
        if out.name_score.max() > .99:
            match = temp_sos.loc[out.name_score.idxmax(),:]
            fda_df.loc[i,'SoS_record'] = match['Identification Number']
            fda_df.loc[i,'URL'] = match['URL']
            fda_df.loc[i,'entity'] = match['Entity Name']
            fda_df.loc[i,'agent_name'] = match['Resident Agent Name']
            fda_df.loc[i,'doc_date'] = match['Most Recent Annual Report']
            fda_df.loc[i,'agent_address'] = match['Street Address']
            fda_df.loc[i,'agent_city'] = match['City1']
            fda_df.loc[i,'agent_state'] = match['State1']
            fda_df.loc[i,'agent_zip'] = match['Zip Code1']
fda_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'MI/MI_FDA_matches.csv',index=False)
