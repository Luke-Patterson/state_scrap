# clean up scraping output for match comparison
#def CA_execute(path):
path = "C:/Users/lpatterson/AnacondaProjects/Tribal_Master"
import pandas as pd
import numpy as np

# read in raw output from the scraper
df = pd.read_excel(path + '/step_4_work/CA/CA_results.xlsx', encoding='utf-8')

# parse name from filing number
# bunch of random spaces thrown in. split by spaces, then extract filing number
df['Filing Number'] = df['Filing Number/Name'].str.split(pat=" ").str[12].str[:-1]

# filing name is trickier, spaces found in the names themselves
df['Entity Name'] = df['Filing Number/Name'].str.strip().str.split(pat=" ").str[13:]
df['Entity Name'] = df['Entity Name'].apply(lambda x: ' '.join(x))

# strip out spaces in other columns
for i in ['Operation Status', 'Agent', 'Agent Address', 'Store Address']:
    df[i] = df[i].str.strip()

# Agent address is actually entity address, store address is mail address
df['Entity Mailing Address'] = df['Store Address']
df['Entity Store Address'] = df['Agent Address']

# parse out agent address, name
# remove blank agents
blanks = df['Agent'].str.find('*')
blanks2 = df['Agent'].str.find('Agent AddressAgent City, State, Zip')
blanks3 = df['Agent'].str.find('View details for agent entity number')
df['Agent'] = np.where(((blanks!=-1) & (blanks2!=-1)) | (blanks3!=-1),'',df['Agent'])

# parse out agent name
df['Agent Name'] = df['Agent'].apply(lambda x: x[0:x.find('Agent Address')-2])

# parse agent address
df['Agent Address'] = df['Agent'].apply(lambda x:
    x[x.find('Agent Address')+13:].replace('Agent City, State, Zip',' '))

# parse entity addresses
# remove text in blank addresses
df['Entity Store Address'] = np.where(
    df['Entity Store Address'].str.find(
        'Entity Address\n        *\nEntity City, State, Zip'
    )!=-1,
    '', df['Entity Store Address']
)

df['Entity Mailing Address'] = np.where(
    df['Entity Mailing Address'].str.find(
        'Entity Mailing Address\n        *\nEntity Mailing City, State, Zip'
    )!=-1,
    '', df['Entity Mailing Address']
)

# remove extraneous text from entity addresses
df['Entity Store Address'] = df['Entity Store Address'].str.replace(
    'Entity Address\n', ''
).str.strip().str.replace('\nEntity City, State, Zip','').str.replace(
    '\n     ', ''
).str.replace('  ',' ')

df['Entity Mailing Address'] = df['Entity Mailing Address'].str.replace(
    'Entity Mailing Address\n', ''
).str.strip().str.replace('\nEntity Mailing City, State, Zip','').str.replace(
    '\n     ', ''
).str.replace('  ',' ')

# Use store address if available, otherwise use mailing address for "master address"
df['Entity Address'] = df['Entity Store Address']
df.loc[df['Entity Address'] == '', 'Entity Address'] = df.loc[df['Entity Address'] == '', 'Entity Mailing Address']

# drop messy columns and reorder some stuff
df = df[['IMPAQ_ID', 'Filing Number', 'Entity Name', 'Entity Mailing Address',
    'Entity Store Address', 'Entity Address', 'Agent Name', 'Agent Address', 'Operation Status']]

df.to_csv(path + '/step_4_work/CA/CA_results_clean.csv', index=False)
