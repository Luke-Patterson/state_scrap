# scraper to query AZ SOS website for possible matches for each retailer
# 2nd part:retriving data for candidate records
import urllib.request
import urllib.parse
import bs4 as bs
import re
import pandas as pd
import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui
import time
import string
import math
from ast import literal_eval
from wordfreq import word_frequency

def AZ_record_scrap(file_num):
    url='https://ecorp.azcc.gov/BusinessSearch/BusinessInfo?entityNumber='+file_num
    driver.get(url)
    result=pd.Series()
    result['Entity Name'] = driver.find_elements_by_xpath('//*[@class="'+
        'col-xs-12 col-sm-3"]')[0].text
    result['Operation Status'] = driver.find_elements_by_xpath('//*[@class="'+
        'col-xs-12 col-sm-3"]')[3].text
    result['Agent Name'] = driver.find_elements_by_xpath('//*[@class="'+
        'col-xs-12 col-sm-3"]')[17].text
    result['Agent Address'] = driver.find_elements_by_xpath('//*[@class="'+
        'col-xs-12 col-sm-3"]')[20].text
    result['Store Address'] = driver.find_elements_by_xpath('//*[@class="'+
        'col-xs-12 col-sm-3"]')[28].text
    return(result)

path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/'
# load csv of records
df = pd.read_csv(path + 'step_4_work/AZ/candidate_records_pt1.csv')
# convert strings to actual list objects
def _leval(str):
    try:
        str = literal_eval(str)
        return(str)
    except:
        return(None)
df['records'] = df['records'].apply(_leval)

# create a df of all the possible candidates and their original records
result_df = pd.DataFrame(
    columns=['Filing Number', 'Entity Name', 'Operation Status', 'Agent Name',
    'Agent Address', 'Store Address', 'IMPAQ_ID'])
for i,row in df.iterrows():
    if row['records'] != None:
        for j in row['records']:
            result_df = result_df.append(pd.Series({'IMPAQ_ID':row['IMPAQ_ID'],
                'Filing Number':j}), ignore_index = True)
# start chrome webdriver
chrome_options = Options()
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)
driver.maximize_window()

# pull up the record for each candidate
for i,row in result_df.iterrows():
    if i % 10 == 0:
        print(i)
    result=AZ_record_scrap(row['Filing Number'])
    result_df.loc[i,:].update(result)
result_df.to_csv(path + 'step_4_work/AZ/candidates_records_filled.csv', index=False)
