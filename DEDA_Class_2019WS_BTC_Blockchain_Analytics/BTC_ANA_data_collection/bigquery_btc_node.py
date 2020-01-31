# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:23:51 2019

@author: David

https://console.cloud.google.com/bigquery?project=crypto-257815&folder&organizationId&p=bigquery-public-data&d=crypto_bitcoin&t=transactions&page=table
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery #pip install google-cloud-bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\David\Dropbox\Code\Crypto-4c44e65fd97d.json" #https://cloud.google.com/docs/authentication/getting-started
client = bigquery.Client() 

# =============================================================================
# Helpers
# =============================================================================

def get_atts(obj, filter=""):
    """Helper function wich prints the public attributes and methods of the given object.
    Can filter the results for simple term.
    """
    return [a for a in dir(obj) if not a.startswith('_') and filter in a]


def estimate_gigabytes_scanned(query, bq_client):
    """A function to estimate query size. 
    """
    my_job_config = bigquery.job.QueryJobConfig()
    my_job_config.dry_run = True
    my_job = bq_client.query(query, job_config=my_job_config)
    BYTES_PER_GB = 2**30
    estimate = my_job.total_bytes_processed / BYTES_PER_GB    
    print(f"This query will process {estimate} GBs.")


# =============================================================================
# get transactions with max transaction value
# =============================================================================
def get_all_tx_over_value(btc):    
    """Pulls all transactions where the receiver of the transaction received
    more than a specified BTC value
    """
    btc_satoshi = 100000000 #btc in satoshi    
    satoshi_amount = btc * btc_satoshi
    
    query = """
    SELECT
        `hash`,
        block_timestamp,
        array_to_string(inputs.addresses, ",") as sender,
        array_to_string(outputs.addresses, ",") as receiver,
        output_value / 100000000 as value
    FROM `bigquery-public-data.crypto_bitcoin.transactions`
        JOIN UNNEST (inputs) AS inputs
        JOIN UNNEST (outputs) AS outputs
    WHERE outputs.value  >= @satoshis
        AND inputs.addresses IS NOT NULL
        AND outputs.addresses IS NOT NULL
    GROUP BY `hash`, block_timestamp, sender, receiver, value
    """
       
    query_params = [    
        bigquery.ScalarQueryParameter("satoshis", "INT64", satoshi_amount),
    ]
     
    estimate_gigabytes_scanned(query, client)
    
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = query_params
    query_job = client.query(
            query,
            job_config=job_config,
    )
    result = query_job.result()
    
    tx = result.to_dataframe()   
    print("Successfully pulled transactions from bigquery")
    return tx

# =============================================================================
# get all transactions for a list of addresses
# =============================================================================   
def get_all_tx_from_address(list_addresses):
    """Pulls the complete transaction history from a list of specified 
    BTC addresses 
    """

    query = """
    SELECT 
        array_to_string(i.addresses, ",") as address,
        i.transaction_hash,
        i.block_number,  
        i.value / 100000000 as value_btc ,
        t.`hash`,
        t.block_timestamp,  
        t.input_count,
        t.output_count,
        t.is_coinbase,
        t.output_value / 100000000 as tx_value_btc , 
        'input' as type
        
    FROM `bigquery-public-data.crypto_bitcoin.inputs` as i     
    INNER JOIN `bigquery-public-data.crypto_bitcoin.transactions` AS t ON t.hash = i.transaction_hash    
    WHERE array_to_string(i.addresses, ',') in UNNEST(@address)
    
    UNION ALL
    
    SELECT 
        array_to_string(o.addresses, ",") as address,
        o.transaction_hash,
        o.block_number,       
        o.value / 100000000 as value_btc ,
        t.`hash`,
        t.block_timestamp,  
        t.input_count,
        t.output_count,
        t.is_coinbase,
        t.output_value / 100000000 as tx_value_btc, 
        'output' as type
        
    FROM `bigquery-public-data.crypto_bitcoin.outputs` as o     
    INNER JOIN `bigquery-public-data.crypto_bitcoin.transactions` AS t ON t.hash = o.transaction_hash        
    WHERE array_to_string(o.addresses, ',') in UNNEST(@address)
    """

    print(estimate_gigabytes_scanned(query, client))
    
    query_params = [    
        bigquery.ArrayQueryParameter("address", "STRING", list_addresses),
    ]
    
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = query_params
    query_job = client.query(
        query,
        job_config=job_config,
    )
    result = query_job.result()
    
    tx = result.to_dataframe() 
    tx = tx.drop(columns=['transaction_hash'])
    print("Successfully pulled transactions from bigquery")
    return tx
  
    