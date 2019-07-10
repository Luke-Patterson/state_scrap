# select candidate records to match with FDA list for NM
# build a parser that predicts matches well
import pandas as pd
import os, sys
import numpy as np
import string
import usaddress as usa
from wordfreq import word_frequency
sys.path.insert(0, 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master')
import functions.matching_functions as mf
# laod SOS data
sos_df=pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'NM/NM_candidate_records.csv')
sos_df.columns=[i.replace(':','') for i in sos_df.columns]
# load FDA data
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df = pd.read_csv(FDA_dir + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='NM',:]

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

# run for all stores
for i,fda_row in fda_df.iterrows():
    print(i)
    temp_sos = sos_df.loc[sos_df['IMPAQ_ID'] == fda_row['IMPAQ_ID']]
    if temp_sos.empty == False:
        out = mf.name_match_scoring(fda_row, temp_sos, fda_colname='DBA Name_update',
            sos_colname = 'Entity Name', id_var='IMPAQ_ID')
        # turns out address fails to predict anything
        # # try out all the different address columns for a match by address
        # addr_out = mf.address_match_scoring(fda_row, temp_sos, update=True,
        #     addr_split=False,full_addr='Agent Address',id_var='IMPAQ_ID')
        # addr_dict={}
        # for j in addr_cols:
        #     addr_dict[j] = mf.address_match_scoring(fda_row, temp_sos, update=True,
        #         addr_split=False,full_addr=j,id_var='IMPAQ_ID')
        #take max values
        # for j in addr_cols:
        #     addr_out = pd.concat([addr_out, addr_dict[j]]).max(level=0)
        # out = out.merge(addr_out, left_index=True, right_index=True, on='IMPAQ_ID')
        name_match = mf.match_selection(out, 'basic name',name_lvl=.99)
        # addr_match = mf.match_selection(out, 'basic addr',addrnum_lvl=.01,
        #     strname_lvl=.01, strtype_lvl=.01, zip_lvl=.01)

        # if addr_match.empty == False:
        #     match = temp_sos.loc[addr_match.index,:]
        if name_match.empty == False:
            match = temp_sos.loc[name_match.index,:]
            # if more than one tied, take the active record
            if any(match['Status'].apply(lambda x: 'Active' in 'x')):
                match = match.loc[('Active' in match['Status']),:]
                name_match = name_match.loc[match.index,:]
            match = match.loc[name_match.name_score.idxmax(),:]
            # handling for corporation record
            fda_df.loc[i,'SoS_record'] = str(match['Business ID#'])
            fda_df.loc[i,'entity'] = match['Entity Name']
            fda_df.loc[i,'agent_name'] = match['Name']
            address = try_tag(match['Physical Address'])
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
                try:
                    fda_df.loc[i,'agent_city'] = address['PlaceName']
                except:
                    print('error parsing city from agent address')
                    pass
                try:
                    fda_df.loc[i,'agent_state'] = address['StateName']
                except:
                    print('error parsing state from agent address')
                    pass
                try:
                    fda_df.loc[i,'agent_zip'] = str(address['ZipCode'])[0:5]
                except:
                    print('error parsing state from agent address')
                    pass
fda_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'NM/NM_FDA_matches.csv',index=False)
