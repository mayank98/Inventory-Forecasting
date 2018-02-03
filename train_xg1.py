import numpy
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import pdb 
import random
import pickle
from sklearn.externals import joblib
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file
import matplotlib
from sklearn.preprocessing import LabelEncoder
from xgboost.sklearn import XGBClassifier
from matplotlib import pyplot
import datetime
import pandas
import csv

dt=xgb.DMatrix('train_data.data')
num=dt.num_row()
dtrain=dt.slice(range((num/100)*80))
dtest=dt.slice(range((num/100)*80,num))
a,b=0,0

print dtest.num_row(),dtrain.num_row(),"=dtest"
param={
        'max_depth':5,
        'n_estimators':100,
        'objective':"reg:logistic",
        "learning_rate":0.1,
        "min_child_weight":5,
        "colsample_bylevel":0.8,
        "colsample_bytree":0.8,
        "subsample":0.8,
        "gamma":0.5
    }
num_round=71
watchlist={(dtest,'eval'),(dtrain,'train')}
# bst=xgb.train(param,dtrain,num_round,watchlist)
bst=xgb.train(param,dtrain,num_round,watchlist)
print "trained"
joblib.dump(bst, "model_all.dat")
# print bst
y_pred=bst.predict(dtest)
print "predicted"
y_test=dtest.get_label()
print sum(y_test),sum(y_pred),"=sum",len(y_test),len(y_pred)

n=len(y_test)
none_actually=0
none_pred=0
none_common=0
false_neg=0

for i in range(n):
    if y_test[i]==1:
        none_actually+=1
    if y_pred[i] >= 0.2:
        none_pred+=1
        if y_test[i]==1:
            none_common+=1
    else:
        if y_test[i] == 1:
            false_neg += 1

print float(2*none_common)/(none_pred+none_actually),"= F1" # mean F1 score
print float(none_common)/none_actually,"= hit rate"
print float(false_neg)/none_actually,"= miss rate"
# for j in range(10):
# j=1.5
# y=[]
# j=float(j)/10
# for i in y_pred:
#   if i>j:
#       y.append(1)
#   else:
#       y.append(0)
# acc=0
# for i in range(len(y)):
#   if y[i]==y_test[i]:acc+=1
# print float(acc)/len(y)*100,j
# i = open('data/test_data.csv', 'rb')
# reader = csv.reader( i )
# index=0
# actual=[]
# orders=[]
# id=0
# l=[]
# n=0
# la=[]
# ids={}
# j=0
# ar=[]
# ar1=[]
# with open('output.csv', 'ab') as f:
#     writer = csv.writer(f)
#     writer.writerows([["order_id","products"]])
# # print y_test
# for line in reader:
#     j=index
#     if id!=line[0]:
#         if id!=0:
#             # ids[id]=1
#             with open('output.csv', 'ab') as f:
#                 writer = csv.writer(f)
#                 a="None"
#                 if len(l)>0: a=" ".join(l)
#                 writer.writerows([[id,a]])
#         l=[]
#         la=[]
#         id=line[0]
#         if (y_pred[j])>0.18:l.append(line[2])
#     else:
#         if (y_pred[j])>0.18 :l.append(line[2])
#     print "index=", index
#     index+=1
# with open('output.csv', 'ab') as f:
#     writer = csv.writer(f)
#     a="None"
#     if len(l)>0: a=" ".join(l)
#     writer.writerows([[id,a]])
# orders.append([id,l])
# actual.append([id,l])
# ids[id]=1