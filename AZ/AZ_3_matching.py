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

sos_df = pd.read_csv(abs_path + '/step_4_work/AZ/candidates_records_filled.csv')
fda_df = pd.read_csv(abs_path + "/step_3_work/output/full_retailer_list.csv")
fda_df = fda_df.loc[[i in sos_df.IMPAQ_ID.values for i in fda_df.IMPAQ_ID.values]]
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
            fda_df.loc[i,'SoS_record'] = match['Filing Number']
            fda_df.loc[i,'entity'] = match['Entity Name']
            fda_df.loc[i,'agent_name'] = match['Agent Name']
            fda_df.loc[i,'store_address'] = match['Store Address']
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
            else:
                fda_df.loc[i,'agent_address'] = ''
                fda_df.loc[i,'agent_city'] = ''
                fda_df.loc[i,'agent_state'] = ''
                fda_df.loc[i,'agent_zip'] = ''
fda_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'AZ/AZ_FDA_matches.csv',index=False)
