# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 12:55:35 2020

@author: David
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from classification_pipeline import algorithm_pipeline


# =============================================================================
# Load dataset
# =============================================================================
data = pd.read_csv("../data/features_trainingset_all_categories.csv")

df1 = data.fillna(0)
cleaned_dataset = df1[df1['category'] == 'Mixer'][0:9500]
category_list = ['Exchange', 'Mining', 'Service', 'Gambling']

df1 = df1.drop(['input_mean_tx_value_btc', 'outputs_mean_tx_value_btc', 'tx_total_value_usd', 'input_mean_tx_value_usd', 'mean_tx_value_percent_marketcap', 'mean_value_percent_marketcap'], axis = 1) 
df1 = df1.drop(['address'], axis = 1)  

for category in category_list:
    df = df1[(df1['category'] == 'Mixer') | (df1['category'] == category) ]
    
    
    #get encoded labels
    labelencoder = LabelEncoder()
    df['target'] = labelencoder.fit_transform(df['category'])
    labels = df.drop_duplicates(subset='category')
    labels = (labels.sort_values(by='target')['category']).to_list()
    df = df.drop(columns='target')
    
    #features, targets
    df['category'] = labelencoder.fit_transform(df['category'])
    
    X = df.loc[:, df.columns != 'category']
    y = df['category']
    
    
    #test, train split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    
# =============================================================================
# Model
# =============================================================================
    model = lgb.LGBMClassifier()
    param_grid = {'subsample_freq': [20], 'subsample': [0.7], 'reg_lambda': [1.1], 'reg_alpha': [1.2], 'num_leaves': [200], 'n_estimators': [400], 'min_split_gain': [0.3], 'max_depth': [25], 'colsample_bytree': [0.9]}    
    model, pred = algorithm_pipeline(X_train, X_test, y_train, y_test, model, 
                                     param_grid, cv=10, scoring_fit='accuracy',
                                     search_mode = 'GridSearchCV', n_iterations = 10, 
                                     labels=labels)
    
    
# =============================================================================
# Remove Mixer from categories
# =============================================================================
    df2 = data[data['category'] == category]
    df2 = df2.rename(columns={'category': 'category_orig'})
    address = df2['address']
    remove = df2[['input_mean_tx_value_btc', 'outputs_mean_tx_value_btc', 'tx_total_value_usd', 'input_mean_tx_value_usd', 'mean_tx_value_percent_marketcap', 'mean_value_percent_marketcap', 'address', 'category_orig']]
    df2 = df2.drop(remove.columns.values, axis = 1)   
    df2 = df2.fillna(0)
    predicted = df2
    
    pred = list(model.predict(predicted))
    predicted['category'] = pred
    
    for category_number, category_name in enumerate(labels):
        predicted.loc[predicted.category == category_number, 'category'] = category_name
    
    predicted = pd.concat([predicted, remove], axis=1)
    
    cols = list(data.columns.values)
    df_cleaned = predicted[predicted['category'] != 'Mixer']
    df_cleaned = df_cleaned.reindex(columns=cols).reset_index(drop=True)
    df_cleaned = df_cleaned[0:9500]
    
    cleaned_dataset = cleaned_dataset.append(df_cleaned)
    
    
cleaned_dataset.to_csv('features_trainingset_all_categories_cleaned.csv', index=False)
