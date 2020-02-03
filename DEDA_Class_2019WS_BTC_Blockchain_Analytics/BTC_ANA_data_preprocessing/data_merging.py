# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 18:33:32 2019

@author: David
"""
import pandas as pd

def merge_data(btc_price_data, tnx, wallets):
    """Merges transactions, price and wallets together"""
      
    wallets = wallets.dropna()
    wallets = wallets.drop_duplicates(subset='address')
    
    #Preprocess transactions
    tnx['date'] = pd.to_datetime(tnx['block_timestamp']).apply(lambda x: '{year}-{month}-{day}'.format(year=x.year, month=x.month, day=x.day))
    
    #Merge trnsactions with wallet labels
    sender = pd.merge(tnx, wallets, left_on='sender', right_on='address', how='left')
    sender.rename(columns = {"owner": "sender_name", "category":"sender_category"}, inplace = True) 
    sender = sender.drop(['address'], axis=1)    
    receiver = pd.merge(tnx, wallets, left_on='receiver', right_on='address', how='left')
    receiver.rename(columns = {"owner": "receiver_name", "category":"receiver_category"}, inplace = True) 
    receiver = receiver.drop(['address'], axis=1)
    
    tnx_labeled = pd.merge(sender, receiver,  how='inner', on=['hash', 'block_timestamp', 'sender','receiver', 'date', 'value'])
    tnx_labeled.rename(columns = {"value": "btc"}, inplace = True) 
    
    #Merge with price data
    btc_price_data = btc_price_data[['date', 'CapMrktCurUSD','PriceUSD']]
    btc_price_data['date'] = pd.to_datetime(btc_price_data['date']).apply(lambda x: '{year}-{month}-{day}'.format(year=x.year, month=x.month, day=x.day))   
    transactions = pd.merge(tnx_labeled, btc_price_data, on='date', how='inner')
    transactions['dollar'] = transactions['btc'] * transactions['PriceUSD']
    transactions['percent_marketcap'] = (transactions['dollar'] / transactions['CapMrktCurUSD']) *100   
    transactions = transactions.drop(['CapMrktCurUSD'], axis=1)  
    return transactions


def filter_data(data, filter_type, value, year_start=2013, year_end=2020):
    """Filters transactions for percent merketcap or dollar value and optional 
    for start and end year
    """
    
    pd.to_numeric(data['percent_marketcap'])
    
    if filter_type == 'dollar':
        filtered_transactions = data[data['dollar'] >= value]
    elif filter_type == 'marketcap':
        filtered_transactions = data[data['percent_marketcap'] >= value]
    
    filtered_transactions['block_timestamp'] = pd.to_datetime(filtered_transactions['block_timestamp']) 
    filtered_transactions = filtered_transactions[(filtered_transactions['block_timestamp'].dt.year >= int(year_start)) & (filtered_transactions['block_timestamp'].dt.year <= int(year_end))]

    filter_name = str(value) + "_" + filter_type + "_"  + str(year_start) + "-" + str(year_end)
    return filter_name, filtered_transactions


def get_unknown_wallets(df):
    """Returns a list of known and unknown wallets"""
    #get addresses that have no label
    sender = df[['sender', 'sender_name']]
    sender.rename(columns = {"sender" : 'address'}, inplace = True) 
    sender_known = sender[sender['sender_name'].notna()]
    sender_unknown = sender[sender['sender_name'].isna()]

    receiver = df[['receiver', 'receiver_name']]
    receiver.rename(columns = {"receiver" : 'address'}, inplace = True) 
    receiver_known = receiver[receiver['receiver_name'].notna()]
    receiver_unknown = receiver[receiver['receiver_name'].isna()]
    
    missing_labels = sender_unknown.append(receiver_unknown)
    missing_labels = missing_labels[['address']].drop_duplicates()  
    
    known_labels = sender_known.append(receiver_known)
    known_labels = known_labels[['address']].drop_duplicates()  
    return missing_labels, known_labels


def add_new_wallets(wallets, labeled_wallets):
    """Adds new wallets to the current list of wallets and removes duplicate"""
    wallet_owners = wallets[['owner', 'category']].drop_duplicates(subset='owner', keep='last').reset_index(drop=True)
    btc_wallets_new = pd.merge(wallet_owners, labeled_wallets[['address', 'owner']], on='owner', how='inner')
    btc_wallets_new = wallets.append(btc_wallets_new).drop_duplicates(subset='address', keep='first')
    return btc_wallets_new



