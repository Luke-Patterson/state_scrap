# turns out there's a better website for records than the one this scraper uses
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
from wordfreq import word_frequency

# function for getting possible matches for record
def AZ_crawling(name, IMPAQ_ID, first):
    # navigate to search url
    driver.get('https://apps.azsos.gov/apps/tntp/se.html')
    if first == True:
        time.sleep(12)
    else:
        time.sleep(3)
    # enter name of address and search
    driver.find_element_by_xpath('//*[@id="Search"]').click()
    driver.find_element_by_xpath('//*[@class="form-control control vk"]')\
        .send_keys(name)
    driver.find_element_by_xpath('//*[@id="Right"]').click()
    time.sleep(20)
    # start a dataframe to keep track of results
    result_df = pd.DataFrame(columns=['Filing Number', 'Entity Name',
        'Operation Status', 'Agent', 'Agent Address', 'Store Address', 'IMPAQ_ID'])

    # go through the rows of the results
    if 'yielded no results' not in driver.find_element_by_xpath(
        '//*[@class="control-label"]').text:
        # set items per page to all
        drop_down = driver.find_element_by_xpath('//*[@class="k-icon k-i-arrow-s"]')
        drop_down.click()
        time.sleep(1)
        drop_down.find_element_by_xpath('//*[@data-offset-index="3"]').click()
        time.sleep(1)
        #filter out trademark/trade name registrations
        count = 0
        for i in driver.find_elements_by_xpath('//*[@role="row"]'):
            regis_type = i.find_elements_by_xpath('//*[@role="gridcell"]')[2].text
            if regis_type != 'Trade Name' and regis_type != 'Trademark' and \
                regis_type != 'AZCC Name Reservation' and 'Partnership' not in \
                regis_type:
                result = pd.Series()
                # record filing number
                result['Filing Number'] = i.find_elements_by_xpath(
                    '//*[@role="gridcell"]')[0].text
                # click on expand arrow
                i.find_element_by_xpath('//*[@class="k-icon k-i-expand"]').click()
                time.sleep(10)
                # record other info
                details = driver.find_elements_by_xpath('//*[@class="k-detail-row' +
                    'k-alt"]')[count]
                result['Entity Name'] = details.find_elements_by_xpath(
                    '//*[@class="row"]')[0].find_elements_by_xpath('//*[@class="'+
                    'col-xs-12 col-sm-2"]')[0].text
                result['Operation Status'] = details.find_elements_by_xpath(
                    '//*[@class="row"]')[1].find_elements_by_xpath('//*[@class="'+
                    'col-xs-12 col-sm-2"]')[1].text
                result['Date Last Updated'] = details.find_elements_by_xpath(
                    '//*[@class="row"]')[3].find_elements_by_xpath('//*[@class="'+
                    'col-xs-12 col-sm-2"]')[1].text
                result['Agent Name'] = details.find_elements_by_xpath(
                    '//*[@class="row"]')[9].find_elements_by_xpath('//*[@class="'+
                    'col-xs-12 col-sm-2"]')[0].text
                result['Agent Address'] = details.find_elements_by_xpath(
                    '//*[@class="row"]')[10].find_elements_by_xpath('//*[@class="'+
                    'col-xs-12 col-sm-2"]')[1].text
                result['IMPAQ_ID']= IMPAQ_ID
                result_df = result_df.append(result)
                count +=1

        import pdb; pdb.set_trace()

path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master'

# start chrome webdriver
chrome_options = Options()
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)

df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
df= df.loc[df['State']=='AZ',:]
df.index=df['IMPAQ_ID']
first = True
for i,row in df.iloc[12:,:].iterrows():
    if first == True:
        AZ_crawling(row['DBA Name_update'],row['IMPAQ_ID'], first)
        first = False
    else:
        AZ_crawling(row['DBA Name_update'],row['IMPAQ_ID'], first)
# driver = webdriver.Chrome(executable_path= \
#     path + "/chrome_driver/chromedriver.exe")
# actionChains = ActionChains(driver)
