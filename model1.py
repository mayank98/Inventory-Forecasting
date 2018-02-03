import csv
import pandas as pd 
import numpy as np
import datetime

order_products_train_df = pd.read_csv("data/order_products__train.csv")
order_products_prior_df = pd.read_csv("data/order_products__prior.csv")
orders_df = pd.read_csv("data/orders.csv")
products_df = pd.read_csv("data/products.csv")
# aisles_df = pd.read_csv("aisles.csv")
# departments_df = pd.read_csv("departments.csv")

order_products_prior_df = pd.merge(order_products_prior_df, products_df, on='product_id', how='left')
order_products_train_df = pd.merge(order_products_train_df, products_df, on='product_id', how='left')
products_df=None
d_prior={}
d_last_prior={}
id=1
pl=[]
totalDays=0
id_test={}
for index,row in orders_df.iterrows():
    print index
    if index>10000:break
    if row['user_id']!=id:
        if pl[-1][-1]=="test":  
            id_test[pl[0][0]]=1
            d_prior[id]=pl[:-1]
            d_last_prior[id]=pl[-1]
        pl=[]
        totalDays=row["days_since_prior_order"]
        id=row['user_id']
        days_since_prior_order=row['days_since_prior_order']
        if row['days_since_prior_order']==None:days_since_prior_order=totalDays/row['order_number']
        pl.append([row['order_id'],row['order_number'],row['order_dow'],row['order_hour_of_day'],totalDays,days_since_prior_order,row['eval_set']])
    else:
        totalDays+=row["days_since_prior_order"]
        days_since_prior_order=row['days_since_prior_order']
        if row['days_since_prior_order']==None:days_since_prior_order=totalDays/row['order_number']
        pl.append([row['order_id'],row['order_number'],row['order_dow'],row['order_hour_of_day'],totalDays,days_since_prior_order,row['eval_set']])
if pl[-1][-1]=="test":
    d_prior[id]=pl[:-1]
    id_test[pl[0][0]]=1
    d_last_prior[id]=pl[-1]
print len(d_prior),len(d_last_prior)

del order_products_train_df
order_prior={}
id=2
l=[]
for index,row in order_products_prior_df.iterrows():
    print index,"order"
    if index>1000000:break
    if row['order_id'] in id_test:
        if row['order_id']!=id:
            order_prior[id]=l
            id=row['order_id']
            l=[[row['aisle_id'],row['department_id'],row['add_to_cart_order'],row['reordered'],row['product_id']]]
        else:
            l.append([row['aisle_id'],row['department_id'],row['add_to_cart_order'],row['reordered'],row['product_id']])
if id not in order_prior:order_prior[id]=l
print len(order_prior), order_prior
del orders_df
del order_products_prior_df
user_props={}
for user in d_prior:
    avg_rate,avg_length=0,0
    l=d_prior[user]
    dep=[0 for i in range(21)]
    aisle=[0 for i in range(134)]
    day=[0 for i in range(7)]
    hour=[0 for i in range(24)]
    for i in l:
        avg_rate+=i[-2]
        day[i[2]]+=1
        hour[i[3]]+=1
        if i[0] in order_prior:
            order=order_prior[i[0]]
            avg_length+=len(order)
            for j in order:
                aisle[j[0]-1]+=1
                dep[j[1]-1]+=1
    avg_rate=avg_rate/len(l)
    avg_length=avg_length/len(l)
    for i in l:i.append(abs(i[-2]-avg_rate))                        #i[-1] will be av predicted day 
    hour=[float(x)/sum(hour)*100 for x in hour]
    day=[float(x)/sum(day)*100 for x in day]
    dep=[float(x)/sum(dep)*100 for x in dep]
    aisle=[float(x)/sum(aisle)*100 for x in aisle]
    user_props[user]=[avg_rate,avg_length,dep,aisle,hour,day]

order_props={}
final_features=[]

for user in d_prior:
    ls=d_prior[user]
    test=d_last_prior[user]
    num_orders=len(d_prior[user])
    products={}
    day=[0 for j in range(7)]
    hour=[0 for j in range(24)]
    day[test[2]]+=1
    hour[test[3]]+=1
    for i in ls:
        if i[0] in order_prior:
            order=order_prior[i[0]]
            for j in order:
                if j[-1] not in products:products[j[-1]]=[1,j[2],i[-3],1000,i[-3]]      #(no. of times bought,cart number,last bought,total interval sums,helper variable)
                else:
                    l=products[j[-1]]
                    l[0]+=1
                    l[1]+=j[2]
                    l[2]=i[-3]
                    l[-1]=i[-3]-l[-1] #l[-1] represents last jab khareeda tha tabse kitne din ho gaye h
                    if l[-2]==1000:l[-2]=l[-1]
                    else:l[-2]+=l[-1]
                    products[j[-1]]=l   
            for x in products:
                # days=1000
                avgDays=1000
                if products[x][0]>1:
                    avgDays=products[x][3]/(products[x][0]-1)
                    # days=products[x][-1]
                # products[x]=[(float(products[x][0])/num_orders)*100,float(products[x][1])/products[x][0],days,avgDays,products[x][2]]
                products[x]=[(float(products[x][0])/num_orders)*100,float(products[x][1])/products[x][0],avgDays,products[x][2]]
                # products[x]=[%age orders, avg cart no, ,avg interval b/w particular orders]
            for j in order:
                dep=[0 for x in range(21)]
                aisle=[0 for x in range(134)]
                dep[j[1]-1]+=1
                aisle[j[0]-1]+=1
                feature=[test[0],user,user_props[user][0],i[-1],abs(test[-3]-products[j[-1]][-1]-products[j[-1]][-2])]+products[j[-1]][:2]+day+hour+dep+aisle+[user_props[user][2][j[1]-1]]+[user_props[user][3][j[0]-1]]+[user_props[user][4][i[2]]]+[user_props[user][5][i[3]]]
                        #order_id,user_id,average interval length of buying,prediction for next bought in general ,prediction for next bought day for that product,% bought by user,avg cart no.,day,hr,dep,aisle,dep%,aisle%,day%,hr%
                final_features.append(feature)  #wait add class variable before appending


with open('train_data.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(final_features) 