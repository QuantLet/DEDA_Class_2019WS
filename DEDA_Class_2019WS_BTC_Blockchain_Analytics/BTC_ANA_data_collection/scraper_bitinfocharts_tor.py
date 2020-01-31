# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 23:20:12 2019

@author: David
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import threading
import time
import random
from torrequest import TorRequest #for windows https://github.com/erdiaker/torrequest/issues/2


# =============================================================================
# Scraper
# =============================================================================      
address_df = pd.read_csv("data/unkown_wallets.csv", index_col=False)

address_list = np.array_split(address_df, 50)
wallet_list = []
proxy_list = []

def scrape_owner(df): 
    """Function that scrapes addresses and the corresponding entity from
    bitinfocharts.com.
    Usage of tor requests and threading for annonymous scraping in parallel
    """
    with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:              
        resp = tr.get('http://ipecho.net/plain')
        proxy = resp.text
        print(proxy)
        proxy_list.append(proxy)
        tr.reset_identity() 
    
        for index, row in df.iterrows():
            address = row['address']         
            try:    
                url = "https://bitinfocharts.com/bitcoin/address/" + address  
                res = tr.get(url)             
                soup = BeautifulSoup(res.content,'lxml')               
                table = soup.find_all('table')[1]
                df = pd.read_html(str(table))[0]
                owner = df.iloc[0,3]
                owner = owner.replace('wallet:', ' ').strip()
                
                wallet_list.append([address, owner])
                print("Appended wallet " + str(len(wallet_list)) + " (" + proxy + ")")
                time.sleep(random.uniform(1, 2))
            except:
                print("Error:", url, sep=" ")
                time.sleep(random.uniform(1,10))
                
    print(">>>finished<<<")
            
    
for counter, df in enumerate(address_list):   
    print("--THREAD " + str(counter) + " STARTED")  
    thread_scrape_owner = threading.Thread(target=scrape_owner, args=(df,))
    thread_scrape_owner.start()      
    time.sleep(random.uniform(1,5))

# =============================================================================
# Export to csv
# =============================================================================
wallets = pd.DataFrame(wallet_list, columns = ['address', 'owner']) 
wallets['category'] = 'Exchange' 
wallets.to_csv('wallets_bitinfocharts_with_numbers.csv', index = False)

def remove_digits(address): 
    """Helper function to separate addresses with real entity names from unknown
    entities consisting only of numbers
    """
    numbers = sum(c.isdigit() for c in address)
    if numbers <= 2:
        return address.strip()
    else: 
        return "unknown"

wallets["owner"] = wallets["owner"].apply(remove_digits)
wallets = wallets[wallets['owner'] != 'unknown']
wallets.to_csv('wallets_bitinfochart_no_numbers.csv', index = False)
