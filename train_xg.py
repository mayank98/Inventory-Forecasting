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

dtrain = xgb.DMatrix('data/train_data.data')
dtest = xgb.DMatrix('data/test_data.data')
a, b = 0, 0

print dtest.num_row(), dtrain.num_row(), "=dtest"
param = {
    'max_depth': 9,
    'n_estimators': 100,
    'objective': "reg:logistic",
    "learning_rate": 0.1,
    "min_child_weight": 7,
    "colsample_bylevel": 0.8,
    "colsample_bytree": 0.8,
    "subsample": 0.8,
    "gamma": 0
}
num_round = 50
watchlist = {(dtest, 'eval'), (dtrain, 'train')}
# bst=xgb.train(param,dtrain,num_round,watchlist)
bst = xgb.train(param, dtrain, num_round, watchlist)
print "trained"
joblib.dump(bst, "model_all.dat")
# print bst
y_pred = bst.predict(dtest)
print "predicted"
y_test = dtest.get_label()
print sum(y_test), sum(y_pred), "=sum", len(y_test), len(y_pred)
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
i = open('data/test_data.csv', 'rb')
reader = csv.reader(i)
index = 0
actual = []
orders = []
id = 0
l = []
n = 0
la = []
ids = {}
j = 0
ar = []
ar1 = []
with open('output.csv', 'ab') as f:
    writer = csv.writer(f)
    writer.writerows([["order_id", "products"]])
# print y_test
for line in reader:
    j = index
    if id != line[0]:
        if id != 0:
            # ids[id]=1
            with open('output.csv', 'ab') as f:
                writer = csv.writer(f)
                a = "None"
                if len(l) > 0: a = " ".join(l)
                writer.writerows([[id, a]])
        l = []
        la = []
        id = line[0]
        if (y_pred[j]) > 0.18: l.append(line[2])
    else:
        if (y_pred[j]) > 0.18: l.append(line[2])
    index += 1
with open('output.csv', 'ab') as f:
    writer = csv.writer(f)
    a = "None"
    if len(l) > 0: a = " ".join(l)
    writer.writerows([[id, a]])
# orders.append([id,l])
# actual.append([id,l])
# ids[id]=1

print "index=", index

# # ord_avg=[]
# # for i in orders:
# #     a,b=i[0],i[1]
# #     l=sorted(i[1])
# #     ord_avg.append([a,l])
# # with open('output.csv', 'wb') as f:
# #     writer = csv.writer(f)
# #     writer.writerows(orders)
# mf=0
# print len(orders),len(actual)
# print orders[2:10]
# print actual[2:10]
# for i in range(len(orders)):
#   x=orders[i][1]
#   y=actual[i][1]
#   pp=0
#   rc=0
#   m=0
#   for z in x:
#       if z in y:m+=1
#   if len(x)!=0:pp=float(m)/len(x)
#   if len(y)!=0:rc=float(m)/len(y)
#   if (pp+rc)!=0:
#       m=(2*pp*rc)/(pp+rc)
#   mf+=m
# print "mean f1=",float(mf)/len(orders),len(orders)
# na=[]
# i = open('order_products__prior.csv', 'rb' )
# reader = csv.reader( i )
# om={}
# for line in reader:
#   if line[0] in ids:
#       if line[0] in om:om[line[0]].append(line[1])
#       else:om[line[0]]=[line[1]]
# mf=0
# del actual
# # print om
# for i in range(len(orders)):
#   # print i
#   x=orders[i][1]
#   y=om[orders[i][0]]

#   pp=0
#   rc=0
#   m=0
#   for z in x:
#       if z in y:m+=1
#   if len(x)!=0:pp=float(m)/len(x)
#   if len(y)!=0:rc=float(m)/len(y)
#   if (pp+rc)!=0:
#       m=(2*pp*rc)/(pp+rc)
#   if (i<10):
#       print orders[i]
#       print y
#       print "F=",m
#   mf+=m
# print "mean f1=",float(mf)/len(orders)
# # param_grid = dict(learning_rate=learning_rate,n_estimators=n_estimators,max_depth=max_depth)
# param={
#     "objective": "reg:logistic",
#     "booster":"gbtree",
#     "max_depth":25,
#     "learning_rate":0.1,
#     'n_estimators':25,
#     "colsample_bylevel":0.1,
#     'subsample':0.3,
#     'reg_lambda':1,
#    # 'gamma':1
#  #  'min_child_weight':10

# }
# false_positive_rate, true_positive_rate, thresholds = roc_curve(y_test, y_pred)
# roc_auc = auc(false_positive_rate, true_positive_rate)
# joblib.dump(bst, "model_splitLevel.dat")

# # pickle.dump(model, open("pima.pickle.dat", "wb"))
# #plot_tree(model, num_trees=1, rankdir='LR')
# #plt.show()
# plt.title('Receiver Operating Characteristic')
# #print "fpos,trup",false_positive_rate,true_positive_rate
# plt.plot(false_positive_rate, true_positive_rate, 'b',label='AUC = %0.2f'% roc_auc)
# plt.legend(loc='lower right')
# plt.plot([0,1],[0,1],'r--')
# plt.xlim([-0.1,1.2])
# plt.ylim([-0.1,1.2])
# plt.ylabel('True Positive Rate')
# plt.xlabel('False Positive Rate')
# plt.show()
# check something wrong with order id 1102169 , see if it is in order_prior.csv