
# load and clean bulk data from WA
import pandas as pd
import os
import glob
import re
import numpy as np
import codecs
import csv
import sys
csv.field_size_limit(100000000)
from itertools import islice
import cleaning_functions as cf

WA_rawdir='R:/FDA/2732 - FDA Tribal Tobacco Retailers/Technical/Task 2 - ' + \
            'Retailers List/Business Data/raw_data/WA'
WA_processdir='R:/FDA/2732 - FDA Tribal Tobacco Retailers/Technical/Task 2 - ' + \
            'Retailers List/Business Data/processed_data/WA'
FDA_dir='C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
fda_df= pd.read_excel(FDA_dir + '/input/Public retail data_original.xlsx')
fda_df= fda_df.loc[fda_df['State']=='WA',:]
fda_df.reset_index(inplace=True)


# load WA tab-delimited data sets
os.chdir(WA_rawdir)
rawfiles=[]
for file in glob.glob("*.txt"):
    rawfiles.append(file)

for k in rawfiles:
    # some inconsistencies with the tab delimited data, so we need to first process with csv
    file = open(k,'rt', encoding="utf8")
    reader = csv.reader(file, delimiter='\t', quotechar = None)
    csv_list = []

    for m,l in enumerate(reader):
        if  m % 100000 == 0:
            print(m)
        csv_list.append(l)
    # make dataframe with first row as column headers
    biz_df= pd.DataFrame(csv_list)
    biz_df.columns = biz_df.iloc[0]
    # assign column number as name if missing
    biz_df.columns = ['col'+str(i) if j is None else j for i,j in enumerate(biz_df.columns)]
    biz_df=biz_df[1:]
    biz_df.reset_index(inplace=True, drop=True)
    # save as pickle
    biz_df.to_pickle(WA_processdir + '/' + k[:-4] + '.pkl')

# additional Biz info file processing
biz_df = pd.read_pickle(WA_processdir + "/BusinessInfo.pkl")

# clean Business Info file
biz_df.reset_index(inplace=True, drop=True)
biz_df = cf.cleaning_sos(biz_df, id='UBI', bizname='BusinessName',
    paddress1='Physical Address Line 1', paddress2='Physical Address Line 2',
    pcity='Physical City', pstate='Physical State', pzip='Physical Zip5',
    maddress1='Mailing Address Line 1', maddress2='Mailing Address Line 2',
    mcity='Mailing  City', mstate='Mailing State', mzip='Mailing Zip5',
    email='Email Address', phone='Phone Number')
biz_df.to_pickle(WA_processdir + '/BusinessInfo.pkl')

# create short versions for a single zip code 98951 for ease of programming
biz_df = biz_df.loc[biz_df['pzip']==98951]
UBIs = biz_df['id'].unique()
biz_df.to_pickle(WA_processdir + '/BusinessInfo_short.pkl')

for i in ['GoverningPersons', 'DocumentTypes', 'Corporations']:
    temp_df = pd.read_pickle(WA_processdir + '/' + i + '.pkl')
    temp_df = temp_df.loc[temp_df['UBI'].isin(UBIs)]
    temp_df.to_pickle(WA_processdir + '/' + i + "_short.pkl")
