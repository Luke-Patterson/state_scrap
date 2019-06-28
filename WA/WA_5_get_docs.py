# get documentation for WA businesses
import pandas as pd
import re
import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from dateutil import parser
import pyautogui


# function for downloading all docs for a specific retailer
def WA_ordering(sos_id, impaq_id,doc_dir, rei, new):
    # search by entity ID
    driver.get('https://ccfs.sos.wa.gov/#/')
    time.sleep(3)
    driver.find_element_by_id('rdoEndswith').click()
    driver.find_element_by_id('UBINumber').send_keys(str(sos_id))
    # press search button
    driver.find_element_by_xpath('/html/body/div[1]/ng-include/div/div/main/div[3]/div/div/div/div/div[5]/div[1]/button').click()
    time.sleep(3)
    # click on result
    driver.find_element_by_xpath('//*[@class="btn-link ng-binding"]').click()
    # save website screenshot
    time.sleep(2)
    try:
        if new == False:
            driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
                'Tribal_Master/output/documentation/Existing Retailers/' +
                rei + '_SoS_Website_Record.png')
        if new == True:
            driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
                'Tribal_Master/output/documentation/New Retailers/IMPAQID_' +
                str(impaq_id) + '_SoS_Website_Record.png')
    except:
        raise('screenshot error')
    # click on filing history
    driver.find_element_by_id('btnFilingHistory').click()
    time.sleep(5)
    # get documents
    # download any pdf's they have
    docs= driver.find_elements_by_xpath('//a[@class="btn-link"]')
    # want to also note type of doc:
    doc_table= driver.find_element_by_xpath('//table[@class="table table-striped table-responsive"]/tbody')
    rows= doc_table.find_elements_by_xpath('.//tr')
    doc_types=[]
    doc_dates=[]
    for j in rows:
        doc_types.append(j.find_elements_by_xpath(
                './/td')[3].text)
        doc_dates.append(j.find_elements_by_xpath(
                './/td')[1].text)
    # make sure doc type characters are ok for filenames
    doc_types = [i.replace('/','_') for i in doc_types]
    first=True
    for j,k in zip(docs,doc_types):
        # try:
            # confirm doc is not already in folder
            if (new == True and 'IMPAQID_' + str(impaq_id) + '_SoS_' + k +'.pdf' not in os.listdir(doc_dir))| \
                (new == False and rei + '_SoS_' + k +'.pdf' not in os.listdir(doc_dir)):
                # open PDF
                j.click()
                time.sleep(5)
                # saves to default downloads folder
                if driver.find_element_by_xpath('//*[@id="divSearchResult"]/div/div/div/div[2]/div/table/tbody/tr/td') \
                    .text != 'No Value Found.':
                    driver.find_element_by_xpath('//i[@class="fa fa-file-text-o fa-lg ng-binding ng-isolate-scope ng-scope"]').click()
                    time.sleep(1)
                    # find the downloaded file, rename it, then move to the doc dir
                    list_of_files = glob.glob('C:/Users/lpatterson/Downloads/*')
                    latest_file = max(list_of_files, key=os.path.getctime)
                    if new == False:
                        os.rename(latest_file,doc_dir + '/' + rei + '_SoS_' + str(k) + '.pdf')
                    if new == True:
                        os.rename(latest_file, doc_dir + '/IMPAQID_'+ str(impaq_id) + '_SoS_' + str(k) + '.pdf')
                    # close the doc window
                time.sleep(3)
                driver.find_element_by_class_name('close').click()
                time.sleep(1)
    return([doc_types,doc_dates])
df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/WA/WA_ownership_results.csv')
df = df.loc[df['entity'].isna()==False]
new_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/New Retailers/WA_temp'
old_dir= 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master/output/documentation/Existing Retailers/WA_temp'

# merge REI into data set
rei_df = pd.read_excel("C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/Public Retail Data_original.xlsx")
rei_df['IMPAQ_ID'] = rei_df.index
rei_df = rei_df[['REI','IMPAQ_ID']]
df = df.merge(rei_df, how='left', on='IMPAQ_ID')
# create df for noting document types gathered
doc_df=df[['IMPAQ_ID']].copy()
doc_df['doc_types']=''
doc_df['doc_date']=''

# open different chrome drivers for different download paths
# new retailers
chrome_options = Options()
chrome_options.add_argument("download.default_directory="+new_dir)
driver = webdriver.Chrome(executable_path=
    "C:/Users/lpatterson/AnacondaProjects/chrome_driver/chromedriver.exe",
    chrome_options = chrome_options)
actionChains = ActionChains(driver)
driver.maximize_window()
for i,row in df.loc[df['ori_flg'] == 'New Retailer'].iterrows():
    print(i)
    result = WA_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI, new=True)
    doc_df.at[i,'doc_types']= result[0]
    if result[1] !=[]:
        doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]

# existing retailers
chrome_options = Options()
chrome_options.add_argument("download.default_directory="+old_dir)
driver = webdriver.Chrome(executable_path=
    "C:/Users/lpatterson/AnacondaProjects/chrome_driver/chromedriver.exe",
    chrome_options = chrome_options)
actionChains = ActionChains(driver)
driver.maximize_window()
for i,row in df.loc[df['ori_flg'] != 'New Retailer'].iterrows():
    print(i)
    result = WA_ordering(row.SoS_record, row.IMPAQ_ID,new_dir, row.REI, new=False)
    doc_df.at[i,'doc_types']= result[0]
    if result[1] !=[]:
        doc_df.at[i,'doc_date']= str(max([parser.parse(i) for i in result[1]]))[0:4]
doc_df.to_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/WA' +
    '/WA_docs_found_pt2.csv',index=False)

print(time.process_time())
