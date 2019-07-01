# ------------------------------------------------------------------------------
# WA_matching
# ------------------------------------------------------------------------------
# determine matches between establishments from FDA
# and business records from state SoS websites

# housekeeping
# import dependencies
import pandas as pd
import re
import os
import numpy as np
from datetime import datetime
import functions.matching_functions as mf
# import master functions
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master')

import functions.matching_functions as mf
pd.options.mode.chained_assignment = 'raise'

start=datetime.now()

WA_rawdir='R:/FDA/2732 - FDA Tribal Tobacco Retailers/Technical/Task 2 - ' + \
            'Retailers List/Business Data/raw_data/WA'
WA_processdir='R:/FDA/2732 - FDA Tribal Tobacco Retailers/Technical/Task 2 - ' + \
            'Retailers List/Business Data/processed_data/WA'
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

fda_df = pd.read_csv(FDA_dir + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='WA',:]
# pick the biz short zip for now
#fda_df= fda_df.loc[fda_df['Zip']==98951,:]
fda_df.reset_index(inplace=True, drop=True)

biz_df = pd.read_pickle(WA_processdir + "/BusinessInfo.pkl")
agent_df = pd.read_pickle(WA_processdir + "/GoverningPersons.pkl")
print("read in all data")
agent_df = agent_df.drop(['index','col9','col10','col11','col12'],axis=1)
biz_df = biz_df.merge(agent_df, how='left', left_on='id', right_on='UBI')
# function to get possible matches from biz_df
matches = []
matches2 = []
matches3 = []
fda_df['match_id'] = ''
print('starting matching process')
for i in range(len(fda_df)):
    print(i)
    # filter SoS data to the same zip or town as the fda row to improve runtime
    fda_row = fda_df.iloc[i,:]
    sos_df = biz_df.loc[(biz_df['pzip'] == fda_row['Zip_update']) |
        (biz_df['pcity'] == fda_row['City_update']),:]
    sos_df.reset_index(inplace = True, drop = True)
    # run through each matching algorithm
    out = mf.name_match_scoring(fda_row, sos_df, fda_colname='DBA Name_update')
    out = out.merge(mf.address_match_scoring(fda_row, sos_df, update=True),
        left_index=True, right_index=True, on='id')
    out = sos_df.merge(out, left_index=True, right_index=True, on='id')
    match = mf.match_selection(out, 'basic addr')
    match2= mf.matc h_selection(out, 'basic name',name_lvl=.99)
    matches.append([fda_row, match])
    matches2.append([fda_row, match2])
    if match.empty == False:
        if isinstance(match,pd.DataFrame):
            match = match.iloc[0,:]
        fda_df.loc[i,'SoS_record'] = match.id
        fda_df.loc[i,'entity'] = match.bizname
        fda_df.loc[i,'agent_name'] = ' '.join([str(match['First Name']),
            str(match['Middle Name']), str(match['Last Name'])])
        fda_df.loc[i,'agent_address'] = match.Address
        fda_df.loc[i,'agent_city'] = match.City
        fda_df.loc[i,'agent_state'] = match.State
        fda_df.loc[i,'agent_zip'] = match.Zip
    elif match2.empty == False:
        if isinstance(match2,pd.DataFrame):
            match2 = match2.iloc[0,:]
        fda_df.loc[i,'SoS_record'] = match2.id
        fda_df.loc[i,'entity'] = match2.bizname
        fda_df.loc[i,'agent_name'] = ' '.join([str(match2['First Name']),
            str(match2['Middle Name']), str(match2['Last Name'])])
        fda_df.loc[i,'agent_address'] = match2.Address
        fda_df.loc[i,'agent_city'] = match2.City
        fda_df.loc[i,'agent_state'] = match2.State
        fda_df.loc[i,'agent_zip'] = match2.Zip
fda_df.to_csv(FDA_dir+"/step_4_work/WA/WA_ownership_results.csv")

# print('writing log file')
# mf.display_results(matches, 'addr_log')

# print runtime
print(datetime.now()-start)
