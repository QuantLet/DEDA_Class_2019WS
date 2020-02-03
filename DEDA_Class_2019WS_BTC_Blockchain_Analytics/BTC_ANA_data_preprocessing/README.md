[<img src="https://github.com/QuantLet/Styleguide-and-FAQ/blob/master/pictures/banner.png" width="888" alt="Visit QuantNet">](http://quantlet.de/)

## [<img src="https://github.com/QuantLet/Styleguide-and-FAQ/blob/master/pictures/qloqo.png" alt="Visit QuantNet">](http://quantlet.de/) **BTC_ANA_data_preprocessing** [<img src="https://github.com/QuantLet/Styleguide-and-FAQ/blob/master/pictures/QN2.png" width="60" alt="Visit QuantNet 2.0">](http://quantlet.de/)

```yaml


Name of Quantlet: 'BTC_ANA_data_preprocessing'

Published in: 'DEDA_Class_2019WS'

Description: 'Data Cleaning, Merging and Preprocessing and application of the common input 
heuristic for of all transactions in order to get additional labels for unknown addresses.
Feature Engineering for Multi Class Address Classification'

Keywords: 'Bitcoin, Blockchain, Transactions, Feature Engineering, Data Preprocessing'

Author: 'David Steiner, Minh Nguyen'

See also: 'https://github.com/DavidDanielSteiner/btc_blockchain_analytics'

Submitted:  '28. Jan 2020'

Datafile: 'to be updated'



```

### PYTHON Code
```python

# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 18:40:24 2019

@author: David
"""

import pandas as pd
import io
import requests

# =============================================================================
# Merge Data
# =============================================================================
from data_merging import merge_data

#Import data sources
response=requests.get('https://coinmetrics.io/newdata/btc.csv').content
btc_price_data=pd.read_csv(io.StringIO(response.decode('utf-8'))) #https://coinmetrics.io/community-data-dictionary/
transactions = pd.read_csv("../data/transactions_100BTC.csv")
wallets = pd.read_csv("../data/btc_wallets_new.csv")

#Combine all data sources
tnx = merge_data(btc_price_data, transactions, wallets)
tnx.to_csv("transactions_100BTC_merged.csv", index=False)

# =============================================================================
# Apply common input ownership heuristic 
# https://en.bitcoin.it/wiki/Common-input-ownership_heuristic
# VERY LONG RUNTIME (~10-20 houres)
# =============================================================================
from common_input_heuristic import merge_tnx_wallets, group_transactions, regroup, add_category
from data_merging import add_new_wallets, get_unknown_wallets

#extract only neccessarry labeled addresses
addresses_unknown, addresses_known = get_unknown_wallets(tnx) #unknown=13.3mio ; known=2.3mio
wallets_subset = pd.merge(addresses_known, wallets, on='address', how='inner')
wallets_subset = wallets_subset[['address', 'owner']]

tnx = tnx.drop(['sender_name', 'sender_category', 'receiver_name', 'receiver_category'], axis=1)  
labeled_wallets = pd.DataFrame()

#Common input heuristic algorithm
for i in range(5):
    labeled_tnx = merge_tnx_wallets(tnx, wallets_subset, labeled_wallets)
    df_grouped = group_transactions(labeled_tnx)
    labeled_wallets = labeled_wallets.append(regroup(df_grouped)).drop_duplicates(keep='last')
    print(len(labeled_wallets))

#Add cateogory to owners
labeled_tnx = add_category(wallets, labeled_tnx)
labeled_tnx.to_csv("transactions_100BTC_labeled.csv", index=False)

#Add new addresses to btc_wallets
btc_wallets_new = add_new_wallets(wallets, labeled_wallets)
btc_wallets_new.to_csv("btc_wallets_new.csv", index=False)


# =============================================================================
# Filter transactions for min dollar or min percent of total marcetcap and year
# =============================================================================
from data_merging import merge_data, filter_data

#Filter
filter_name, filtered_tnx = filter_data(labeled_tnx, filter_type = 'marketcap', value=0.01, year_start = 2015, year_end = 2020)

#remove self transaction
tmp = filtered_tnx[filtered_tnx.groupby('hash')['sender'].transform('size') == 1]
self_transactions = tmp[tmp['sender'] == tmp['receiver']] 
filtered_tnx = filtered_tnx.append(self_transactions).drop_duplicates(keep=False)

filtered_tnx.to_csv("transactions_" + filter_name  + ".csv", index=False)

# =============================================================================
# Get list of unknown addresses (for scraping and feature engineering)
# =============================================================================
from data_merging import get_unknown_wallets

addresses_unknown, addresses_known = get_unknown_wallets(filtered_tnx)
addresses_unknown.to_csv("addresses_unknown_" + filter_name + ".csv", index=False)
addresses_known.to_csv("addresses_known_" + filter_name + ".csv", index=False)
addresses_all = addresses_unknown.append(addresses_known)
addresses_all.to_csv("addresses_all_" + filter_name + ".csv", index=False)

# =============================================================================
# Feature engineering trainingset
# VERY LONG RUNTIME (~5-10 houres)
# =============================================================================
from feature_engineering import get_features

category_names = ['Exchange','Gambling','Service','Mixer','Mining']
features_all_categories = pd.DataFrame()  

for category_name in category_names:
    #Import csv with adr details
    all_tnx = pd.read_csv("../data/address_" + category_name + ".csv")
    
    #create new features
    df_features = get_features(all_tnx)
    
    #append 
    features_all_categories = features_all_categories.append(df_features)
    
    #Export csv with features
    df_features.to_csv("features_" + category_name + ".csv", index=False)  
    print(category_name, "exported", sep=" ")
  
#Export all features
features_all_categories.to_csv("features_all_categories.csv", index=False) 

# =============================================================================
# Feature engineering unknown dataset
# VERY LONG RUNTIME (~24-48 houres)
# =============================================================================
features_unknown = pd.DataFrame()  

for number in range(2,5):
    #Import csv with adr details
    all_tnx = pd.read_csv("../data/address_unknown_chunk_" + str(number) + ".csv")    
    
    #create new features
    df_features = get_features(all_tnx)    
    
    #Export csv with features
    df_features.to_csv("features_" + str(number) + ".csv", index=False)  
    print(str(number), "exported", sep=" ")
    
    #append 
    features_unknown = features_unknown.append(df_features)   
    
#Export all features
features_unknown.to_csv("features_unknown.csv", index=False) 

```

automatically created on 2020-02-03