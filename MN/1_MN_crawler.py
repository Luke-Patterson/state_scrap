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
def MN_scrape(name, IMPAQ_ID):
    # open URL
    driver.get('https://mblsportal.sos.state.mn.us/Business/Search')
    time.sleep(1)
    # select contains option
    driver.find_element_by_xpath('//*[@id="businessNameTab"]/div[2]/div[2]/div[1]/div[1]/label[2]').click()
    # select include option
    driver.find_element_by_xpath('//*[@id="businessNameTab"]/div[2]/div[2]/div[1]/div[3]/label[2]').click()
    # type in name
    driver.find_element_by_xpath('//*[@id="BusinessName"]').send_keys(name)
    # click search
    driver.find_element_by_xpath('//*[@id="businessNameTab"]/div[1]/div/button').click()
    time.sleep(1)
    # see if any records were returned:
    if 'No results match the criteria entere' not in \
        driver.find_elements_by_xpath('//*[@class="module-bottom"]')[1].text:
        # start a data frame to keep track of results
        result_df = pd.DataFrame()
        # find the rows in results.
        rows = driver.find_elements_by_xpath('//tr')[1:]
        row_count = 1
        # for each row, open the details tab
        for _ in range(len(rows)):
            i = driver.find_elements_by_xpath('//tr')[row_count]
            i.find_element_by_xpath('./td[2]/a').click()
            time.sleep(1)
            data_tbl = driver.find_element_by_id('filingSummary')
            cells = driver.find_elements_by_xpath('//dl')
            cell_df= pd.DataFrame()
            cell_df['Cell']=cells
            cell_df['Label']=cell_df['Cell'].apply(lambda x:
                ' '.join([j.text for j in x.find_elements_by_xpath('./dt')])).str.strip()
            cell_df['Data']=cell_df['Cell'].apply(lambda x:
                ' '.join([j.text for j in x.find_elements_by_xpath('./dd')])).str.strip()
            result=cell_df[['Label','Data']].set_index('Label')
            result=result['Data']
            result['Entity Name'] = driver.find_elements_by_class_name('navbar-brand')[1].text
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
df= df.loc[df['State']=='MN',:]
df.index=df['IMPAQ_ID']
record_df = pd.DataFrame()
# record_df.columns =['IMPAQ_ID','Filing Number', 'Entity Name', 'Operation Status'
#     , 'Agent Name','Agent Address', 'Store Address']
for i,row in df.iloc[:6,:].iterrows():
    print(i)
    record_df = record_df.append(MN_scrape(row['DBA Name_update'],row['IMPAQ_ID']),
        ignore_index=True,sort=False)
record_df.to_csv(path +'/step_4_work/MN/candidate_records.csv',index=False)
