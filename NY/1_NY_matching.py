# clean up NY data and get ready for matching
import pandas as pd
# import master functions
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master')
import functions.matching_functions as mf
import functions.cleaning_functions as cf
import datetime

# load NY biz data
sos_df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/' +
    'state bulk sos data/NY_Active_Corporations.csv')
sos_df['id']=sos_df.index
sos_df = cf.cleaning_sos(sos_df, id='id', bizname='Current Entity Name',
    paddress1='Location Address 1', paddress2='Location Address 2',
    pcity='Location City', pstate='Location State', pzip='Location Zip',
    maddress1='DOS Process Address 1', maddress2='DOS Process Address 2',
    mcity='DOS Process City', mstate='DOS Process State', mzip='DOS Process Zip',
    email=None, phone=None)

# fill in physical address if missing
for i in ['address1','address2','city','state','zip']:
    sos_df.loc[sos_df['p'+i].isna(),'p'+i] = sos_df.loc[sos_df['p'+i].isna(),'m'+i]

# create sample from fda
fda_df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/'
    + '/step_3_work/output/full_retailer_list.csv')
fda_df = fda_df.loc[fda_df['State']=='NY',:]
fda_df = fda_df.reset_index(drop=True)
matches=[]
matches2=[]
# match records
for i in range(len(fda_df)):
    print(i)
    # filter SoS data to the same zip or town as the fda row to improve runtime
    fda_row = fda_df.iloc[i,:]
    temp_sos = sos_df.loc[(sos_df['pzip'] == fda_row['Zip_update']) |
        (sos_df['pcity'] == fda_row['City_update']),:]
    temp_sos.reset_index(inplace = True, drop = True)
    # run through each matching algorithm
    out = mf.name_match_scoring(fda_row, temp_sos, fda_colname='DBA Name_update',
        sos_colname='bizname')
    out = out.merge(mf.address_match_scoring(fda_row, temp_sos, update=True),
        left_index=True, right_index=True, on='id')
    out = temp_sos.merge(out, left_index=True, right_index=True, on='id')
    match = mf.match_selection(out, 'basic addr')
    match2= mf.match_selection(out, 'basic name',name_lvl=.99)
    matches.append([fda_row, match])
    matches2.append([fda_row, match2])
    if match.empty == False:
        if isinstance(match,pd.DataFrame):
            match = match.iloc[0,:]
        fda_df.loc[i,'SoS_record'] = match.id
        fda_df.loc[i,'entity'] = match.bizname
        fda_df.loc[i,'agent_name'] = match['Registered Agent Name']
        fda_df.loc[i,'agent_address'] = match['Registered Agent Address 1']
        fda_df.loc[i,'agent_city'] = match['Registered Agent City']
        fda_df.loc[i,'agent_state'] = match['Registered Agent State']
        fda_df.loc[i,'agent_zip'] = match['Registered Agent Zip']
    elif match2.empty == False:
        if isinstance(match2,pd.DataFrame):
            match2 = match2.iloc[0,:]
        fda_df.loc[i,'SoS_record'] = match2.id
        fda_df.loc[i,'entity'] = match2.bizname
        fda_df.loc[i,'agent_name'] = match2['Registered Agent Name']
        fda_df.loc[i,'agent_address'] = match2['Registered Agent Address 1']
        fda_df.loc[i,'agent_city'] = match2['Registered Agent City']
        fda_df.loc[i,'agent_state'] = match2['Registered Agent State']
        fda_df.loc[i,'agent_zip'] = match2['Registered Agent Zip']
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df.to_csv(FDA_dir+"/step_4_work/NY/NY_ownership_results.csv")

# print('writing log file')
mf.display_results(matches, 'addr_log_NY')
mf.display_results(matches2, 'name_log_NY')

# print runtime
print(datetime.now()-start)
