import csv
import pandas as pd
from math import isnan

order_products_train_df = pd.read_csv("data/order_products__train.csv")
order_products_prior_df = pd.read_csv("data/order_products__prior.csv")
orders_df = pd.read_csv("data/orders.csv")
products_df = pd.read_csv("data/products.csv")
# aisles_df = pd.read_csv("data/aisles.csv")
# departments_df = pd.read_csv("data/departments.csv")
print "read all files"

order_products_prior_df = pd.merge(order_products_prior_df, products_df, on='product_id', how='left')
order_products_train_df = pd.merge(order_products_train_df, products_df, on='product_id', how='left')

print "merging complete"
del products_df

d_prior = {}
d_last_prior = {}
avg_prior_features={}
id = 1
pl = []
totalDays = 0
id_train = {}
id_test = {}

for index, row in orders_df.iterrows():
    if index % 10000 == 0: print index, "order"
    if row['user_id'] != id:
        if pl[-1][-1] == "train":
            for i in pl[:-1]: id_train[i[0]] = 1
            id_test[pl[-1][0]] = 1
            d_prior[id] = pl[:-1]
            d_last_prior[id] = pl[-1]
        pl = []
        totalDays = 0
        id = row['user_id']
        days_since_prior_order = 0
        pl.append([row['order_id'], row['order_number'], row['order_dow'], row['order_hour_of_day'], totalDays,
                   days_since_prior_order, row['eval_set']])
    else:
        days_since_prior_order = row['days_since_prior_order']
        if isnan(days_since_prior_order):
            days_since_prior_order=0
        totalDays += days_since_prior_order
        pl.append([row['order_id'], row['order_number'], row['order_dow'], row['order_hour_of_day'], totalDays,
                   days_since_prior_order, row['eval_set']])
if pl[-1][-1] == "train":
    for i in pl[:-1]: id_train[i[0]] = 1
    id_test[pl[-1][0]] = 1
    d_prior[id] = pl[:-1]
    d_last_prior[id] = pl[-1]

del orders_df
print len(d_prior), len(d_last_prior)
print sum([len(d_prior[x]) for x in d_prior])

order_products={}
order_train={}
l=[]
id=1

print "iterating order_products_train 14,00,000"
for index, row in order_products_train_df.iterrows():
    if index % 100000 == 0: print index, "order"
    if row['order_id'] in id_test:
        if row['order_id'] != id:
            order_train[id] = l
            id = row['order_id']
            l = [[row['aisle_id'], row['department_id'], row['add_to_cart_order'], row['reordered'], row['product_id']]]
        else:
            l.append([row['aisle_id'], row['department_id'], row['add_to_cart_order'], row['reordered'], row['product_id']])
        if row['order_id'] in order_products:
            order_products[row['order_id']].append(row['product_id'])
        else:
            order_products[row['order_id']]=[row['product_id']]
if id not in order_train:
    order_train[id]=l
print "finished iterating order_products_train"

order_prior={}
l=[]
id=2

print "iterating order_products_prior 3,24,00,000"
for index, row in order_products_prior_df.iterrows():
    if index % 1000000 == 0: print index, "order"
    if row['order_id'] in id_train:
        if row['order_id'] != id:
            order_prior[id] = l
            id = row['order_id']
            l = [[row['aisle_id'], row['department_id'], row['add_to_cart_order'], row['reordered'], row['product_id']]]
        else:
            l.append([row['aisle_id'], row['department_id'], row['add_to_cart_order'], row['reordered'], row['product_id']])
        if row['order_id'] in order_products:
            order_products[row['order_id']].append(row['product_id'])
        else:
            order_products[row['order_id']]=[row['product_id']]
if id not in order_prior:
    order_prior[id]=l
print "finished iterating order_products_prior"

del order_products_train_df
del order_products_prior_df

# general features (for all users)
total_no_of_orders=len(order_prior)
times_reord={}  # key is product_id
times_bought={}  # key is product_id

for id in order_prior:
    for prod in order_prior[id]:
        if prod[-1] in times_bought:
            times_bought[prod[-1]]+=1
        else:
            times_bought[prod[-1]]=1
        if prod[-1] in times_reord:
            times_reord[prod[-1]]+=prod[-2]
        else:
            times_reord[prod[-1]]=prod[-2]

temp=[]
for user in d_prior:
    ls = d_prior[user]
    size=len(ls)
    test = d_last_prior[user]
    last_prior_products=set(order_products[test[0]])

    dow_percent=[0 for x in range(7)]
    hod_percent=[0 for x in range(24)]
    aisle_percent=[0 for x in range(134)]
    dep_percent=[0 for x in range(21)]

    prior_products=set()
    product={}
    cnt={}
    num_products_ordered=0

    for i in ls:
        prior_products=prior_products.union(set(order_products[i[0]]))  # i[0]=order_id
        dow_percent[i[2]-1]+=1
        hod_percent[i[3]-1]+=1
        num_products_ordered+=len(order_prior[i[0]])
        for prod in order_prior[i[0]]:
            product_id=prod[-1]
            aisle_percent[prod[0]-1]+=1
            dep_percent[prod[1]-1]+=1
            if product_id in product:
                product[product_id][-2]+=prod[-2]
                product[product_id][2]+=prod[2]
                cnt[product_id]+=1
            else:
                product[product_id]=prod
                cnt[product_id]=1

    reord_day=0  #reorders at that day
    reord_hr=0  #reorders at that hr
    for i in ls:
        if test[2]==i[2]:
            for prod in order_prior[i[0]]:
                reord_day+=prod[-2]
        if test[3]==i[3]:
            for prod in order_prior[i[0]]:
                reord_hr+=prod[-2]

    max_reord=0
    sum_reord=0
    for id in product:
        sum_reord+=product[id][-1]
        max_reord=max(max_reord,product[id][-2])
    for id in product:
        if product[id][-2]==max_reord: break

    f=[0]*17  # making a feature
    # {of this product ---> aisle_id,department_id,reorder_percentage,reorder_rate,aisle %age,department %age},
    # reorder length general,reorder rate general,% of reordered products at that day,
    # % of reordered products at that hr, no. of orders, no. of unique products,avg_cart_no of most reordered product,
    # no of products
    f[0]=product[id][0]
    f[1]=product[id][1]
    if sum_reord > 0:
        f[2]=float(max_reord*100)/sum_reord
        f[8]=float(reord_day*100)/sum_reord
        f[9]=float(reord_hr*100)/sum_reord
    f[3]=float(max_reord)/size
    f[4]=float(aisle_percent[product[id][0]-1]*100)/sum(aisle_percent)
    f[5]=float(dep_percent[product[id][1]-1]*100)/sum(dep_percent)
    f[6]=sum_reord/size
    f[7]=sum_reord/num_products_ordered
    f[10]=size
    f[11]=len(prior_products)
    f[12]=product[id][2]/cnt[id]
    f[13]=num_products_ordered
    if times_reord[id] > 0:
        f[14]=float(max_reord*100)/times_reord[id] # reorder %age overall
    f[15]=float(times_reord[id]*100)/times_bought[id] # reorder %age overall
    f[16]=times_reord[id]/total_no_of_orders # reorder rate overall

    tot=sum(dow_percent)
    dow_percent=[float(dow_percent[x])*100/tot for x in range(7)]
    tot=sum(hod_percent)
    hod_percent=[float(hod_percent[x])*100/tot for x in range(24)]

    none=0
    if len(prior_products.intersection(last_prior_products))==0:
        none=1

    temp_feature = [0, 0, 0, 0, 0]
    # avg_order_num,avg_day of week,avg_hour_of_day,avg_days_since_prior_order,avg_order_length
    for order in ls:
        temp_feature[0] += order[1]
        temp_feature[1] += order[2]
        temp_feature[2] += order[3]
        temp_feature[3] += order[5]
        temp_feature[4] += len(order_products[order[0]])
    temp_feature[0] /= size
    temp_feature[1] /= size
    temp_feature[2] /= size
    temp_feature[3] /= size
    temp_feature[4] /= size

    feature = [user]+test[:-1]+temp_feature+[dow_percent[test[2]-1],hod_percent[test[3]-1]]+f+[none]
    temp.append(feature)

    if len(temp) > 500:
        with open('train_data.csv', 'ab') as file:
            writer = csv.writer(file)
            writer.writerows(temp)
        temp = []

if len(temp) > 0:
    with open('train_data.csv', 'ab') as file:
        writer = csv.writer(file)
        writer.writerows(temp)
    temp = []