# scraper to query AZ SOS website for possible matches for each retailer
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
from wordfreq import word_frequency
import traceback

# function for getting possible matches for record
def AZ_crawling(name, IMPAQ_ID):
    # att = 0
    # while True:
    #     try:
    driver.delete_all_cookies()
    # navigate to search url
    driver.get('https://ecorp.azcc.gov/EntitySearch/Index')
    # change search type to "Contains"
    #driver.find_element_by_id('SearchType').click()
    time.sleep(5)
    driver.find_element_by_xpath('//option[@value="Contains"]').click()
    driver.find_element_by_name('txt_quicksearch').send_keys(name)
    driver.find_element_by_id('btn_Search').click()
    time.sleep(20)
    # see if any results were found
    no_res_msg=driver.find_elements_by_xpath('//*[@class="sweet-alert '+
        'showSweetAlert visible"]')
    if len(no_res_msg) != 0:
        pass
        # TODO:possibly return some blank objects representing not found
    else:
        # see how many records there are
        record_txt=driver.find_element_by_xpath('//*[@id="pagination-digg"]').text
        record_num=max(map(int,[e for e in re.split("[^0-9]", record_txt) if e != '']))
        page_num=math.ceil(record_num/20)
        # # grab all the entity numbers for each record that's not
        # a trade name/trademark
        records=[]
        for n in range(page_num):
            for i in driver.find_elements_by_tag_name('tr')[1:-1]:
                regis_type = i.find_elements_by_tag_name('td')[2].text
                if regis_type != 'Trade Name' and regis_type != 'Trademark' and \
                    regis_type != 'AZCC Name Reservation' and 'Partnership' not in \
                    regis_type and regis_type != 'Unidentified':
                    records.append(i.find_elements_by_tag_name('td')[0].text)
            # if not the last page, click on the "next page" button
            if n != page_num - 1:
                # scroll down to end of page so we can click next
                driver.find_element_by_xpath('/html/body').send_keys(Keys.PAGE_DOWN)
                driver.find_element_by_xpath('/html/body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
                driver.find_element_by_xpath('//a[text()[contains(.,"Next")]]').click()
                time.sleep(20)
        return(records)
        #break
        # except:
        #     if att < 10:
        #         print('scraping error, attempt #' + str(att))
        #         att+=1
        #         continue
        #     else:
        #         raise('too many scraping attempts')
path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

# start chrome webdriver
chrome_options = Options()
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)
driver.maximize_window()

df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
df= df.loc[df['State']=='AZ',:]
df.index=df['IMPAQ_ID']
record_df = df[['IMPAQ_ID']].copy()
record_df['records']=''
for i,row in df.loc[2834:,:].iterrows():
    record_df.at[i, 'records'] = AZ_crawling(row['DBA Name_update'],row['IMPAQ_ID'])
record_df.to_csv(path +'/step_4_work/AZ/candidate_records.csv',index=False)
