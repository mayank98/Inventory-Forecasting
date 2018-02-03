import pandas as pd

order_products_prior=pd.read_csv('data/order_products__prior.csv')
order_products_train=pd.read_csv('data/order_products__train.csv')
orders=pd.read_csv('data/orders.csv')

order_prior={}
order_train={}

for row in order_products_prior.iterrows():
    id=row['order_id']
    if id not in order_prior:
        order_prior[id]=[str(row['product_id'])]
    else:
        order_prior[id].append(str(row['product_id']))

for row in order_products_train.iterrows():
    id=row['order_id']
    if id not in order_train:
        order_train[id]=[row['product_id']]
    else:
        order_train[id].append(row['product_id'])

id=1
pl=[]
user_products_prior={}
user_products_train={}

for row in orders.iterrows():
    if row['user_id']!=id:
        if pl[-1][2]=='train':
            user_products_train[id]=order_train[pl[-1][0]]
            a=set()
            for orderID in pl[-5:-1][0]:
                b=set(order_prior[orderID])
                a=a.union(b)
            user_products_prior[id]=a
        id=row['user_id']
        pl=[[row['order_id'],row['user_id'],row['eval_set']]]
    else:
        pl.append([row['order_id'],row['user_id'],row['eval_set']])

temp=[]
for id1 in user_products_prior:
    similar=[]
    for id2 in user_products_prior:
        if id1==id2: continue
        a=len(user_products_prior[id1])
        b=len(user_products_prior[id2])
        c=len(user_products_prior[id1].intersection(user_products_prior[id2]))
        x=float(c)/a
        y=float(c)/b
        HM=2*x*y/(x+y) # equal to 2*c/(a+b)
        similar.append([HM,id2])
    l=[order_train[x[1]] for x in sorted(similar[-5:])]
    l=[" ".join(a) for a in l]
    temp.append([id1]+l)
    if len(temp)>500:
        with open('correlation.csv', 'ab') as file:
                writer = csv.writer(file)
                writer.writerows(temp)
        temp=[]