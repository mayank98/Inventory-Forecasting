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
print "read all files"

order_products_prior_df = pd.merge(order_products_prior_df, products_df, on='product_id', how='left')
order_products_train_df = pd.merge(order_products_train_df, products_df, on='product_id', how='left')
print "merging complete"
products_df = None
d_prior = {}
d_last_prior = {}
id = 1
pl = []
totalDays = 0
id_train = {}
id_test = {}
# additional features
product_reorder_pct_byProduct = {}  # 4 apples reordered out of 10 apples bought == 40%
product_reorder_pct_overall = {}  # 4 apples reordered out of 100 products bought == 4%
product_bought_pct_overall = {}  # 8 apples ordered out of 100 products bought == 8%
dep_pct_overall = {}
aisle_pct_overall = {}
depNaisle_pct_overall = {}

tot=len(order_products_prior_df['reordered'])+len(order_products_train_df['reordered'])
for i in range(49688):
    p=order_products_prior_df['reordered'][order_products_prior_df['product_id']==i+1].value_counts()
    t=order_products_train_df['reordered'][order_products_train_df['product_id']==i+1].value_counts()
    num0=p[0]+t[0]
    num1=p[1]+t[1]
    product_reorder_pct_byProduct[i+1]=(float(num1)/(num0+num1))*100
    product_reorder_pct_overall[i+1]=(float(num1)/tot)*100
    product_bought_pct_overall[i+1]=(float(num0+num1)/tot)*100

for i in range(21):
    p=len(order_products_prior_df[order_products_prior_df['department_id']==i+1])
    t=len(order_products_train_df[order_products_train_df['department_id']==i+1])
    dep_pct_overall[i+1]=(float(p+t)/tot)*100

for i in range(134):
    p=len(order_products_prior_df[order_products_prior_df['aisle_id']==i+1])
    t=len(order_products_train_df[order_products_train_df['aisle_id']==i+1])
    aisle_pct_overall[i+1]=(float(p+t)/tot)*100

for dep in range(21):
    for aisle in range(134):
        p = len(order_products_prior_df[order_products_prior_df['department_id']==dep+1][order_products_prior_df['aisle_id']==aisle+1])
        t = len(order_products_train_df[order_products_train_df['department_id']==dep+1][order_products_train_df['aisle_id']==aisle+1])
        depNaisle_pct_overall[i + 1] = (float(p + t) / tot) * 100

for index, row in orders_df.iterrows():
    # print index
    #   if index>10000:break
    if row['user_id'] != id:
        if pl[-1][-1] == "test":
            for i in pl[:-1]: id_train[i[0]] = 1
            id_test[pl[-1][0]] = 1
            d_prior[id] = pl[:-1]
            d_last_prior[id] = pl[-1]
        pl = []
        totalDays = 0
        # if totalDays==None:totalDays
        id = row['user_id']
        days_since_prior_order = 0
        # if row['days_since_prior_order']==None:days_since_prior_order=totalDays/row['order_number']
        pl.append([row['order_id'], row['order_number'], row['order_dow'], row['order_hour_of_day'], totalDays,
                   days_since_prior_order, row['eval_set']])
    else:
        totalDays += row["days_since_prior_order"]
        days_since_prior_order = row['days_since_prior_order']
        # if row['days_since_prior_order']==None:days_since_prior_order=totalDays/row['order_number']
        pl.append([row['order_id'], row['order_number'], row['order_dow'], row['order_hour_of_day'], totalDays,
                   days_since_prior_order, row['eval_set']])
if pl[-1][-1] == "test":
    d_prior[id] = pl[:-1]
    # id_train[pl[0][0]]=1
    for i in pl: id_train[i[0]] = 1
    id_test[pl[-1][0]] = 1
    d_last_prior[id] = pl[-1]
print len(d_prior), len(d_last_prior)
print sum([len(d_prior[x]) for x in d_prior])
del order_products_train_df
order_prior = {}
order_prior_last_id = {}
order_length = {}
id = 2
l = []
for index, row in order_products_prior_df.iterrows():
    if (index % (1000000) == 0): print index, "order"
    if row['order_id'] in id_test:
        order_prior_last_id[(row['order_id'], row['product_id'])] = 1
    # if index>1000000:break
    if row['order_id'] in id_train:
        if row['order_id'] not in order_length:
            order_length[row['order_id']] = 1
        else:
            order_length[row['order_id']] += 1
        if row['order_id'] != id:
            order_prior[id] = l
            id = row['order_id']
            l = [[row['aisle_id'], row['department_id'], row['add_to_cart_order'], row['reordered'], row['product_id']]]
        else:
            l.append([row['aisle_id'], row['department_id'], row['add_to_cart_order'], row['reordered'], row['product_id']])
if id not in order_prior: order_prior[id] = l
print len(order_prior)
del orders_df
del order_products_prior_df
user_props = {}
cc = 0
for user in d_prior:
    avg_rate, avg_length = 0, 0
    l = d_prior[user]
    flag = False
    dep = [0 for i in range(21)]
    aisle = [0 for i in range(134)]
    day = [0 for i in range(7)]
    hour = [0 for i in range(24)]
    for i in l:
        avg_rate += i[-2]
        day[i[2]] += 1
        hour[i[3]] += 1
        if i[0] in order_prior:
            flag = True
            order = order_prior[i[0]]
            avg_length += order_length[i[0]]
            for j in order:
                aisle[j[0] - 1] += 1
                dep[j[1] - 1] += 1
    avg_rate = avg_rate / (len(l) - 1)
    avg_length = avg_length / len(l)
    for i in l: i.append(abs(i[-2] - avg_rate))  # i[-1] will be av predicted day
    if (flag):
        hour = [float(x) / sum(hour) * 100 for x in hour]
        day = [float(x) / sum(day) * 100 for x in day]
        dep = [float(x) / sum(dep) * 100 for x in dep]
        aisle = [float(x) / sum(aisle) * 100 for x in aisle]
    else:
        cc += 1
    user_props[user] = [avg_rate, avg_length, dep, aisle, hour, day]

order_props = {}
# final_features=[]
tt = 0
cl = 0
temp = []
for user in d_prior:
    ls = d_prior[user]
    test = d_last_prior[user]

    num_orders = len(d_prior[user])
    products = {}
    day = [0 for j in range(7)]
    hour = [0 for j in range(24)]
    day[test[2]] += 1
    hour[test[3]] += 1
    marked = {}
    reordered = {}
    for i in ls:
        if i[0] in order_prior:  # hoga hi ,always true if running for the full file
            order = order_prior[i[0]]
            for j in order:
                if j[-1] not in reordered:
                    reordered[j[-1]] = j[-2]
                else:
                    reordered[j[-1]] += j[-2]
                if j[-1] not in products:
                    products[j[-1]] = [1, j[2], i[-3], 1000, i[-3]]
                    # (no. of times bought,cart number,last bought,total interval sums,helper variable)
                else:
                    l = products[j[-1]]
                    l[0] += 1
                    l[1] += j[2]
                    l[2] = i[-3]
                    l[-1] = i[-3] - l[-1]  # l[-1] represents last jab khareeda tha tabse kitne din ho gaye h
                    if l[-2] == 1000:
                        l[-2] = l[-1]
                    else:
                        l[-2] += l[-1]
                    products[j[-1]] = l
    for x in reordered:
        reordered[x] = (float(reordered[x]) / num_orders) * 100
    for x in products:
        # days=1000
        avgDays = 1000
        if products[x][0] > 1:
            avgDays = products[x][3] / (products[x][0] - 1)
            # days=products[x][-1]
        # products[x]=[(float(products[x][0])/num_orders)*100,float(products[x][1])/products[x][0],days,avgDays,products[x][2]]
        products[x] = [(float(products[x][0]) / num_orders) * 100, float(products[x][1]) / products[x][0], avgDays,
                       products[x][2]]
        # products[x]=[%age orders, avg cart no, ,avg interval b/w particular orders]
    for i in ls:
        if i[0] in order_prior:  # hoga hi ,always true if running for the full file
            order = order_prior[i[0]]
            for j in order:
                if j[-1] not in marked:
                    marked[j[-1]] = 1
                    print "test,", test
                    print "i=,", i
                    print "j=", j
                    dep = [0 for x in range(21)]
                    aisle = [0 for x in range(134)]
                    dep[j[1] - 1] += 1
                    aisle[j[0] - 1] += 1
                    class1 = 0
                    if (test[0], j[-1]) in order_prior_last_id: class1 = 1
                    feature = [test[0], user, j[-1], user_props[user][1], i[-1],
                               abs(test[-3] - products[j[-1]][-1] - products[j[-1]][-2]), reordered[j[-1]]] + [
                                  products[j[-1]][1]] + day + hour + dep + aisle + [user_props[user][2][j[1] - 1]] + [
                                  user_props[user][3][j[0] - 1]] + [user_props[user][4][test[3]]] + [
                                  user_props[user][5][test[2]]] + [class1]
                    # order_id,user_id,product_id,average interval length of buying,prediction for next bought in general ,prediction for next bought day for that product,% bought by user,avg cart no.,day,hr,dep,aisle,dep%,aisle%,day%,hr%
                    # final_features.append(feature)    #wait add class variable before appending
                    print "iter-", tt, cl
                    tt += 1
                    if class1 == 1: cl += 1
                    temp.append(feature)
                    if len(temp) > 500:
                        with open('test_data.csv', 'ab') as file:
                            writer = csv.writer(file)
                            writer.writerows(temp)
                        temp = []

print "fuck", cc, "Ratio of products with label 1=", float(cl) / tt

if len(temp) > 0:
    with open('test_data.csv', 'ab') as file:
        writer = csv.writer(file)
        writer.writerows(temp)
    temp = []