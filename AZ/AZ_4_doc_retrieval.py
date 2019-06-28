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
driver.maximize_window()

def AZ_ordering(sos_id,impaq_id,doc_dir,rei,new):
    url='https://ecorp.azcc.gov/BusinessSearch/BusinessInfo?entityNumber='+sos_id
    driver.get(url)
    driver.find_element_by_xpath('/html/body').send_keys(Keys.PAGE_DOWN)
    driver.find_element_by_xpath('/html/body').send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    driver.find_element_by_xpath('//input[@value="Document History"]').click()
    # download any pdf's they have
    docs= driver.find_elements_by_xpath('//table//a[@name="lnkdownload"]')
    # want to also note type of doc:
    doc_table= driver.find_elements_by_xpath('//table//a[@name="lnkdownload"]//span')
    rows= driver.find_elements_by_xpath('//*[@id="xhtml_grid"]//tr')
    doc_types=[]
    doc_dates=[]
    for j in rows[1:]:
        doc_types.append(j.find_elements_by_xpath('.//td')[0].text)
        doc_dates.append(j.find_elements_by_xpath('.//td')[2].text)
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
        # some docs have "no records found" that we need to skip b/c selenium
        # has trouble handling
        if k != 'Records Request - Certified Copies - Corporations':
            try:
                # confirm doc is not already in folder
                if (new == True and 'IMPAQID_' + str(impaq_id) + '_SoS_' + k+'.pdf' not in os.listdir(doc_dir))| \
                    (new == False and rei + '_SoS_' + k +'.pdf' not in os.listdir(doc_dir)):
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
                    #
                    # driver.switch_to.window(driver.window_handles[1])
                    # actionChains.key_down(Keys.CONTROL) \
                    #     .send_keys('s') \
                    #     .key_up(Keys.CONTROL) \
                    #     .perform()
                    # time.sleep(1)
                    # #actionChains.context_click(viewer).perform()
                    # # need to use pyautogui since we need to send keys outside
                    # # of chrome to windows explorer save window
                    # pyautogui.typewrite(['down','down','enter'])
                    # time.sleep(1)
                    # if first==True:
                    #     # enter output path
                    #     import pdb; pdb.set_trace()
                    #     pyautogui.typewrite(['tab','tab','tab','tab','tab','enter'])
                    #     time.sleep(1)
                    #     pyautogui.typewrite(doc_dir)
                    #     pyautogui.typewrite(['enter'])
                    #     time.sleep(1)
                    #     pyautogui.typewrite(['tab','tab','tab','tab','tab','tab'])
                    #     first=False
                    # # Save PDF as REI name, doc type, and candidate number
                    # time.sleep(1)
                    # if new == True:
                    #     pyautogui.typewrite('IMPAQID_')
                    #     pyautogui.typewrite(str(impaq_id))
                    #     pyautogui.typewrite('_SoS_')
                    #     pyautogui.typewrite(k)
                    # if new == False:
                    #     pyautogui.typewrite(rei)
                    #     pyautogui.typewrite('_SoS_')
                    #     pyautogui.typewrite(k)
                    # time.sleep(1)
                    # pyautogui.typewrite(['tab','tab','tab','enter'])
                    # # close the window
                driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
                driver.switch_to.window(driver.window_handles[0])
            except:
                print('error opening PDF')
                driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 'w')
                driver.switch_to.window(driver.window_handles[0])
    return([doc_types,doc_dates])
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'AZ/AZ_FDA_matches.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/New Retailers/AZ_temp'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/Existing Retailers/AZ_temp'

# merge REI into data set
rei_df = pd.read_excel("C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/Public Retail Data_original.xlsx")
rei_df['IMPAQ_ID'] = rei_df.index
rei_df = rei_df[['REI','IMPAQ_ID']]
df = df.merge(rei_df, how='left', on='IMPAQ_ID')
# create df for noting document types gathered
doc_df=df[['IMPAQ_ID']].copy()
doc_df['doc_types']=''
doc_df['doc_date']=''
for i,row in df.iloc[1:,:].iterrows():
    if row.ori_flg == 'New Retailer':
        result = AZ_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI, new=True)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
    else:
        result = AZ_ordering(row.SoS_record, row.IMPAQ_ID,old_dir, row.REI, new=False)
        doc_df.at[i,'doc_types']= result[0]
        if result[1] !=[]:
            doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
doc_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/AZ' +
    '/AZ_docs_found.csv',index=False)

print(time.process_time())
