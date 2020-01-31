# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 20:33:51 2019

@author: David
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

df_btc_wallets = pd.DataFrame()

res = requests.get("https://www.cryptoground.com/mtgox-cold-wallet-monitor/")
soup = BeautifulSoup(res.content,'lxml')

'''Page 1'''
table = soup.find_all('table')[3]
df = pd.read_html(str(table))[0]

df = df[[0]]
df.columns = ['address']
df['owner'] = 'Mt.Gox'
df['category'] = 'Exchange'

df.to_csv('data/wallets_cryptoground.csv', index = False)
