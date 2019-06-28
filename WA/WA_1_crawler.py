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

os.chdir('Z:/lpatterson/Tribal')

# start chrome webdriver
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path= \
    "C:/Users/lpatterson/AnacondaProjects/chrome_driver/chromedriver.exe")


# download bulk data from WA website
url="https://www.sos.wa.gov/corps/alldata.aspx"
driver.get(url)
driver.find_element_by_link_text('Text (tab delimited)')
