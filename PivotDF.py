import pandas as pd
import numpy as np

this = {'AOR':['Guam','Guam','Guam','Guam','Japan','Japan','USA','USA'],
        'Type':['PID','RV','Tank','PID','PID','RV','RV','Tank'],
        'SAE':['33_2_100','33_2_4','33_2_7','33_2_101','44_2_100','44_2_4','2_2_4','2_2_7']}

def THOSE(x):
    list(x)

y = pd.DataFrame(this)
xxxx = y[y['AOR']=='Guam']['SAE']
x = y.pivot_table(index=['AOR'],columns=['Type'],values=['SAE'],aggfunc=sum)
x.to_excel('this.xlsx')


def pivotDF(df,index,columns,values):
    tmpdict = {}
    if index not in df or columns not in df or values not in df:
        return df
    newindex = pd.unique(df[index])
    uniquecols = pd.unique(df[columns])
    for idx in newindex:
        tmpdict[idx] = {}
        for col in uniquecols:
            tmpdict[idx][col] = df[(df[columns]==col)&(df[index]==idx)][values].tolist()
    return pd.DataFrame(tmpdict)

xx = pivotDF(y,'AOR','Type','SAE')

jj = xx.to_dict()
