import pandas as pd
import numpy as np

lowsample = {'ltime':[1,5,10],'id':[0,1,2]}
highsample = {'htime':np.linspace(0,11,100),'hsample':np.random.randint(0,100,100)}

l = pd.DataFrame(lowsample)
h = pd.DataFrame(highsample)

def timealign(df1,df2,df1time,df2time,**kwargs):
    dropNAN = kwargs.get('dropNan',False)
    df1.set_index(df1time,inplace=True)
    df2.set_index(df2time,inplace=True)
    if df1.shape[0] > df2.shape[0]:
        left = df1
        right = df2
        timefld = df1time
    else:
        left = df2
        right = df1
        timefld = df2time
    left = left.join(right, how='outer')
    left.fillna(method='ffill',inplace=True)
    left = left.reset_index().rename(columns={'index':timefld})
    if dropNAN:
        left.dropna(inplace=True)
    return left

x = timealign(l,h,'ltime','htime',dropNan=True)
