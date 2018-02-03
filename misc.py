import xgboost as xgb
import csv
import pandas as pd
from math import isnan

f=open('train_data_del_cols.csv')
idx,cnt=1,0
for line in f:
    ls=line.split(',')
    cnt+=int(ls[-1])
    print idx
    idx+=1
print cnt