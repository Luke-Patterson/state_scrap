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

# function for scraping necessary information for a single store
def NM_scrape(name, IMPAQ_ID, first):
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
    # click contains
    driver.find_element_by_id('rdContains').click()
    # type in name
    driver.find_element_by_xpath('//*[@id="txtBusinessName"]').send_keys(name)
    # click search
    driver.find_element_by_xpath('//*[@name="btnSearch"]').click()
    time.sleep(1)
    # see if any records were returned:
    if driver.find_elements_by_id('errorDialog') == []:
        # start a data frame to keep track of results
        result_df = pd.DataFrame()
        # find the rows in results.
        rows = driver.find_elements_by_xpath('//tr[@class="bgwhite"]|'+
            '//tr[@class="bgrowalt"]')
        row_count = 0
        # for each row, open the details tab
        for _ in range(len(rows)):
            time.sleep(2)
            i = driver.find_elements_by_xpath('//tr[@class="bgwhite"]|'+
                '//tr[@class="bgrowalt"]')[row_count]
            type=i.find_element_by_xpath('./td[3]').text
            if 'Partnership' not in type:
                i.find_element_by_xpath('./td[1]/a').click()
                time.sleep(1)
                # labels = driver.find_elements_by_xpath('//table[1]/tbody/tr[2]//td|'+
                #     '//table[1]/tbody/tr[3]//td')
                # values = driver.find_elements_by_xpath('//table[1]/tbody/tr[2]//td/strong|'+
                #     '//table[1]/tbody/tr[3]//td/strong')
                # parse out labels and values from text
                text= driver.find_elements_by_xpath('//body/table[2]/tbody/tr[2]//tbody//td|'+
                    '//body/table[2]/tbody/tr[4]//tbody//td|'+
                    '//body/table[2]/tbody/tr[5]//tbody//td')
                text=[i.text.split('\n') for i in text]
                text = [item for sublist in text for item in sublist]
                # detect value/label pairs through looking for colons and alternating pairs
                prev_label_flg=0
                prev_value_flg=0
                labels=[]
                values=[]
                for i in text:
                    if ':' in i:
                        if prev_label_flg==1:
                            values.append('')
                            labels.append(i)
                            prev_label_flg=1
                            prev_value_flg=0
                        if prev_label_flg==0:
                            labels.append(i)
                            prev_label_flg=1
                            prev_value_flg=0
                    else:
                        if prev_label_flg==1:
                            values.append(i)
                            prev_label_flg=0
                            prev_value_flg=1
                        if prev_label_flg==0:
                            prev_label_flg=0
                            prev_value_flg=1
                values = [i.replace(':','') for i in values]
                result= pd.Series(values,index=labels)
                result['type']=type
                # fix for multiples of same field
                if any(result.index.duplicated()):
                    temp_idx = result.index.to_list()
                    newlist = []
                    for i, v in enumerate(temp_idx):
                        totalcount = temp_idx.count(v)
                        count = temp_idx[:i].count(v)
                        newlist.append(v + str(count + 1) if totalcount > 1 else v)
                    # scrub 1's from the assignments
                    result.index=newlist
                result_df = result_df.append(result,ignore_index=True,sort=False)
                # click on Back to get back to search results
                driver.find_element_by_xpath('//*[@value="Back"]').click()
                row_count +=1
        result_df['IMPAQ_ID'] = IMPAQ_ID
        return(result_df)
path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

# start chrome webdriver
chrome_options = Options()
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
#actionChains = ActionChains(driver)
driver.maximize_window()

df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
df= df.loc[df['State']=='NM',:]
df.index=df['IMPAQ_ID']
record_df = pd.DataFrame()
# record_df.coluNMs =['IMPAQ_ID','Filing Number', 'Entity Name', 'Operation Status'
#     , 'Agent Name','Agent Address', 'Store Address']
first = True
for i,row in df.loc[:,:].iterrows():
    print(i)
    record_df = record_df.append(NM_scrape(row['DBA Name_update'],row['IMPAQ_ID'],
        first=first), ignore_index=True,sort=False)
    if first==True:
        first=False
record_df.to_csv(path +'/step_4_work/NM/NM_candidate_records.csv',index=False)
