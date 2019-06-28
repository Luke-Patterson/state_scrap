def OK_execute(path):
    import urllib.request
    import urllib.parse
    import bs4 as bs
    import re
    import pandas as pd
    import os
    import numpy as np
    import time

    os.chdir(path)

    est_df= pd.read_csv(path + "/step_3_work/output/full_retailer_list.csv")
    est_df= est_df.loc[est_df['State']=='OK',:]
    est_df.reset_index(inplace=True)

    def OK_scrape(name):
        uri = 'https://www.sos.ok.gov/corp/corpinquiryfind.aspx'

        # fields to pass to form
        formFields = (
           (r'__VSTATE', r'/wEPDwUKMTAzMzYwOTI1Ng9kFgJmD2QWBAIBD2QWAgIGDxYCHgRocmVmBRQuLi9BcHBfVGhlbWVzL2llLmNzc2QCAw9kFgICBQ9kFgICAQ9kFgJmD2QWBgIBDw8WAh4HVmlzaWJsZWdkFggCAQ8WAh4EVGV4dAUcQnVzaW5lc3MgRW50aXRpZXMgU2VhcmNoIEFsbGQCBQ8WAh8CBStFbnRlciBOYW1lIGFuZCBDbGljayBvbiB0aGUgJ1NlYXJjaCcgQnV0dG9uZAIHD2QWBAIBD2QWAgILDxBkZBYBZmQCAg9kFgICBQ9kFgJmD2QWAgIBD2QWAmYPZBYCAgEPZBYCAhEPEGRkFgFmZAILD2QWAgIBEBBkZBYBZmRkAgMPDxYCHwFoZGQCDQ9kFgJmD2QWBgIFDw8WBB8CBQ9Ub3RhbCBSZXN1bHRzOiAfAWhkZAIHDw8WBB8CBQEwHwFoZGQCCRA8KwANAQAPFgYfAWceC18hSXRlbUNvdW50Zh4LXyFEYXRhQm91bmRnZGRkGAMFM2N0bDAwJERlZmF1bHRDb250ZW50JENvcnBOYW1lU2VhcmNoMSRFbnRpdHlHcmlkVmlldw8UKwAKZGRkZGRkFQEMRmlsaW5nTnVtYmVyZGYUKwABKClZU3lzdGVtLkludDY0LCBtc2NvcmxpYiwgVmVyc2lvbj0yLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODkKMzYxMjQzMDg4NmQFL2N0bDAwJERlZmF1bHRDb250ZW50JENvcnBOYW1lU2VhcmNoMSRNdWx0aVZpZXcxDw9kZmQFL2N0bDAwJERlZmF1bHRDb250ZW50JENvcnBOYW1lU2VhcmNoMSRNdWx0aVZpZXcyDw9kZmTJxWqwshaEWxdJ8frrlnRQdJ6wFw'),
           (r'__VIEWSTATE', r''),
           (r'ctl00$DefaultContent$CorpNameSearch1$_singlename', name),
           (r'ctl00$DefaultContent$CorpNameSearch1$SearchButton', 'Search')
        )
        for n in range(10):
            try:
                encodedFields = urllib.parse.urlencode(formFields).encode("utf-8")
                req = urllib.request.Request(uri)
                f= urllib.request.urlopen(req, encodedFields)
                out=str(f.read())
                break
            except:
                print('error encountered, retrying request #' + str(n))
                time.sleep(3)
                continue
        return(out)
        # need to figure out how to get past first page, this is the start on that
        # from selenium import webdriver
        # driver = webdriver.PhantomJS(executable_path='C:/Users/lpatterson/AppData/Local/Continuum/anaconda3/Lib/site-packages/selenium/webdriver/phantomjs')
        # driver.get(uri)
        # p_element = driver.find_element_by_id(id_='aspnetForm')
        # print(p_element)

    # function to create list of even, odd numbers
    def evens_odds(lower, upper, evens=True):
        num_list=[]
        for i in range(lower,upper):
            if i%2!=0 and evens==False:
                num_list.append(i)
            elif i%2==0 and evens==True:
                num_list.append(i)
        return(num_list)

    # clean up retrieved HTML output
    def OK_clean(out, name, IMPAQ_ID):
        # Read the results in BeautifulSoup
        soup=bs.BeautifulSoup(out,'lxml')
        # text_file = open("Output.txt", "w")
        # text_file.write(str(soup.prettify()))


        # clean up the html tags and store relevant info in lists
        def cleanhtml(raw_html):
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            cleantext = cleantext.replace('&amp;','&')
            return(cleantext)

        # Filing number
        store_filenum=[cleanhtml(str(i)) for i in soup.select('a[target*=_self]')]
        # not a cleanly labeled id number in HTML, need to remove extraneous tags picked up
        # Id's are all numbers, so we will only keep numeric elements
        store_filenum= [i for i in store_filenum if i.isdigit()]
        store_filenum= [int(i) for i in store_filenum]

        store_name=[cleanhtml(str(i)) for i in soup.select('span[id*=lblName]')]

        temp_type= [cleanhtml(str(i)) for i in soup.select('span[id*=lblType]')]
        # type appears twice, separate info
        store_entity_type=[temp_type[i] for i in evens_odds(0,len(temp_type),evens=True)]
        store_regist_type=[temp_type[i] for i in evens_odds(0,len(temp_type),evens=False)]

        store_status=[cleanhtml(str(i)) for i in soup.select('span[id*=lblStatus]')]
        store_owner=[cleanhtml(str(i)) for i in soup.select('span[id*=lblAgentName]')]
        store_owner_city=[cleanhtml(str(i)) for i in soup.select('span[id*=lblCity]')]
        store_owner_state=[cleanhtml(str(i)) for i in soup.select('span[id*=lblState]')]
        d_temp=pd.DataFrame({'Filing Number':store_filenum, 'Name':store_name,'Type':store_entity_type,
             'Status':store_status,'Owner':store_owner, 'Owner City': store_owner_city, \
             'Owner State': store_owner_state})
        d_temp['IMPAQ_ID']=IMPAQ_ID

        return(d_temp)

    # testing out scraping on first 20 records in OK
    out_df= pd.DataFrame()
    first=True
    for i in range(len(est_df)):
        print('Scraping #', i)
        out= OK_scrape(est_df.loc[i,'DBA Name_update'])
        temp_df=OK_clean(out,est_df.loc[i,'DBA Name_update'],est_df.loc[i,'IMPAQ_ID'])
        if first==True:
            out_df=temp_df.merge(est_df, on='IMPAQ_ID', sort=True)
            first=False
        else:
            out_df=out_df.append(temp_df.merge(est_df, on='IMPAQ_ID'))

    out_df.to_excel(path + '/step_4_work/OK/OK_results.xlsx')
path = "C:/Users/lpatterson/AnacondaProjects/Tribal_Master"
OK_execute(path)
