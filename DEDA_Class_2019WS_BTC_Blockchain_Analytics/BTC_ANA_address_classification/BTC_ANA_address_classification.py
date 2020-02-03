# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 15:04:53 2019

@author: David
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

from classification_pipeline import algorithm_pipeline

# =============================================================================
# Load dataset
# =============================================================================
data = pd.read_csv("../data/features_trainingset_all_categories.csv")
df = data.fillna(0)
data = data[['address', 'category'
,'lifetime', 'n_tx', 'n_inputs', 'n_outputs', 'p_inputs', 'mean_inputs', 'mean_outputs', 'p_payback', 'std_inputs', 'std_outputs', 'tx_per_day'
,'std_tx_value_percent_marketcap', 'mean_tx_value_percent_marketcap', 'std_value_percent_marketcap', 'mean_value_percent_marketcap'
,'std_balance_btc', 'mean_balance_btc', 'adr_inputs_btc', 'adr_outputs_btc'
,'input_mean_value_btc', 'input_std_value_btc', 'input_mean_tx_value_btc', 'input_std_tx_value_btc'
,'output_mean_value_btc', 'output_std_value_btc', 'outputs_mean_tx_value_btc', 'outputs_std_tx_value_btc'
,'adr_dif_usd', 'p_adr_dif_usd', 'input_p_adr_tx_value_usd', 'outputs_p_adr_tx_value_usd',  'input_max_tx_value_usd', 'input_max_value_usd','max_balance_usd']]
df = data.drop(['address'], axis = 1)  


#get encoded labels
from sklearn.preprocessing import LabelEncoder
labelencoder = LabelEncoder()
df['target'] = labelencoder.fit_transform(df['category'])
labels = df.drop_duplicates(subset='category')
labels = (labels.sort_values(by='target')['category']).to_list()
df = df.drop(columns='target')

#features, targets
df['category'] = labelencoder.fit_transform(df['category'])
X = df.loc[:, df.columns != 'category']
y = df['category']


'''
#random oversampling
from imblearn.over_sampling import SMOTE
sm = SMOTE(sampling_strategy='auto')
X, y = sm.fit_resample(X, y)
'''

#test, train split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# =============================================================================
# Logistic Regression
#
#Best Params: {'tol': 0.0001, 'max_iter': 5000, 'C': 1.0}
#Accuracy: 0.48 
#F1 macro: 0.42
# =============================================================================
model = LogisticRegression()
param_grid = {
        'C':[0.5, 1.0, 2.0], 
        'max_iter':[1000, 5000, 8000], 
        'tol':[0.0001, 0.0002],
}

model, pred = algorithm_pipeline(X_train, X_test, y_train, y_test, model, 
                                 param_grid, cv=10, scoring_fit='accuracy',
                                 search_mode = 'RandomizedSearchCV', n_iterations = 10,
                                 labels=labels)

# =============================================================================
# Random Forest
#Params: {'n_estimators': 500, 'max_leaf_nodes': 500, 'max_depth': 24}
#Accuracy: 0.81
#F1 macro: 81
# =============================================================================
model = RandomForestClassifier()
param_grid = {
    'n_estimators': [200, 300, 500],
    'max_depth': [18,20,22,24],
    'max_leaf_nodes': [300, 500]
}

model, pred = algorithm_pipeline(X_train, X_test, y_train, y_test, model, 
                                 param_grid, cv=10, scoring_fit='accuracy',
                                 search_mode = 'RandomizedSearchCV', n_iterations = 20,
                                 labels=labels)

# =============================================================================
# XBGBoost Regression
# Accuracy 0.844
# =============================================================================
model = xgb.XGBClassifier()
param_grid = {
    'n_estimators': [400, 700, 1000],
    'colsample_bytree': [0.7, 0.8],
    'max_depth': [15,20,25],
    'reg_alpha': [1.1, 1.2, 1.3],
    'reg_lambda': [1.1, 1.2, 1.3],
    'subsample': [0.7, 0.8, 0.9]
}

model, pred = algorithm_pipeline(X_train, X_test, y_train, y_test, model, 
                                 param_grid, cv=10, scoring_fit='accuracy',
                                 search_mode = 'RandomizedSearchCV', n_iterations = 5,
                                 labels=labels)


# =============================================================================
# LightGBM
# Accuracy 0.85
#param_grid = {'subsample_freq': [20], 'subsample': [0.7], 'reg_lambda': [1.1], 'reg_alpha': [1.2], 'num_leaves': [300], 'n_estimators': [1000], 'min_split_gain': [0.3], 'max_depth': [20], 'colsample_bytree': [0.9]}
# =============================================================================
model = lgb.LGBMClassifier()

param_grid = {
    'n_estimators': [200, 400, 700, 1000],
    'colsample_bytree': [0.8, 0.9, 1],
    'max_depth': [15,20,25, 40, 60],
    'num_leaves': [150, 200, 250, 300],
    'reg_alpha': [1.1, 1.2, 1.3],
    'reg_lambda': [1, 1.1, 1.2],
    'min_split_gain': [0.3, 0.4],
    'subsample': [0.6, 0.7, 0.8],
    'subsample_freq': [20, 40] 
}


#param_grid = {'subsample_freq': [20], 'subsample': [0.7], 'reg_lambda': [1.1], 'reg_alpha': [1.2], 'num_leaves': [300], 'n_estimators': [1000], 'min_split_gain': [0.3], 'max_depth': [20], 'colsample_bytree': [0.9]}

model, pred = algorithm_pipeline(X_train, X_test, y_train, y_test, model, 
                                 param_grid, cv=10, scoring_fit='accuracy',
                                 search_mode = 'GridSearchCV', n_iterations = 1,
                                 labels=labels)

#Feature Importance
feature_importances = pd.DataFrame(model.best_estimator_.feature_importances_,
                                   index = X_train.columns,
                                   columns=['importance']).sort_values('importance', ascending=False)

# =============================================================================
# Neural Network v1
# =============================================================================
'''
# define baseline model
def baseline_model():
	# create model
	model = Sequential()
	model.add(Dense(40, input_dim=40, activation='relu'))
    model.add(Dense(40, activation='relu'))
	model.add(Dense(5, activation='softmax'))
	# Compile model
	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model
 
estimator = KerasClassifier(build_fn=baseline_model, epochs=200, batch_size=5, verbose=0)
kfold = KFold(n_splits=10, shuffle=True)
results = cross_val_score(estimator, X_train, y_train, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))
'''

# =============================================================================
# Neural Network 
# =============================================================================
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder


#feature and target split
X = df.loc[:, df.columns != 'category']
y = df['category']

#Standartization
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(X)
X = scaler.transform(X)

#Label encoding
from sklearn.preprocessing import LabelBinarizer
encoder = LabelBinarizer()
y = encoder.fit_transform(y)

#test, train split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Initialize the constructor
model = Sequential()
# input layer 
model.add(Dense(40, input_shape=(40,), activation='relu'))
# hidden layer 
model.add(Dropout(0.2))
model.add(Dense(40, input_shape=(40,),activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(40, input_shape=(40,),activation='relu'))
# output layer 
model.add(Dense(5, input_shape=(40,), activation='softmax'))

#Model details
model.output_shape
model.summary()
model.get_config()
model.get_weights()

model.compile(loss='categorical_crossentropy', #categorical_crossentropy, binary_crossentropy
              optimizer='adam', #SGD, RMSprop, adam
              metrics=['accuracy'])
                   
model.fit(X_train, y_train,epochs=100, batch_size=10, verbose=1)

#Evaluation
pred = model.predict(X_test)
score = model.evaluate(X_test, y_test,verbose=1)

y_pred = np.argmax(pred, axis = 1)
y_test = np.argmax(y_test, axis = 1)  

# Import the modules from `sklearn.metrics`
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, cohen_kappa_score

# Confusion matrix
confusion_matrix(y_test, y_pred)
precision_score(y_test, y_pred, average='micro')
recall_score(y_test, y_pred, average='micro')
f1_score(y_test,y_pred, average='micro')
f1_score(y_test,y_pred, average='macro')
f1_score(y_test,y_pred, average='weighted')
print(classification_report (y_test, y_pred))


# =============================================================================
# Save model
# =============================================================================
from sklearn.externals import joblib

filename = 'GBM.sav'
joblib.dump(model, '../models/' + filename)


# =============================================================================
# Test with validation set
# GBM Accuracy: 0.883
# =============================================================================
loaded_model = joblib.load('../models/' + 'GBM.sav')

data = pd.read_csv("../data/features_validation.csv")
validation = data[['address', 'category', 'owner']]

df = data.fillna(0)
df = df[['address', 'category'
,'lifetime', 'n_tx', 'n_inputs', 'n_outputs', 'p_inputs', 'mean_inputs', 'mean_outputs', 'p_payback', 'std_inputs', 'std_outputs', 'tx_per_day'
,'std_tx_value_percent_marketcap', 'mean_tx_value_percent_marketcap', 'std_value_percent_marketcap', 'mean_value_percent_marketcap'
,'std_balance_btc', 'mean_balance_btc', 'adr_inputs_btc', 'adr_outputs_btc'
,'input_mean_value_btc', 'input_std_value_btc', 'input_mean_tx_value_btc', 'input_std_tx_value_btc'
,'output_mean_value_btc', 'output_std_value_btc', 'outputs_mean_tx_value_btc', 'outputs_std_tx_value_btc'
,'adr_dif_usd', 'p_adr_dif_usd', 'input_p_adr_tx_value_usd', 'outputs_p_adr_tx_value_usd',  'input_max_tx_value_usd', 'input_max_value_usd','max_balance_usd']]
df = df.drop(['address', 'category'], axis = 1)  

pred = list(loaded_model.predict(df))
df['category'] = pred
df['category_real'] = validation['category']
df['address'] = validation['address']
df['owner'] = validation['owner']
 

for category_number, category_name in enumerate(labels):
    df.loc[df.category == category_number, 'category'] = category_name

view = df[['address', 'owner', 'category', 'category_real']] #,
wallet_owners_real = view.groupby(['category_real']).agg(['count'], as_index=False).reset_index()
wallet_owners_predicted = view.groupby(['category']).agg(['count'], as_index=False).reset_index()

from sklearn.metrics import accuracy_score
accuracy_score(df['category_real'], df['category'])


# =============================================================================
# Predict unknown transactions
# =============================================================================
loaded_model = joblib.load('../models/' + 'GBM.sav')

data = pd.read_csv("../data/features_unknown.csv")
df = data.fillna(0)
address = df['address']
df = df[['address'
,'lifetime', 'n_tx', 'n_inputs', 'n_outputs', 'p_inputs', 'mean_inputs', 'mean_outputs', 'p_payback', 'std_inputs', 'std_outputs', 'tx_per_day'
,'std_tx_value_percent_marketcap', 'mean_tx_value_percent_marketcap', 'std_value_percent_marketcap', 'mean_value_percent_marketcap'
,'std_balance_btc', 'mean_balance_btc', 'adr_inputs_btc', 'adr_outputs_btc'
,'input_mean_value_btc', 'input_std_value_btc', 'input_mean_tx_value_btc', 'input_std_tx_value_btc'
,'output_mean_value_btc', 'output_std_value_btc', 'outputs_mean_tx_value_btc', 'outputs_std_tx_value_btc'
,'adr_dif_usd', 'p_adr_dif_usd', 'input_p_adr_tx_value_usd', 'outputs_p_adr_tx_value_usd',  'input_max_tx_value_usd', 'input_max_value_usd','max_balance_usd']]
df = df.drop(['address'], axis = 1)  

pred = list(loaded_model.predict(df))
df['category'] = pred
df['address'] = address
df['owner'] = 'predicted'
 
for category_number, category_name in enumerate(labels):
    df.loc[df.category == category_number, 'category'] = category_name

predicted_wallets = df[['address', 'owner', 'category']]
wallet_owners = predicted_wallets.groupby(['category']).agg(['count'], as_index=False).reset_index()

predicted_wallets.to_csv("wallets_predicted.csv", index=False)
