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
def SD_scrape(name, IMPAQ_ID):
    # open URL
    driver.get('https://sosenterprise.sd.gov/BusinessServices/Business/FilingSearch.aspx')
    time.sleep(1)
    # select contains option
    driver.find_element_by_id('ctl00_MainContent_chkSearchIncludes').click()
    # type in name
    driver.find_element_by_id('ctl00_MainContent_txtSearchValue').send_keys(name)
    # click search
    driver.find_element_by_id('ctl00_MainContent_SearchButton').click()
    time.sleep(1)
    # see if any records were returned:
    if 'No Records Found....' not in \
        driver.find_element_by_id('ctl00_MainContent_SearchResultList').text:
        # start a data frame to keep track of results
        result_df = pd.DataFrame()
        # find the rows in results.
        rows = driver.find_elements_by_xpath('//tr')[1:]
        row_count = 1
        # for each row, open the details tab
        for _ in range(min(len(rows),30)):
            i = driver.find_elements_by_xpath('//tr')[row_count]
            id = i.find_element_by_xpath('./td[1]/a').text
            type = i.find_element_by_xpath('./td[3]').text
            i.find_element_by_xpath('./td[1]/a').click()
            time.sleep(1)
            # if it's a DBA, see if there's a link to click to the actual owning entity
            if type == 'DBA - Business':
                links = driver.find_elements_by_xpath('//a[contains(@href,"FilingDetail")]')
                if len(links) > 0:
                    links[0].click()
            labels = driver.find_elements_by_xpath(
                '//*[@id="ctl00_MainContent_updatePanel"]' +
                '//*[@class="col-md-2 hidden-xs hidden-sm FieldLabel"]|'+
                '//*[@id="ctl00_MainContent_updatePanel"]' +
                '//*[@class="col-md-3 hidden-xs hidden-sm FieldLabel"]|'+
                '//*[@id="ctl00_MainContent_updatePanel"]' +
                '//*[@class="col-md-offset-6 col-md-3 hidden-xs hidden-sm FieldLabel"]')
            values = driver.find_elements_by_xpath('//*[@class="col-md-10"]|' +
                '//*[@class="col-md-3"]|//*[@class="col-md-4"]')
                #'//*[@id="ctl00_MainContent_txtOfficeAddresss"]')
            labels = [i.text.replace(':','').strip() for i in labels]
            values = [i.text.replace(':','').strip() for i in values]
            index_val = values.index(id)
            result= pd.Series(values[index_val:],index=labels)
            # drop empty if present
            try:
                result= result.drop('')
            except:
                pass
            # fix for multiples of same field
            if any(result.index.duplicated()):
                temp_idx = result.index.to_list()
                newlist = []
                for i, v in enumerate(temp_idx):
                    totalcount = temp_idx.count(v)
                    count = temp_idx[:i].count(v)
                    newlist.append(v + str(count + 1) if totalcount > 1 else v)
                # scrub 1's from the assignments
                newlist = [i.replace('1','') for i in newlist]
                result.index=newlist
            result['URL'] = driver.current_url
            result_df = result_df.append(result,ignore_index=True,sort=False)
            driver.execute_script("window.history.go(-1)")
            row_count +=1
        result_df['IMPAQ_ID'] = IMPAQ_ID
        return(result_df)
path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

# start chrome webdriver
chrome_options = Options()
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
#actionChains = ActionChains(driver)
#driver.maximize_window()

df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
df= df.loc[df['State']=='SD',:]
df.index=df['IMPAQ_ID']
record_df = pd.DataFrame()
errors = pd.Series()
# record_df.columns =['IMPAQ_ID','Filing Number', 'Entity Name', 'Operation Status'
#     , 'Agent Name','Agent Address', 'Store Address']
for i,row in df.loc[:,:].iterrows():
    print(i)
    try:
        record_df = record_df.append(SD_scrape(row['DBA Name_update'],row['IMPAQ_ID']),
            ignore_index=True,sort=False)
    except:
        chrome_options = Options()
        driver = webdriver.Chrome(executable_path= \
            path + "/chrome_driver/chromedriver.exe")
        actions = ActionChains(driver)
        driver.maximize_window()
        print('error scraping record #' +str(i))
        errors.append(pd.Series(row['IMPAQ_ID']))
record_df.to_csv(path + '/step_4_work/SD/SD_candidate_records.csv',index=False)
errors.to_csv(path + '/step_4_work/SD/SD_scraping_errors.csv',index=False)
