# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 23:20:12 2019

@author: David
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

# =============================================================================
# Scraper
# =============================================================================
df_btc_wallets = pd.DataFrame()
res = requests.get("https://bitinfocharts.com/top-100-richest-bitcoin-addresses.html")
soup = BeautifulSoup(res.content,'lxml')

'''Page 1'''
table = soup.find_all('table')[2] 
df = pd.read_html(str(table))
df_top = df[0]
header = ['ranking', 'address_full', 'balance', 'percentage_coins', 'first_in', 'last_in', 'number_ins', 'first_out', 'last_out', 'number_outs']
df_top.columns = header

table = soup.find_all('table')[3] 
df = pd.read_html(str(table))
df_bottom = df[0]
df_bottom.columns = header

df_btc_wallets = df_btc_wallets.append(df_top)
df_btc_wallets = df_btc_wallets.append(df_bottom)


'''Page 2ff'''
for page in range(2, 101):
    print("Appended page: " + str(page))
    
    res = requests.get("https://bitinfocharts.com/top-100-richest-bitcoin-addresses-" + str(page) + ".html")
    soup = BeautifulSoup(res.content,'lxml')
    
    table = soup.find_all('table')[0] 
    df = pd.read_html(str(table))
    df_top = df[0]
    df_top.columns = header
    
    table = soup.find_all('table')[1] 
    df = pd.read_html(str(table))
    df_bottom = df[0]
    df_bottom.columns = header
    
    df_btc_wallets = df_btc_wallets.append(df_top)
    df_btc_wallets = df_btc_wallets.append(df_bottom)


# =============================================================================
# Data Cleaning
# =============================================================================
df = df_btc_wallets

def get_owner(address_full):
    """Removes unneccessary chars and numbers from the enity name
    """
    address_full.replace('  ', ' ')
    wallet_owner = address_full.split(' ')[-1]    
    numbers = sum(c.isdigit() for c in wallet_owner)
    length = len(wallet_owner)    
    if numbers <= 1 and length < 25:
        return wallet_owner.strip()
    else: 
        return "unknown"


def check_wallet_type(row):
    '''
    EXCHANGE = more than 200 ins
    WHALE = more than 10.000 Bitcoin and less than 200 ins
    BIG_FISH = less than 10.000 Bitcoin and less than 200 ins
    '''
    
    if row['owner'] != "unknown":
        return "Exchange"   
    #elif row['number_ins'] >= 200:
    #    return "EXCHANGE"
    #elif row['balance'] >= 10000:
    #    return "WHALE"
    #else:
    #    return "BIG_FISH"

df["address_full"] = df["address_full"].apply(lambda x: x.replace('wallet:', ' '))
df["owner"] = df["address_full"].apply(get_owner)
df["address"] = df["address_full"].apply(lambda x: x.split(' ')[0])
df["balance"] = df["balance"].apply(lambda x: x.split(' ')[0])
df["balance"] = df["balance"].replace(regex=[','], value='')
df["balance"] = pd.to_numeric(df["balance"])
df['category'] = df.apply(check_wallet_type, axis=1)

# =============================================================================
# Export
# =============================================================================
df.to_csv('wallets_cleaned.csv', index = False)
df = df[['address', 'owner', 'category']]
df.to_csv('wallets_bitinfocharts.csv', index = False)
