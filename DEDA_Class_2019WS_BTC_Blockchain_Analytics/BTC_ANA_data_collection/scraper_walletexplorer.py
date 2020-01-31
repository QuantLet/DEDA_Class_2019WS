# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 19:23:55 2019

@author: David
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import threading
import time
import traceback
from lxml.html import fromstring
from itertools import cycle
from sqlalchemy import create_engine 
import importlib.util

#DB connection
spec = importlib.util.spec_from_file_location("module.name", "C:/Users/David/Dropbox/Code/config.py")
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
DB_CREDENTIALS = config.sqlalchemy_DATASTIG_CRYPTO  
engine = create_engine(DB_CREDENTIALS)

#proxies = pd.read_csv('proxies.txt', names=['ips'], header=None, index_col=False) #https://proxyscrape.com/free-proxy-list
#proxies =  proxies.ips.values.tolist()
proxies_used = []
categories_names = ['Exchange', 'Pools', 'Services', 'Gambling', 'Historic']


def scrape_owner(owner, category_name, proxy):
    """Function that scrapes addresses and the corresponding entity from
    walletexplorer.com
    Usage of proxies and threading for annonymous scraping in parallel.
    Saves the scraped addresses in an sql database.
    """        
    
    url_pages = "https://www.walletexplorer.com/wallet/" + owner
    res, proxy = get_response(proxy, url_pages)
    res = requests.get(url_pages) 
    soup = BeautifulSoup(res.content,'lxml')      
    tmp = []   
    for data in soup.find_all('div', class_='paging'):
        for a in data.find_all('a'):
            tmp.append(a.get('href'))
    tmp = tmp[-1]
    max_page = re.findall(r'\d+', tmp)[0]
    max_page = int(max_page)
    print("Total Pages for", owner, max_page, sep = " ")
                   
    for page in range(1,max_page):   
        try:            
            url = "https://www.walletexplorer.com/wallet/" + owner + "/addresses?page=" + str(page)    
            res, proxy = get_response(proxy, url)                  
            soup = BeautifulSoup(res.content,'lxml')
            table = soup.find_all('table')[0]
            df = pd.read_html(str(table))[0]
            df['owner'] = owner
            df['category'] = category_name
            df = df.drop(columns=['balance', 'incoming txs', 'last used in block'])
            #df_all_wallets = df_all_wallets.append(df)
            df.to_sql("wallets_new", engine, index=False, if_exists='append') 
            print(proxy, owner, "appended page: ",str(page) , sep=" ")
            time.sleep(1)
        except Exception :        
            print(traceback.format_exc())
            break
       
    print(">>>" + owner + " " + str(page) + " finished<<<")
    proxies_used.remove(proxy)
    
      
# =============================================================================
#  Proxies
# =============================================================================

def get_proxies():
    """Scrapes a list of proxies from free-proxy-list.net
    """
    
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:100]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies
    

def find_working_proxy(url):
    """Helper function that returns a proxie that is working for 
    walletexplorer.com
    """
    proxies = get_proxies()
    proxy_pool = cycle(proxies)   
    found_proxy = False   
    
    while found_proxy == False: 
            test_proxy = next(proxy_pool)
            if test_proxy not in proxies_used:
                proxies_used.append(test_proxy)   
                print(len(proxies_used), "/" ,len(proxies), " proxies used", sep ="")
                try:     
                    res = requests.get(url, proxies={"http": test_proxy, "https": test_proxy})    
                    print(test_proxy + " connected")
                    found_proxy = True
                    return res, test_proxy
                except:
                    print(test_proxy + " not working. Skipping")                       


def get_response(proxy, url):
    """Helper function that checks if the proxies is working for specified url
    """   
    found_proxy = False
    while found_proxy == False:    
        try:                   
            res = requests.get(url, proxies={"http": proxy, "https": proxy}) 
            found_proxy = True
            return res, proxy
        except:
            print("connection error " + owner)
            res, proxy = find_working_proxy(url)
            return res, proxy    
    
# =============================================================================
# START    
# =============================================================================
print('Searching for connection. Please wait')   
url = "https://www.walletexplorer.com/"
res, proxy = find_working_proxy(url)

soup = BeautifulSoup(res.content,'lxml')
categories_lists = soup.find_all('ul')   

for counter, category in enumerate(categories_names):
    #if counter == 1 or counter == 2 or counter == 3:
    category_name = categories_names[counter]
    categories_list = categories_lists[counter]
   
    owners_list = []
    for litag in categories_list.find_all('li'):
        pattern = r'\(.*?\)'
        owner = litag.text
        owner = re.sub(pattern, '', owner).strip()
        owners_list.append(owner)
        
    for counter, owner in enumerate(owners_list):
        proxy = find_working_proxy("https://www.walletexplorer.com/")      
        print("--THREAD " + str(counter) + "/" + str(len(owners_list)) + " STARTED " + owner + "--")  
        thread_scrape_owner = threading.Thread(target=scrape_owner, args=(owner, category_name, proxy))
        thread_scrape_owner.start()
