import numpy as np
import pandas as pd

orders = pd.read_csv('data/orders.csv')
prior = pd.read_csv('data/order_products__prior.csv')
order_prior = pd.merge(prior,orders,on=['order_id','order_id'])
print "sorting"
order_prior = order_prior.sort_values(by=['user_id','order_id'])
print order_prior.head()
print order_prior.describe()