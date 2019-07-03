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

# function for navigating to a specific record by SOS_ID
def MT_record(SOS_ID):
    # open URL
    driver.get('https://www.mtsosfilings.gov/mtsos-master/')
    time.sleep(1)
    # navigate to search page
    driver.find_element_by_xpath('//*[@class="guest-primary-row3-partA-itemA1-' +
        'menuA1 appMenu appMenuItem appMenuDepth0 appPlainLink noUrlStackPush' +
        ' appNotReadOnly appIndex0"]').click()
    time.sleep(1)
    # type in id number
    driver.find_element_by_id('QueryString').send_keys(str(SOS_ID))
    time.sleep(1)
    # click search
    driver.find_element_by_xpath('//*[contains(@class,"appSubmitButton")]').click()
    time.sleep(5)
    # click on result
    driver.find_element_by_xpath('//a[contains(@class,"appItemSearchResult")]').click()

# function for scraping necessary information for a single store
def MT_scrape(name, IMPAQ_ID):
    # open URL
    driver.get('https://www.mtsosfilings.gov/mtsos-master/')
    time.sleep(1)
    # navigate to search page
    driver.find_element_by_xpath('//*[@class="guest-primary-row3-partA-itemA1-' +
        'menuA1 appMenu appMenuItem appMenuDepth0 appPlainLink noUrlStackPush' +
        ' appNotReadOnly appIndex0"]').click()
    time.sleep(1)
    # select contains from drop down
    driver.find_element_by_xpath('//div[@class="appGroupSelector appRestricted '+
        'appRestrictedSelect"]/select').click()
    driver.find_element_by_xpath('//div[@class="appGroupSelector appRestricted '+
        'appRestrictedSelect"]/select').send_keys(Keys.DOWN)
    driver.find_element_by_xpath('//div[@class="appGroupSelector appRestricted '+
        'appRestrictedSelect"]/select').send_keys(Keys.ENTER)
    time.sleep(2)
    # limit date of search
    driver.find_element_by_xpath('//a[contains(@class, "appRestrictedExpand")]').click()
    time.sleep(.25)
    driver.find_element_by_xpath('//select[contains(@title, "Search Operator")]').click()
    driver.find_element_by_xpath('//select[contains(@title, "Search Operator")]').send_keys(Keys.DOWN)
    driver.find_element_by_xpath('//select[contains(@title, "Search Operator")]').send_keys(Keys.DOWN)
    driver.find_element_by_xpath('//select[contains(@title, "Search Operator")]').send_keys(Keys.ENTER)
    time.sleep(.5)
    driver.find_element_by_xpath('//input[contains(@class, "webuiValidateDate")]').send_keys('01/01/2000')
    # type in name
    driver.find_element_by_id('QueryString').send_keys(name)
    time.sleep(1)
    # click search
    driver.find_element_by_xpath('//*[contains(@class,"appSubmitButton")]').click()
    time.sleep(5)
    # see if any records were returned:
    if 'No results found. Please check your spelling' not in \
        driver.find_element_by_xpath('//*[contains(@class,"appSearchResults")]').text:
        # change the page size to 200
        driver.find_element_by_xpath('//div[@class="appSearchPageSize"]/select').click()
        driver.find_element_by_xpath('//div[@class="appSearchPageSize"]/select').send_keys(Keys.DOWN)
        driver.find_element_by_xpath('//div[@class="appSearchPageSize"]/select').send_keys(Keys.DOWN)
        driver.find_element_by_xpath('//div[@class="appSearchPageSize"]/select').send_keys(Keys.DOWN)
        driver.find_element_by_xpath('//div[@class="appSearchPageSize"]/select').send_keys(Keys.DOWN)
        driver.find_element_by_xpath('//div[@class="appSearchPageSize"]/select').send_keys(Keys.ENTER)
        # start a data frame to keep track of results
        result_df = pd.DataFrame()
        # find the rows in results.
        row_count = 0
        rows = driver.find_elements_by_xpath('//div[contains(@class,"appRepeaterRowContent")]')
        #results = driver.find_elements_by_xpath('//a[contains(@class,"appItemSearchResult")]')
        # for each row, open the details tab
        for _ in range(min(len(rows),30)):
            back_count = 1
            row = driver.find_elements_by_xpath('//div[contains(@class,"appRepeaterRowContent")]')[row_count]
            type = row.find_element_by_xpath('.//div[@class="appMinimalAttr Discriminant"]|'+
                './/div[@class="appMinimalAttr itemRegistrationType"]/span'+
                '[@class="appMinimalValue"]').text
            type = type.replace('Entity Type','').strip()
            actions.move_to_element(row).perform()
            time.sleep(.5)
            driver.find_elements_by_xpath(
                '//a[contains(@class,"appItemSearchResult")]')[row_count].click()
            time.sleep(1)
            labels = driver.find_elements_by_xpath('//*[@class="appLabelText"]')
            values = driver.find_elements_by_xpath('//*[@class="appAttrValue"]|'+
                '//div[contains(@class,"appAttrHyperlink")]/a|'+
                '//li[@class="select2-selection__choice"]')
            labels = [i.text for i in labels]
            labels[0] = 'Record Name on Website'
            values = [i.text for i in values]
            # remove blank labels if present
            labels = [i for i in labels if i != '']
            values = [i for i in values if i != '']

            result= pd.Series(values,index=labels)
            # if type is Assumed Business Name and there's an entity listed,
            # navigate to that record and rescrap data:
            if type =='Assumed Business Name' and 'Business Identifier' in labels \
                and result['Business Identifier']!='Unresolved':
                MT_record(result['Business Identifier'])
                time.sleep(5)
                # rescrap data
                labels = driver.find_elements_by_xpath('//*[@class="appLabelText"]')
                values = driver.find_elements_by_xpath('//*[@class="appAttrValue"]|'+
                    '//div[contains(@class,"appAttrHyperlink")]/a|'+
                    '//li[@class="select2-selection__choice"]')
                labels = [i.text for i in labels]
                labels[0] = 'Record Name on Website'
                values = [i.text for i in values]
                # remove blank labels if present
                labels = [i for i in labels if i != '']
                values = [i for i in values if i != '']

                result= pd.Series(values,index=labels)
                type='Corporation'
                back_count+=3
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
            result['URL'] = driver.current_url
            result['type'] = type
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
df= df.loc[df['State']=='MT',:]
df.index=df['IMPAQ_ID']
record_df = pd.DataFrame()
# record_df.columns =['IMPAQ_ID','Filing Number', 'Entity Name', 'Operation Status'
#     , 'Agent Name','Agent Address', 'Store Address']
for i,row in df.loc[:,:].iterrows():
    print(i)
    record_df = record_df.append(MT_scrape(row['DBA Name_update'],row['IMPAQ_ID']),
        ignore_index=True,sort=False)
record_df.to_csv(path +'/step_4_work/MT/candidate_records.csv',index=False)
