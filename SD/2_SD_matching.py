# select candidate records to match with FDA list for SD
# build a parser that predicts matches well
import pandas as pd
import os, sys
import numpy as np
import string
import usaddress
from wordfreq import word_frequency
sys.path.insert(0, 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master')

import functions.matching_functions as mf
# laod SOS data
sos_df=pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'SD/candidate_records.csv')
sos_df=sos_df.append(pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'SD/candidate_records.csv'), ignore_index=False,sort=False)
# note type of each record
sos_df['type'] = sos_df['Business ID'].str[0:2]
# load FDA data
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df = pd.read_csv(FDA_dir + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='SD',:]

# address parser for agent address
def try_tag(str):
    try:
        str=str.replace('\r',' ')
        str=str.replace('\n',' ')
        s=usa.tag(str)
        if 'StreetNamePostType' in s[0]:
            s[0]['StreetNamePostType'] = mf.normalizeStreetSuffixes(
                s[0]['StreetNamePostType'].lower())
        return(s[0])
    except:
        return('')

# run for all stores
for i,fda_row in fda_df.iterrows():
    temp_sos = sos_df.loc[sos_df['IMPAQ_ID'] == fda_row['IMPAQ_ID']]
    if temp_sos.empty == False:
        out = mf.name_match_scoring(fda_row, temp_sos, fda_colname='DBA Name_update',
            sos_colname = 'Name', id_var='IMPAQ_ID')
        import pdb; pdb.set_trace()
        if out.name_score.max() > .99:
            match = temp_sos.loc[out.name_score.idxmax(),:]
            if isinstance(match,pd.DataFrame):
                match = match.iloc[0,:]
            # handling for corporation record
            if match['type']=='DB':
                fda_df.loc[i,'SoS_record'] = str(match['Business ID'])
                fda_df.loc[i,'entity'] = match['Name']
                fda_df.loc[i,'agent_name'] = match['Agent Name']
                address = try_tag(str(match['Agent Address']))
                if address != '':
                    elems = ['AddressNumber', 'StreetNamePreType', 'StreetName',
                    'StreetNamePostType', 'OccupancyType', 'OccupancyIdentifier']
                    temp_elems=pd.Series(elems)
                    for n,j in enumerate(elems):
                        if j in address.keys():
                            temp_elems.iloc[n]=True
                        else:
                            temp_elems.iloc[n]=False
                    fda_df.loc[i,'agent_address'] = pd.Series(address).str.cat(
                        na_rep='', sep = ' ').strip().upper()
                    fda_df.loc[i,'agent_city'] = address['PlaceName']
                    fda_df.loc[i,'agent_state'] = address['StateName']
                    fda_df.loc[i,'agent_zip'] = str(address['ZipCode'])[0:5]
            # handling for DBA record - company
            if match['type']=='UB' and '- D' in match['Owner Name']:
                fda_df.loc[i,'SoS_record'] = str(match['Business ID'])
                trunc_idx = match['Owner Name'].str.find('- D')
                fda_df.loc[i,'entity'] = match['Owner Name'].str[0:trunc_idx].str.strip()
                fda_df.loc[i,'agent_name'] = 'Not found'
                fda_df.loc[i,'agent_address'] = 'Not found'
                fda_df.loc[i,'agent_city'] = 'Not found'
                fda_df.loc[i,'agent_state'] = 'Not found'
                fda_df.loc[i,'agent_zip'] = 'Not found'
            # handling for DBA record - individual
            if match['type']=='UB' and '- D' not in match['Owner Name']:
                fda_df.loc[i,'SoS_record'] = str(match['Business ID'])
                fda_df.loc[i,'entity'] = match['Owner Name'] + ' - Individually Owned'
                fda_df.loc[i,'agent_name'] = match['Owner Name']
                address = try_tag(match['Agent Address'])
                if address != '':
                    elems = ['AddressNumber', 'StreetNamePreType', 'StreetName',
                    'StreetNamePostType', 'OccupancyType', 'OccupancyIdentifier']
                    temp_elems=pd.Series(elems)
                    for n,j in enumerate(elems):
                        if j in address.keys():
                            temp_elems.iloc[n]=True
                        else:
                            temp_elems.iloc[n]=False
                    fda_df.loc[i,'agent_address'] = pd.Series(address).str.cat(
                        na_rep='', sep = ' ').strip().upper()
                    fda_df.loc[i,'agent_city'] = address['PlaceName']
                    fda_df.loc[i,'agent_state'] = address['StateName']
                    fda_df.loc[i,'agent_zip'] = str(address['ZipCode'])[0:5]
fda_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'SD/SD_FDA_matches.csv',index=False)
