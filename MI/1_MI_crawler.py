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
from itertools import groupby

# function for scraping necessary information for a single store
def MI_scrape(name, IMPAQ_ID):
    # open URL
    driver.get('https://cofs.lara.state.mi.us/corpweb/CorpSearch/CorpSearch.aspx')
    time.sleep(1)
    # select contains from drop down
    driver.find_element_by_id('ddBeginsWithEntityName').click()
    driver.find_element_by_id('ddBeginsWithEntityName').send_keys(Keys.DOWN)
    driver.find_element_by_id('ddBeginsWithEntityName').send_keys(Keys.DOWN)
    driver.find_element_by_id('ddBeginsWithEntityName').send_keys(Keys.ENTER)
    time.sleep(2)
    # type in name
    driver.find_element_by_id('txtEntityName').send_keys(name)
    time.sleep(1)
    # click search
    driver.find_element_by_id('MainContent_btnSearch').click()
    time.sleep(2)
    # see if any records were returned; sends you to a different page if it does
    if driver.current_url != 'https://cofs.lara.state.mi.us/corpweb/CorpSearch/CorpSearch.aspx':
        # start a data frame to keep track of results
        result_df = pd.DataFrame()
        # find the rows in results.
        row_count = 0
        rows = driver.find_elements_by_xpath('//tr[@class="GridRow"]|//tr[@class="GridAltRow"]')
        # for each row, open the details tab
        print(str(len(rows))+' candidates found')
        for _ in range(len(rows)):
            back_count = 1
            row = driver.find_elements_by_xpath('//tr[@class="GridRow"]|//tr[@class="GridAltRow"]')[row_count]
            actions.move_to_element(row).perform()
            time.sleep(.5)
            row.find_element_by_xpath('.//a').click()
            time.sleep(1)
            text = driver.find_elements_by_xpath('//span[@class="p5"]|//span[@class="p1"]|'
                +'//tr[@class="p1"]//td|//tr[@class="p1"]//strong|//span[@id="purposeLabel"]|'
                +'//*[@id="MainContent_termlabel"]/span/span|//*[@id="MainContent_lblInactiveDateLabel"]/span[1]|'
                +'//*[@id="MainContent_lblInactiveDateLabel"]/span[2]')
            text= [i.text.strip() for i in text]
            # delineate between values and labels using colons
            # drop colon labels that have no values associated with them
            text = [i for i in text if i not in ['The name and address of the Resident Agent:',
                'Registered Office Mailing address:', 'Managed By:',
                'View filings for this business entity:',
                'Comments or notes associated with this business entity:']]
            # remove duplicated values from text
            text = [x[0] for x in groupby(text)]
            text = [i for i in text if i !='']
            text = [i for i in text if i[-1]==':' or ':' not in i]
            # first two values are repeated data without labels
            text = text[2:]
            # # label_pos creates flags for labels
            # label_pos = [1 if ':' in i else 0 for i in text]
            # # we'll then check to see if labels appear consecutively, and
            # # insert blank values when no value accompanies a label
            # prev=None
            # newtemp=[]
            # for i,j in zip(text,label_pos):
            #     if prev==1 & j==1:
            #         newtemp.append('')
            #     newtemp.append(i)
            #     prev=j
            # # make sure we are not ending on a label
            # if prev==1:
            #     newtemp.append('')
            # text=newtemp
            #
            # # delineate labels and values
            # labels = [i for i in text if ':' in i]
            # values = [i for i in text if ':' not in i]

            # try the New Mexico method for this
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
            # make sure we are not ending on a label
            if prev_label_flg==1:
                 values.append('')
            result= pd.Series(values,index=labels)
            #try:
            # except:
            #     print('error: parsed different number of labels and fields for a candidate')
            #     for i in range(back_count):
            #         driver.execute_script("window.history.go(-1)")
            #         time.sleep(1)
            #     row_count +=1
            #     continue
            # # fix for multiples of same field
            if any(result.index.duplicated()):
                temp_idx = result.index.to_list()
                newlist = []
                for i, v in enumerate(temp_idx):
                    totalcount = temp_idx.count(v)
                    count = temp_idx[:i].count(v)
                    newlist.append(v + str(count + 1) if totalcount > 1 else v)
                result.index=newlist
            result['URL'] = driver.current_url
            result_df = result_df.append(result,ignore_index=True,sort=False)
            for i in range(back_count):
                driver.execute_script("window.history.go(-1)")
                time.sleep(1)
            row_count +=1
        result_df['IMPAQ_ID'] = IMPAQ_ID
        return(result_df)
path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

# start chrome webdriver
chrome_options = Options()
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
actions = ActionChains(driver)
driver.maximize_window()

df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
df= df.loc[df['State']=='MI',:]
df.index=df['IMPAQ_ID']
record_df = pd.DataFrame()
errors = pd.Series()
# record_df.columns =['IMPAQ_ID','Filing Number', 'Entity Name', 'Operation Status'
#     , 'Agent Name','Agent Address', 'Store Address']
for i,row in df.loc[2047:,:].iterrows():
    print(i)
    # try:
    record_df = record_df.append(MI_scrape(row['DBA Name_update'],row['IMPAQ_ID']),
        ignore_index=True,sort=False)
    # except:
    #     chrome_options = Options()
    #     driver = webdriver.Chrome(executable_path= \
    #         path + "/chrome_driver/chromedriver.exe")
    #     actions = ActionChains(driver)
    #     driver.maximize_window()
    #     print('error scraping record #' +str(i))
    #     errors.append(pd.Series(row['IMPAQ_ID']))
record_df.to_csv(path + '/step_4_work/MI/MI_candidate_records_pt2.csv',index=False)
errors.to_csv(path + '/step_4_work/MI/MI_scraping_errors.csv',index=False)
