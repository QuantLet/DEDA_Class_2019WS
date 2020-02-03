# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 14:49:53 2019

@author: David
"""

import pandas as pd
import threading
import numpy as np
import requests
import io

def feature_engineering(df):
    """Aggregates all transactions per address and computes new features"""
    
    df = df.sort_values('block_number')    
    df = df.reset_index(drop=True)        
    
    #Calculate Balance
    for index, row in df.iterrows():
        if index == 0:
            balance = 0
        else:
            balance = df.iloc[[index - 1]]['balance_btc']
            
        if row['type'] == 'output':
            balance += row['value_btc']
        else:
            balance -= row['value_btc']
        df.at[index,'balance_btc'] = balance
     
    df['balance_usd'] = df['balance_btc'] * df['PriceUSD']
        
    #Lifetime and inputs
    tx = df.sort_values('type') 
    tx = tx.reset_index(drop=True)  
    tx = tx.drop_duplicates(subset='hash', keep='first') #keep inputs

    df['n_tx'] = len(tx)
    df['lifetime'] = (((max(df['block_timestamp'])) - (min(df['block_timestamp']))).days) +1
    df['tx_per_day'] = df['n_tx'] / df['lifetime']

    inputs = tx[tx['type'] == 'input']
    outputs = tx[tx['type'] == 'output']
    df['n_inputs'] = len(inputs)
    df['n_outputs'] = len(outputs)
    df['p_inputs'] = len(inputs) / df['n_tx']
    
    #transaction value usd category count 
    df['p_0k'] = len(tx[tx['value_usd'] <= 100]) / df['n_tx']
    df['p_1k'] = len(tx[(tx['value_usd'] >= 100) & (tx['value_usd'] < 1000)]) / df['n_tx']
    df['p_10k'] = len(tx[(tx['value_usd'] >= 1000) & (tx['value_usd'] < 10000)]) / df['n_tx']
    df['p_100k'] = len(tx[(tx['value_usd'] >= 10000) & (tx['value_usd'] < 100000)]) / df['n_tx']
    df['p_1m'] = len(tx[(tx['value_usd'] >= 100000) & (tx['value_usd'] < 1000000)]) / df['n_tx']
    df['p_10m'] = len(tx[(tx['value_usd'] >= 1000000) & (tx['value_usd'] < 10000000)]) / df['n_tx']
    df['p_100m'] = len(tx[(tx['value_usd'] >= 10000000) & (tx['value_usd'] < 100000000)]) / df['n_tx']
    df['p_1b'] = len(tx[(tx['value_usd'] >= 100000000) & (tx['value_usd'] < 1000000000)]) / df['n_tx']
    df['p_10b'] = len(tx[tx['value_usd'] >= 1000000000]) / df['n_tx']
        
    #paypack rate (address in input and output)
    tx_type = df.drop_duplicates(subset=['hash', 'type'], keep='first')
    inputs = tx_type[tx_type['type'] == 'input']
    outputs = tx_type[tx_type['type'] == 'output']    
    payback = pd.merge(inputs,outputs, how='inner', on='hash')
    df['p_payback'] = len(payback) / df['n_tx']
    
    #Address counts per transaction
    df['mean_inputs'] = inputs['input_count'].mean()
    df['std_inputs'] = inputs['input_count'].std()
    df['mean_outputs'] = outputs['output_count'].mean()
    df['std_outputs'] = outputs['output_count'].std()
    
    #balance 
    df['mean_balance_btc'] = df['balance_btc'].mean()   
    df['std_balance_btc']  = df['balance_btc'].std() 
    df['mean_balance_usd'] = df['balance_usd'].mean()  
    df['std_balance_usd'] = df['balance_usd'].std() 
    df['max_balance_usd'] = df['balance_usd'].max() 
    df['median_balance_usd'] = df['balance_usd'].median() 
    df['mode_balance_usd'] = df['balance_usd'].mode() 
        
    #totql address input and output transaction value
    df['adr_inputs_btc'] = df[df['type'] == 'input']['value_btc'].sum()
    df['adr_outputs_btc'] = df[df['type'] == 'output']['value_btc'].sum()
    df['adr_inputs_usd'] = df[df['type'] == 'input']['value_usd'].sum()
    df['adr_outputs_usd'] = df[df['type'] == 'output']['value_usd'].sum()
    df['adr_dif_usd'] = df['adr_inputs_usd'] - df['adr_outputs_usd']
    df['p_adr_dif_usd'] = df['adr_dif_usd'] / df['adr_inputs_usd']
    
    #adr transaction value (one address)
    df['input_mean_value_btc'] = inputs['value_btc'].mean()
    df['input_std_value_btc'] = inputs['value_btc'].std()  
    df['input_mean_value_usd'] = inputs['value_usd'].mean()
    df['input_std_value_usd'] = inputs['value_usd'].std()  
    df['input_max_value_usd'] = inputs['value_usd'].max()  
    df['input_median_value_usd'] = inputs['value_usd'].median()  
    df['input_mode_value_usd'] = inputs['value_usd'].mode() 
     
    df['output_mean_value_btc'] = outputs['value_btc'].mean()
    df['output_std_value_btc'] = outputs['value_btc'].std()  
    df['output_mean_value_usd'] = outputs['value_usd'].mean()
    df['output_std_value_usd'] = outputs['value_usd'].std()  
    df['output_max_value_usd'] = outputs['value_usd'].max()  
    df['output_median_value_usd'] = outputs['value_usd'].median()  
    df['output_mode_value_usd'] = outputs['value_usd'].mode()  
    
    #total transaction value (all addresses)
    df['tx_total_value_usd'] = tx['tx_value_usd'].sum()
    
    df['input_mean_tx_value_btc'] = inputs['tx_value_btc'].mean()
    df['input_std_tx_value_btc'] = inputs['tx_value_btc'].std()  
    df['input_mean_tx_value_usd'] = inputs['tx_value_usd'].mean()
    df['input_std_tx_value_usd'] = inputs['tx_value_usd'].std()  
    df['input_max_tx_value_usd'] = inputs['tx_value_usd'].max() 
    df['input_median_tx_value_usd'] = inputs['tx_value_usd'].median() 
    df['input_mode_tx_value_usd'] = inputs['tx_value_usd'].mode() 
      
    df['outputs_mean_tx_value_btc'] = outputs['tx_value_btc'].mean()
    df['outputs_std_tx_value_btc'] = outputs['tx_value_btc'].std()  
    df['outputs_mean_tx_value_usd'] = outputs['tx_value_usd'].mean()
    df['outputs_std_tx_value_usd'] = outputs['tx_value_usd'].std()  
    df['outputs_max_tx_value_usd'] = outputs['tx_value_usd'].max()  
    df['outputs_median_tx_value_usd'] = outputs['tx_value_usd'].median()  
    df['outputs_mode_tx_value_usd'] = outputs['tx_value_usd'].mode()  
    
    #ratio of adr value to tx value
    df['input_p_adr_tx_value_usd'] = df['input_mean_value_usd'] / df['input_mean_tx_value_usd'] 
    df['outputs_p_adr_tx_value_usd'] = df['output_mean_value_usd'] / df['outputs_mean_tx_value_usd'] 
    
    #percent marketcap
    df['mean_value_percent_marketcap'] = df['value_percent_marketcap'].mean()
    df['std_value_percent_marketcap'] = df['value_percent_marketcap'].std()
    df['mean_tx_value_percent_marketcap'] = df['tx_value_percent_marketcap'].mean()
    df['std_tx_value_percent_marketcap'] = df['tx_value_percent_marketcap'].std()
              
    #drop unneccessary columns
    final = df.drop(['block_number', 'block_timestamp', 'value_btc', 'hash',
           'input_count', 'output_count', 'tx_value_btc',
           'balance_btc', 'date', 'value_usd', 'tx_value_usd',
           'value_percent_marketcap', 'tx_value_percent_marketcap',
           'balance_usd', 'type', 
           'CapMrktCurUSD', 'PriceUSD'], axis = 1) 
    final = final.iloc[[0]]
    return final


df_features = pd.DataFrame()    
all_tnx = pd.DataFrame()  
lock = threading.Lock()


def handle_threads(list_address, counter):
    """Helper Function to handle multiple threads"""
    df_features_local = pd.DataFrame()  
    global all_tnx
    
    for address in list_address:
        df = all_tnx [all_tnx['address'] == address]
        final = feature_engineering(df)
        df_features_local = df_features_local.append(final)
        if(counter % 10 == 0):
            print(len(df_features_local), "/" , len(list_address), 'appended. Thread:' , str(counter), sep=" ")       
        
    print(">>>THREAD FINISHED<<<")
    with lock:
        global df_features
        df_features = df_features.append(df_features_local)
  


def get_features(tx, n_threads = 100):
    """Helper Function to prepare for feature engineering.
    Gets a specified number of threads and preprocesses the data"""
    
    global df_features
    df_features = df_features[0:0]
    
    #Add Dollar Price       
    response=requests.get('https://coinmetrics.io/newdata/btc.csv').content
    btc_price_data = pd.read_csv(io.StringIO(response.decode('utf-8')))
    btc_price_data = btc_price_data[['date', 'CapMrktCurUSD','PriceUSD']]
    btc_price_data['date'] = pd.to_datetime(btc_price_data['date']).apply(lambda x: '{year}-{month}-{day}'.format(year=x.year, month=x.month, day=x.day))  
    
    tx['date'] = pd.to_datetime(tx['block_timestamp']).apply(lambda x: '{year}-{month}-{day}'.format(year=x.year, month=x.month, day=x.day))
    tx = pd.merge(tx, btc_price_data, on='date', how='inner')
    tx['value_usd'] = tx['value_btc'] * tx['PriceUSD']
    tx['tx_value_usd'] = tx['tx_value_btc'] * tx['PriceUSD']
    tx['value_percent_marketcap'] = (tx['value_usd'] / tx['CapMrktCurUSD']) *100
    tx['tx_value_percent_marketcap'] = (tx['tx_value_usd'] / tx['CapMrktCurUSD']) *100
    tx['block_timestamp'] = pd.to_datetime(tx['block_timestamp'])
    tx['balance_btc'] = 0.0 
    del tx['is_coinbase']
    
    #Multithrading
    print("Split data into " + str(n_threads) + "threads")
    global all_tnx
    all_tnx = tx
    addresses = all_tnx.drop_duplicates(subset='address')['address'].to_list()
    print('Rows: ', len(addresses), sep=" ")
    addresses_list = np.array_split(addresses, n_threads)
    
    threads = []  
    for counter, list_address in enumerate(addresses_list):   
        counter += 1
        thread = threading.Thread(target=handle_threads, args=(list_address, counter))
        threads.append(thread)
        thread.start() 
              
        if(counter % 10 == 0):
            print('Thread started', counter, sep=" ")
        
    for thread in threads:
        thread.join()
    
    print('All Threads finished')     
    print("Total rows", len(df_features), sep=" ")
    
    return df_features

   