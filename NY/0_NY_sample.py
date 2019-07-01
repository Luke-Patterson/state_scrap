# create a sample of NY data from one zip for matching
import pandas as pd

# load NY biz data
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/' +
    'state bulk sos data/NY_Active_Corporations.csv', dtype=str)

samp_df = df.loc[df['DOS Process Zip']=='13655']
samp_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/' +
    'state bulk sos data/NY_Active_Corporations_short.csv')
