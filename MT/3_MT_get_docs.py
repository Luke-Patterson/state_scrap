import urllib.request
import urllib.parse
import requests
import bs4 as bs
import re
import pandas as pd
import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from dateutil import parser
import pyautogui
import time
import glob
pyautogui.FAILSAFE = False
# start chrome webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path= \
    "C:/Users/lpatterson/AnacondaProjects/Tribal_Master/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)
driver.maximize_window()

def MT_ordering(sos_id,impaq_id,doc_dir,rei,url,new):
    # open URL
    driver.get('https://www.mtsosfilings.gov/mtsos-master/')
    time.sleep(1)
    # navigate to search page
    driver.find_element_by_xpath('//*[@class="guest-primary-row3-partA-itemA1-' +
        'menuA1 appMenu appMenuItem appMenuDepth0 appPlainLink noUrlStackPush' +
        ' appNotReadOnly appIndex0"]').click()
    time.sleep(1)
    # type in id number
    driver.find_element_by_id('QueryString').send_keys(str(sos_id))
    time.sleep(1)
    # click search
    driver.find_element_by_xpath('//*[contains(@class,"appSubmitButton")]').click()
    time.sleep(5)
    # click on result
    driver.find_element_by_xpath('//a[contains(@class,"appItemSearchResult")]').click()
    # zoom out
    time.sleep(3)
    # scroll down
    for _ in range(11):
        driver.find_element_by_tag_name('body').send_keys(Keys.DOWN)
    if new == False:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/documentation/Existing Retailers/' +
            row.REI + '_SoS_Website_Record.png')
    if new == True:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/documentation/New Retailers/IMPAQID_' +
            str(row.IMPAQ_ID) + '_SoS_Website_Record.png')
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'MT/MT_FDA_matches.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/New Retailers'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/Existing Retailers'

# merge REI into data set
rei_df = pd.read_excel("C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/Public Retail Data_original.xlsx")
rei_df['IMPAQ_ID'] = rei_df.index
rei_df = rei_df[['REI','IMPAQ_ID']]
df = df.merge(rei_df, how='left', on='IMPAQ_ID')

# no documents to get for free, so just saving screenshots
for i,row in df.loc[:,:].iterrows():
    print(i)
    if row.ori_flg == 'New Retailer':
        MT_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI,row.URL, new=True)
    else:
        MT_ordering(row.SoS_record, row.IMPAQ_ID,old_dir, row.REI,row.URL, new=False)
print(time.process_time())
