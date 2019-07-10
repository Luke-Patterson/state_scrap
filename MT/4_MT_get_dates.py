# get latest doc dates for montana entities
import pandas as pd
import numpy as np

# load data
cand_df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/MT/MT_candidate_records.csv')
fda_df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/MT/MT_FDA_matches.csv')

# need to recreate Business Identifier column, which didn't process properly
cand_df['ID_idx_start']=cand_df['Record Name on Website'].str.find('(')
cand_df['ID_idx_end']=cand_df['Record Name on Website'].str.find(')')
cand_df['Business Identifier']=cand_df.apply(lambda x:
    x['Record Name on Website'][x['ID_idx_start']+1:x['ID_idx_end']],axis=1)
# just need identifier and last ar date
cand_df=cand_df[['Business Identifier', 'Last AR Filed Date']]

# merge with FDA_df
cand_df = cand_df.merge(fda_df[['SoS_record','IMPAQ_ID']],how='inner',left_on='Business Identifier',
    right_on='SoS_record')

# create columns for document df in line with other states
cand_df['doc_date']=cand_df['Last AR Filed Date'].apply(lambda x: x[-4:] if pd.isna(x)==False else np.nan)
cand_df['doc_type']='Website_Record'
# reorder and filter columns
cand_df=cand_df[['IMPAQ_ID','doc_type','doc_date']].sort_values('IMPAQ_ID')
cand_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/MT/MT_docs_found.csv',index=False)
