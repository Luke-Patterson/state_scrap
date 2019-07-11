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
pyautogui.FAILSAFE = False
# start chrome webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path= \
    "C:/Users/lpatterson/AnacondaProjects/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)

# function for downloading all docs for a specific retailer
def MI_ordering(sos_id, impaq_id,doc_dir, rei, url, new):
    # get record URL
    driver.get(url)
    time.sleep(1)
    doc_types=[]
    doc_dates=[]
    # save screenshot
    for _ in range(4):
        driver.find_element_by_tag_name('body').send_keys(Keys.DOWN)
    if new == False:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/Existing Retailers/' +
            row.REI + '_SoS_Website_Record.png')
    if new == True:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/New Retailers/IMPAQID_' +
            str(row.IMPAQ_ID) + '_SoS_Website_Record.png')
        doc_types.append('Website_Record')
    # if there's a view filings button, click on it
    view_filings=driver.find_elements_by_xpath('//*[@id="MainContent_btnViewFilings"]')
    if view_filings!=[]:
        view_filings[0].click()
        time.sleep(1)
        rows = driver.find_elements_by_xpath('//tr[@class="GridRow"]|//tr[@class="GridAltRow"]')
        # download any pdf's they have
        docs= driver.find_elements_by_xpath('//a[@class="link"]')[1:]
        for n,j in enumerate(rows):
            doc_link= docs[n]
            doc_type=j.find_elements_by_xpath('.//td')[1].text.replace('/','_').replace(':','_')
            doc_types.append(doc_type)
            doc_dates.append(j.find_elements_by_xpath('.//td')[2].text)
            # confirm doc is not already in folder
            if (new == True and 'IMPAQID_' + str(impaq_id) + '_SoS_' + doc_type+'.pdf' not in os.listdir(doc_dir))| \
                (new == False and rei + '_SoS_' + doc_type +'.pdf' not in os.listdir(doc_dir)):
                # get pdf url
                doc_url=doc_link.get_attribute('href')
                response = requests.get(doc_url)
                time.sleep(2)
                if new == True:
                    with open(doc_dir + '/IMPAQID_' + str(impaq_id) + '_SoS_' + doc_type+'.pdf', 'wb') as f:
                        f.write(response.content)
                if new == False:
                    with open(doc_dir + '/' + str(rei) + '_SoS_' + doc_type+'.pdf', 'wb') as f:
                        f.write(response.content)
            # except:
            #     print('error opening PDF')
            #     driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
            #     driver.switch_to.window(driver.window_handles[0])
    return([doc_types,doc_dates])
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'MI/MI_FDA_matches.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/New Retailers'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/Existing Retailers'

# merge REI into data set
rei_df = pd.read_excel("C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/Public Retail Data_original.xlsx")
rei_df['IMPAQ_ID'] = rei_df.index
rei_df = rei_df[['REI','IMPAQ_ID']]
df = df.merge(rei_df, how='left', on='IMPAQ_ID')
# create df for noting document types gathered
doc_df=df[['IMPAQ_ID']].copy()
doc_df['doc_types']=''
doc_df['doc_date']=''
for i,row in df.iterrows():
    if row.ori_flg == 'New Retailer':
        result = MI_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI,row.URL, new=True)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([int('0'+i.replace(' ','0')) for i in result[1]]))
    else:
        result = MI_ordering(row.SoS_record, row.IMPAQ_ID,old_dir, row.REI,row.URL, new=False)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([int('0'+i.replace(' ','0')) for i in result[1]]))
doc_df['doc_date']=doc_df['doc_date'].replace('0','')
doc_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/MI' +
    '/MI_docs_found.csv',index=False)

print(time.process_time())
