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
fda_df=pd.read_csv
