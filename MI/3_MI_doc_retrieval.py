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
def MI_ordering(sos_id, impaq_id,doc_dir, rei, new,url):
    # get record URL
    driver.get(url)
    time.sleep(1)
    doc_types=[]
    doc_dates=[]
    # save screenshot
    if new == False:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/documentation/Existing Retailers/' +
            row.REI + '_SoS_Website_Record.png')
    if new == True:
        driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
            'Tribal_Master/output/documentation/New Retailers/IMPAQID_' +
            str(row.IMPAQ_ID) + '_SoS_Website_Record.png')
        doc_types.append('Website_Record')
    # if there's a view filings button, click on it
    view_filings=driver.find_elements_by_xpath('//*[@id="MainContent_btnViewFilings"]')
    if view_filings!=[]:
        view_filings[0].click()
        time.sleep(1)
        # download any pdf's they have
        docs= driver.find_elements_by_xpath( \
            '//a[@class="link"]')
        import pdb; pdb.set_trace()
        # want to also note type of doc:
        doc_table= driver.find_element_by_xpath( \
            '//table[@id="docTable"]/tbody')
        rows= doc_table.find_elements_by_xpath(
            './/tr')
        for j in rows:
            if j.find_elements_by_xpath(
                './/td')[2].text!='Image unavailable. Please request paper copy.':
                doc_types.append(j.find_elements_by_xpath(
                    './/td')[0].text)
                doc_dates.append(j.find_elements_by_xpath(
                    './/td')[1].text)
        first=True
        for j,k,date in zip(docs,doc_types,doc_dates):
            try:
                # confirm doc is not already in folder
                if (new == True and 'IMPAQID_' + str(impaq_id) + '_SoS_' + k+'.pdf' not in os.listdir(doc_dir))| \
                    (new == False and rei + '_SoS_' + k +'.pdf' not in os.listdir(doc_dir)):
                    # open PDF
                    j.click()
                    time.sleep(3)
                    driver.switch_to.window(driver.window_handles[1])
                    doc_url=driver.current_url
                    response = requests.get(doc_url)
                    if new == True:
                        with open(doc_dir + '/IMPAQID_' + str(impaq_id) + '_SoS_' + k+'.pdf', 'wb') as f:
                            f.write(response.content)
                    if new == False:
                        with open(doc_dir + '/' + str(rei) + '_SoS_' + k+'.pdf', 'wb') as f:
                            f.write(response.content)
                driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
                driver.switch_to.window(driver.window_handles[0])
            except:
                print('error opening PDF')
                driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
                driver.switch_to.window(driver.window_handles[0])
    return([doc_types,doc_dates])
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'MI/MI_FDA_matches.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/New Retailers/MI_temp'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/Existing Retailers/MI_temp'

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
            doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
    else:
        result = MI_ordering(row.SoS_record, row.IMPAQ_ID,old_dir, row.REI,row.URL, new=False)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
doc_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/MI' +
    '/MI_docs_found.csv',index=False)

print(time.process_time())
