# select candidate records to match with FDA list for MT
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
    'MT/MT_candidate_records.csv')
# drop a trademark picked up
sos_df=sos_df.loc[sos_df['type']!='Service mark'].dropna(axis=1,how='all')
# can't match to assumed business names, which do not list entities. Can only match
# with the corporations identified from the assumed business name entries
sos_df=sos_df.loc[sos_df['type']!='Assumed Business Name'].dropna(axis=1,how='all')
# need to recreate Business Identifier column, which didn't process properly
sos_df['ID_idx_start']=sos_df['Record Name on Website'].str.find('(')
sos_df['ID_idx_end']=sos_df['Record Name on Website'].str.find(')')
sos_df['Business Identifier']=sos_df.apply(lambda x:
        x['Record Name on Website'][x['ID_idx_start']+1:x['ID_idx_end']],axis=1)

# load FDA data
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df = pd.read_csv(FDA_dir + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='MT',:]

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
    temp_sos = sos_df.loc[sos_df['IMPAQ_ID'] == fda_row['IMPAQ_ID']]
    if temp_sos.empty == False:
        out = mf.name_match_scoring(fda_row, temp_sos, fda_colname='DBA Name_update',
            sos_colname = 'Record Name on Website', id_var='IMPAQ_ID')
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
            fda_df.loc[i,'SoS_record'] = str(match['Business Identifier'])
            fda_df.loc[i,'entity'] = match['Record Name on Website']
            fda_df.loc[i,'agent_name'] = match['Name']
            address = try_tag(match['Postal Address'])
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
            fda_df.loc[i,'URL'] = match['URL']
fda_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'MT/MT_FDA_matches.csv',index=False)
