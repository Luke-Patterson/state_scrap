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

def SD_ordering(sos_id,impaq_id,doc_dir,rei,url,new):
    # go to URL of record
    driver.get(url)
    time.sleep(1)
    # download any pdf's they have
    # want to also note type of doc:
    doc_table= driver.find_element_by_id('ctl00_MainContent_divHistorySummary')
    rows= doc_table.find_elements_by_xpath('.//tr')
    doc_types=[]
    doc_dates=[]
    docs = []
    for j in rows[1:-1]:
        if j.text != '':
            doc_types.append(j.find_elements_by_xpath('.//td')[0].text)
            doc_dates.append(j.find_elements_by_xpath('.//td')[1].text)
            docs.append(j.find_elements_by_xpath('.//td')[2])
    if new == False:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/documentation/Existing Retailers/' +
            row.REI + '_SoS_Website_Record.png')
    if new == True:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/documentation/New Retailers/IMPAQID_' +
            str(row.IMPAQ_ID) + '_SoS_Website_Record.png')
    doc_types.append('Website_Record')
    first=True
    for j,k,date in zip(docs,doc_types,doc_dates):
        # confirm doc is not already in folder, and there's a link to a doc
        if ((new == True and 'IMPAQID_' + str(impaq_id) + '_SoS_' + k+'.pdf' not in os.listdir(doc_dir))| \
            (new == False and rei + '_SoS_' + k +'.pdf' not in os.listdir(doc_dir))) & \
            (j.find_elements_by_xpath('.//a') != []):
                # click to download pdf
                j.find_element_by_xpath('.//a').click()
                time.sleep(5)
                # saves to default downloads folder
                # find the downloaded file, rename it, then move to the doc dir
                list_of_files = glob.glob('C:/Users/lsp52/Downloads/*')
                latest_file = max(list_of_files, key=os.path.getctime)
                k = k.replace('/','_')
                if new == False:
                    os.rename(latest_file,doc_dir + '/' + rei + '_SoS_' + str(k) + '.pdf')
                if new == True:
                    os.rename(latest_file, doc_dir + '/IMPAQID_'+ str(impaq_id) + '_SoS_' + str(k) + '.pdf')
                time.sleep(1)
    return([doc_types,doc_dates])
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'SD/SD_FDA_matches.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/New Retailers'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/Existing Retailers'

# merge REI into data set
rei_df = pd.read_excel("C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/Public Retail Data_original.xlsx")
rei_df['IMPAQ_ID'] = rei_df.index
rei_df = rei_df[['REI','IMPAQ_ID']]
df = df.merge(rei_df, how='left', on='IMPAQ_ID')
# create df for noting document types gathered
doc_df=df[['IMPAQ_ID']].copy()
doc_df['doc_types']=''
doc_df['doc_date']=''
for i,row in df.iloc[:,:].iterrows():
    print(i)
    if row.ori_flg == 'New Retailer':
        result = SD_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI,row.URL, new=True)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
    else:
        result = SD_ordering(row.SoS_record, row.IMPAQ_ID,old_dir, row.REI,row.URL, new=False)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
doc_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/SD' +
    '/SD_docs_found.csv',index=False)

print(time.process_time())
