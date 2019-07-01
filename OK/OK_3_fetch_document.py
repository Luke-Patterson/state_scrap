# fetch documentation screenshot for each OK record
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path= \
    "C:/Users/lpatterson/AnacondaProjects/Tribal_Master/chrome_driver/chromedriver.exe")

df = pd.read_csv('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/step_4_work/' +
    'OK/OK_FDA_matches.csv',dtype='str')
# rei_df = pd.read_excel('C:/Users/lpatterson/AnacondaProjects/Tribal_Master/input/' +
#     'Public retail data_original.xlsx',dtype='str')
# rei_df.index = rei_df.index.astype('str')
# df = df.merge(rei_df[['REI']], how='left', left_on='IMPAQ_ID',right_index=True)
for i,row in df.iterrows():
    if pd.isna(row.SoS_record) == False:
        url = 'https://www.sos.ok.gov/corp/corpInformation.aspx?id='+ row.SoS_record
        driver.get(url)
        driver.find_element_by_xpath('/html/body').send_keys(Keys.DOWN)
        driver.find_element_by_xpath('/html/body').send_keys(Keys.DOWN)
        driver.find_element_by_xpath('/html/body').send_keys(Keys.DOWN)
        try:
            if row.ori_flg == 'From Original List':
                driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
                    'Tribal_Master/output/documentation/Existing Retailers/' +
                    row.REI + '_SoS_Website_Record.png')
            if row.ori_flg == 'New Retailer':
                driver.get_screenshot_as_file('C:/Users/lpatterson/AnacondaProjects/' +
                    'Tribal_Master/output/documentation/New Retailers/IMPAQID_' +
                    row.IMPAQ_ID + '_SoS_Website_Record.png')
        except:
            raise('record retrival error')
