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

path = 'C:/Users/lpatterson/AnacondaProjects/Tribal_Master'
# function for scraping necessary information for a single store
def CA_scrape(name, IMPAQ_ID, driver):

    # filter out common words in name for search term use
    # split by spaces
    name_split=pd.Series(name).str.split(pat=" ", expand=True)

    # clear out punctuation marks
    translator = str.maketrans('', '', string.punctuation)
    def punc_rm(s):
        if s!=None:
            s = str(s).translate(translator).upper()
            s = s.replace('-', ' ')
            s = s.replace('/', ' ')
            return(s)
    name_split=name_split.applymap(punc_rm)
    # score typical frequency of words in the DBA name
    # remove common ones that don't help with identification
    def freq_str(str):
        if str!=None:
            return(word_frequency(str, 'en'))
    score_name=name_split.applymap(freq_str)
    search_name = ''
    for i,j in zip(name_split.values[0], score_name.values[0]):
        # filter by cutoff score for common words
        def is_not_number(s):
            try:
                float(s)
                return False
            except ValueError:
                return True
        if j<=.0005 and is_not_number(i):
            search_name = search_name + i + ' '

    first=True
    # Build URL
    out=[]
    for type in ['CORP','LPLLC']:
        url= 'https://businesssearch.sos.ca.gov/CBS/'
        driver.get(url)
        # click on search type
        if type == 'CORP':
            driver.find_element_by_id('CorpNameOpt').click()
        else:
            driver.find_element_by_id('LLCNameOpt').click()
        # click on search criteria and enter name
        driver.find_element_by_id('SearchCriteria').click()
        driver.find_element_by_id('SearchCriteria').send_keys(search_name)
        # press search button
        driver.find_element_by_xpath('//*[@id="formSearch"]/div[5]/div/div/div/button').click()
        # see if there are any results
        if driver.find_element_by_xpath("//table[@id='enitityTable']/tbody").text!= \
            'No matching entities found':
            # get rows of tables
            results= driver.find_elements_by_xpath("//table[@id='enitityTable']/tbody/tr")

            # click on drop down to get first 100 results if it's hit 10
            if len(results)>=10:
                dropdown = driver.find_element_by_name('enitityTable_length')
                for option in dropdown.find_elements_by_tag_name('option'):
                    if option.text == '100':
                        option.click()
                        break
                    results= driver.find_elements_by_xpath( \
                        "//table[@id='enitityTable']/tbody/tr")

            # click on each result's details link
            for j in range(len(results)):
                time.sleep(1)
                button=driver.find_elements_by_xpath( \
                    "//table[@id='enitityTable']/tbody/tr//button")[j]
                button.click()
                # save source code containing biz info
                out.append(driver.page_source)
                driver.execute_script("window.history.go(-1)")
    return(out)

# clean up retrieved HTML output and put into a dataframe
def CA_clean(out, name, IMPAQ_ID, driver):
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        cleantext = cleantext.replace('&amp;','&')
        return(cleantext)
    d_temp=pd.DataFrame(columns= ['Filing Number/Name', 'Operation Status',
    'Agent', 'Agent Address', 'Store Address'])
    for j in out:
        soup=bs.BeautifulSoup(j,'lxml')

        # clean up the html tags and store relevant info in data frame
        store_name_num=cleanhtml(str(soup.select('div[class*=col-md-12] h2')[0]))
        # type appears twice, separate info
        # store_entity_type=cleanhtml(str(soup.select('#maincontent > div:nth-of-type(6) > div.col-sm-8.col-xs-6')[0]))
        store_status=cleanhtml(str(soup.select('#maincontent > div:nth-of-type(6) > div.col-sm-8.col-xs-6')[0]))
        store_agent=cleanhtml(str(soup.select('#maincontent > div:nth-of-type(7) > div.col-sm-8.col-xs-6')[0]))
        agent_address=cleanhtml(str(soup.select('#maincontent > div:nth-of-type(8) > div.col-sm-8.col-xs-6')[0]))
        store_address= cleanhtml(str(soup.select('#maincontent > div:nth-of-type(9) > div.col-sm-8.col-xs-6')[0]))
        d_temp = d_temp.append(pd.DataFrame([[store_name_num,
            store_status,store_agent,agent_address, store_address]],columns= ['Filing Number/Name', 'Operation Status',
            'Agent', 'Agent Address', 'Store Address']))
    d_temp['IMPAQ_ID']=IMPAQ_ID
    return(d_temp)

est_df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
est_df= est_df.loc[est_df['State']=='CA',:]
est_df.reset_index(inplace=True)

# start chrome webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path= \
    path + "/chrome_driver/chromedriver.exe")
actionChains = ActionChains(driver)

out_df= pd.DataFrame()
first=True
for i in range(len(est_df)):
#for i in range(5):
    print('Scraping #', i)
    out = CA_scrape(est_df.loc[i,'DBA Name_update'],est_df.loc[i,'IMPAQ_ID'],driver)
    if len(out) > 0:
        temp_df=CA_clean(out,est_df.loc[i,'DBA Name_update'],est_df.loc[i,'IMPAQ_ID'],driver)
        if first==True:
            out_df=temp_df
            first=False
        else:
            out_df=out_df.append(temp_df)
out_df = out_df.reset_index(drop = True)
out_df.to_excel(path + '/step_4_work/CA/CA_results.xlsx')
