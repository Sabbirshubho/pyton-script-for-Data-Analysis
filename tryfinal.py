# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 08:37:34 2020

@author: sash
"""


import pandas as pd
import numpy as np


df = pd.read_excel (r'C:\Users\sash\Downloads\Article Consumption Details_RAFI Oct 2020 OHNE Autom.xlsx', sheet_name='Article Consumption Supplier Fo')
df1 = pd.read_excel (r'C:\Users\sash\Desktop\orderlist\MOQ.xlsx')

#total= df[['Our stockcode', 'Day', 'Quantity']]


df1['MOQ'] = df1['MOQ'].fillna(0)
row_num = df.shape[0]
uniqueStockCode = list(df['Our stockcode'].unique())



lists = []
lists_missing=[]
#print(len(df))

for i in uniqueStockCode:
    try:                   # which are in lists
        index = np.where(df1['IXXAT Nr.'] == i)[0][0]
        MOQ = df1['MOQ'][index]
        count_stockcode = 0
        d=[]
        for j in range(len(df)):
            # print ("from outside of condition j is:")
            # print (j)
            
            if i == df['Our stockcode'][j]:
                b=0
                # print("from inside j is:")
                # print (j)
                count_stockcode = count_stockcode + int(df['Quantity'][j])
                # print(i)
                # print(count_stockcode)
                your_stockcode = df['Your stockcode'][j]
                day = df['Day'][j]
                d.append(day)
                #print(d)
            
            if  MOQ == 0:
                stock = {}
                stock['Your stockcode'] = your_stockcode
                stock['Our stockcode'] = i
                stock['Date'] = d[0]
                stock['Quant'] = count_stockcode
                lists.append(stock)
                
                d=[]
               
            
            if count_stockcode >= MOQ:
                stock = {}
                stock['Your stockcode'] = your_stockcode
                stock['Our stockcode'] = i
                stock['Date'] = d[0]
                stock['Quant'] = MOQ
                lists.append(stock)
                d_copy = d
                d=[]
                count_stockcode = count_stockcode - MOQ
                
            if j == (len(df) -1):
                if count_stockcode > 0 :
                    # print(count_stockcode)
                    stock = {}
                    stock['Your stockcode'] = your_stockcode
                    stock['Our stockcode'] = i
                    try:
                        stock['Date'] = d[0]
                    except:
                        stock['Date'] = d_copy[len(d_copy) -1]
                    stock['Quant'] = count_stockcode
                    lists.append(stock)             
                
                        
            
          


    except :
        print(i, 'not available')
        count_stock = 0
        for j in range(len(df)):
            if i == df['Our stockcode'][j]:
                count_stock = int(df['Quantity'][j])
                your_stockcode = df['Your stockcode'][j]
                day = df['Day'][j]
                stock_missing={}
           
                stock_missing['Your stockcode'] = your_stockcode
                stock_missing['Our stockcode'] = i
                stock_missing['Date'] = day
                stock_missing['Quant']=count_stock
                lists_missing.append(stock_missing)
        



list_main=lists+lists_missing
       

df = pd.DataFrame(list_main)
#print(df)
df['Date'] =pd.to_datetime(df.Date)
df['Date'] = df['Date'].dt.strftime('%Y/%m/%d')

df.to_excel("Article Consumption Details_RAFI Oct 2020 OHNE Autom  modify.xlsx", sheet_name='Article Consumption Supplier Fo', index=False) 