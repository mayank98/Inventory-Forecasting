import pandas as pd
import csv

order_products_prior=pd.read_csv('data/order_products__prior.csv')
order_products_train=pd.read_csv('data/order_products__train.csv')
orders=pd.read_csv('data/orders.csv')

order_prior={}
order_train={}

for index,row in order_products_prior.iterrows():
    id=row['order_id']
    if index%10000==0: print "inside order_products_prior", index
    if id not in order_prior:
        order_prior[id]=[str(row['product_id'])]
    else:
        order_prior[id].append(str(row['product_id']))

for index,row in order_products_train.iterrows():
    id=row['order_id']
    if index % 10000 == 0: print "inside order_products_train", index
    if id not in order_train:
        order_train[id]=[str(row['product_id'])]
    else:
        order_train[id].append(str(row['product_id']))

id=1
pl=[]
user_products_prior={}
user_products_train={}

for index,row in orders.iterrows():
    if index % 10000 == 0: print "inside orders_df", index
    if row['user_id']!=id:
        if pl[-1][2]=='train':
            user_products_train[id]=order_train[pl[-1][0]]
            a=set()
            for order in pl[-5:-1]:
                orderID=order[0]
                b=set(order_prior[orderID])
                a=a.union(b)
            user_products_prior[id]=a
        id=row['user_id']
        pl=[[row['order_id'],row['user_id'],row['eval_set']]]
    else:
        pl.append([row['order_id'],row['user_id'],row['eval_set']])
# edge case
if pl[-1][2]=='train':
    user_products_train[id]=order_train[pl[-1][0]]
    a=set()
    for order in pl[-5:-1]:
        orderID=order[0]
        b=set(order_prior[orderID])
        a=a.union(b)
    user_products_prior[id]=a
del order_prior

i=1
temp=[]
for id1 in user_products_prior:
    print id1,i,"iterations done"
    i+=1
    a=len(user_products_prior[id1])
    ls=[]
    for id2 in user_products_prior:
        if id1==id2:
            continue
        b=len(user_products_prior[id2])
        c=len(user_products_prior[id1].intersection(user_products_prior[id2]))
        # x=float(c)/a
        # y=float(c)/b
        # HM=2*x*y/(x+y) # equal to 2*c/(a+b)
        HM=2*float(c)/(a+b)
        ls.append([HM,id2])
    # l=[user_products_train[x[1]] for x in sorted(ls[-5:])]
    l=[]
    for x in sorted(ls[-5:]):
        ls1=[]
        A=user_products_prior[id1].intersection(user_products_prior[x[1]])
        for y in user_products_train[x[1]]:
            ls1.append(y)
            ls1.append(y in A)
        l.append(ls1)
    l = [" ".join(a) for a in l]
    temp.append([id1] + l)
    if len(temp)>500:
        with open('correlation.csv', 'ab') as file:
            writer = csv.writer(file)
            writer.writerows(temp)
        temp=[]