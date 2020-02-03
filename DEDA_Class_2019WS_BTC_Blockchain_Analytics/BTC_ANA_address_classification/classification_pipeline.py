# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 13:48:16 2020

@author: David
"""

import numpy as np
import matplotlib.pyplot as plt   
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import classification_report, plot_confusion_matrix


# =============================================================================
# Pipeline
# =============================================================================

def algorithm_pipeline(X_train_data, X_test_data, y_train_data, y_test_data, 
                       model, param_grid, cv=5, scoring_fit='accuracy',
                       do_probabilities = True, model_evaluation = True, 
                       search_mode = 'GridSearchCV', n_iterations = 10, labels=None):
    """Pipeline for Gridsearch/RandomizedSearch and Model evaluation"""
    
    fitted_model = None
    
    if(search_mode == 'GridSearchCV'):
        gs = GridSearchCV(
            estimator=model,
            param_grid=param_grid, 
            cv=cv, 
            n_jobs=-1, 
            scoring=scoring_fit,
            verbose=2
        )
        fitted_model = gs.fit(X_train_data, y_train_data)

    elif (search_mode == 'RandomizedSearchCV'):
        rs = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_grid, 
            cv=cv,
            n_iter=n_iterations,
            n_jobs=-1, 
            scoring=scoring_fit,
            verbose=2
        )
        fitted_model = rs.fit(X_train_data, y_train_data)
    
    print(fitted_model.best_params_)
    print(fitted_model.best_score_)
       
    if(fitted_model != None):
        if do_probabilities:
            pred = fitted_model.predict_proba(X_test_data)
            y_pred = np.argmax(pred, axis = 1)  
        else:
            pred = fitted_model.predict(X_test_data)
            y_pred = pred
           
             
    if model_evaluation:     
        print(classification_report(y_test_data, y_pred))

        #Plot Confusion Matrix
        titles_options = [("Confusion matrix", None),
                  ("Normalized confusion matrix", 'true')]
        for title, normalize in titles_options:
            disp = plot_confusion_matrix(fitted_model, X_test_data, y_test_data,
                                         display_labels=labels,
                                         values_format = '6.2f',
                                         xticks_rotation = 'vertical',
                                         cmap=plt.cm.Blues,
                                         normalize=normalize)
            disp.ax_.set_title(title)
                       
    return fitted_model, pred