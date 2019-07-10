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

def NM_ordering(sos_id,impaq_id,doc_dir,rei,new,first):
    # open URL
    driver.get('https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch/Index')
    time.sleep(1)
    # log in if first time
    if first == True:
        driver.find_element_by_id('lblHome').click()
        driver.find_element_by_id('txtUsername').send_keys('mmiller4')
        driver.find_element_by_id('txtPassword').send_keys('CDL533032')
        driver.find_element_by_id('btnSave').click()
        time.sleep(1)
        # click ok
        driver.find_element_by_xpath('//*[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only button"]').click()
        driver.get('https://portal.sos.state.nm.us/BFS/online/CorporationBusinessSearch/Index')
    # enter the biz id
    driver.find_element_by_id('txtBusinessId').send_keys(str(int(sos_id)))
    # click search
    driver.find_element_by_xpath('//*[@name="btnSearch"]').click()
    time.sleep(1)
    # click on result
    driver.find_element_by_xpath('//tr[@class="bgwhite"]/td[1]/a').click()

    # scroll down
    for _ in range(4):
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
    'NM/NM_FDA_matches.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/New Retailers'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/Existing Retailers'

# merge REI into data set
rei_df = pd.read_excel("C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/Public Retail Data_original.xlsx")
rei_df['IMPAQ_ID'] = rei_df.index
rei_df = rei_df[['REI','IMPAQ_ID']]
df = df.merge(rei_df, how='left', on='IMPAQ_ID')
# no documents to get for free, so just saving screenshots
first=True
for i,row in df.loc[:,:].iterrows():
    print(i)
    if row.ori_flg == 'New Retailer':
        NM_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI, new=True,first=first)
    else:
        NM_ordering(row.SoS_record, row.IMPAQ_ID,old_dir, row.REI, new=False,first=first)
    if first==True:
        first=False
