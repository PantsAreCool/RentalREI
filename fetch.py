import requests
import json

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import numpy as np



def generate_rental_estimate(data):
  # Convert the list into a DataFrame
  df = pd.DataFrame(data)
  
  # Define the feature set (X) and the target variable (y)
  X = df[['sqft', 'beds', 'baths_full', 'lot_sqft', 'list_price']]
  y = df['rent_estimate']
  
  # Split the dataset into training set and test set
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
  
  # Create a linear regression object
  regressor = LinearRegression()
  
  # Train the model using the training sets
  regressor.fit(X_train, y_train)
  
  # Predicting the Test set results
  y_pred = regressor.predict(X_test)
  
  # Comparing actual vs predicted
  compare_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
  print(compare_df)
  
  # Checking the performance of the model
  print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))  
  print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))  
  print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
  print('Percentage Error:',regressor.score(X_test,y_test)*100)
  

