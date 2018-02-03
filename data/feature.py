import csv
import pandas as pd
import numpy as np
import datetime

order_products_train_df = pd.read_csv("order_products__train.csv")
order_products_prior_df = pd.read_csv("order_products__prior.csv")
orders_df = pd.read_csv("orders.csv")
products_df = pd.read_csv("products.csv")
# aisles_df = pd.read_csv("aisles.csv")
# departments_df = pd.read_csv("departments.csv")
print "read all files"
order_products_prior_df = pd.merge(order_products_prior_df, products_df, on='product_id', how='left')
order_products_prior_df=pd.merge(orders_df,order_products_prior_df,on="order_id",how='left').sort('user_id')
print "merging complete"
id=1
user_prod={}
prods={}
totalDays=0
prods1={}
for index, row in order_products_prior_df.iterrows():
	if index%10000==0: print index
	if row['user_id']!=id:
		for i in user_prod:
			l=user_prod[i]
			if len(l)>1:
				n=len(l)
				nl=[0 for i in range(n-1)]
				s=0
				for i in range(1,n):
					x=l[i]-l[i-1]
					nl[i]=x
					s+=x
				if i in prods:prods[i]=[prods[i][0]+s,prods[i][1]+n-1]
				else:prods[i]=[s,n-1]
				if i not in prods1:prods1[i]=[[i,1] for i in nl]
				else:
					l2=prods1[i]
					l3=[[i,1] for i in nl]
					if len(nl)>len(l2):
						for j in range(len(l2)):
							l3[j]=[l3[j][0]+l2[j][0],1+l2[j][1]]
						prods1[i]=l3
					else:
						for j in range(len(l3)):
							l2[j]=[l3[j][0]+l2[j][0],1+l2[j][1]]
						prods1[i]=l2
		user_prod={}
		totalDays=row['days_since_prior_order']
		user_prod[row['product_id']]=[totalDays]
	else:
		totalDays+=row['days_since_prior_order']
		if row['product_id'] not in user_prod:user_prod[row['product_id']]=[totalDays]
		else:user_prod[row['product_id']].append(totalDays)
temp=[]
for i in prods:
	avg=float(prods[i][0])/prods[i[1]]
	avgs=[float(x[0])/x[1] for x in prods1[i]]
	avgs.append(avg)
	temp.append([i]+avgs)
	if len(temp)>1000:
		with open('feature.csv', 'ab') as file:
			writer = csv.writer(file)
			writer.writerows(temp)
		temp=[]
if len(temp)>0:
	with open('feature.csv', 'ab') as file:
			writer = csv.writer(file)
			writer.writerows(temp)