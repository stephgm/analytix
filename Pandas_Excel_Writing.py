#An example in how to color cells with pandas xlsx writer....  Conditional statements and everything.
import pandas as pd
truth = {'TrackId':[1,2,3,4,5,5]}
track = {'TrackId':[1,2,3,4,6,7,8,11,0,10],
         'Type':['Puppy','Doggy','Tnak','TV','Fun','Hank','tank','pid','Unicorn','pid'],
         'Type2':[5,55,555,5555,55555,555555,5555555,55555555,555555555,55555555555]}

Truth = pd.DataFrame(truth)
Track = pd.DataFrame(track)

#result = Truth.join(Track,on='TrackId',how='left')
Truth['Type'] = Truth['TrackId'].map(Track.set_index('TrackId')['Type']).fillna('UNK')

def color_strings(val):
    if isinstance(val,str):
        if val.startswith('Do'):
            color = 'red'
        elif val.lower().startswith('p'):
            color = 'green'
        elif 'ank' in val:
            color = 'blue'
        else:
            color = 'blue'
    else:
        color = 'black'
    return 'color: %s' % color

def highlight_cell(val):
    if isinstance(val,str):
        if val.startswith('U'):
            color = 'green'
        else: color = 'white'
    else:
        color = 'red'
    return 'background-color: {}'.format(color)

Truth = Truth.style.applymap(color_strings).applymap(highlight_cell)
Truth.to_excel('That.xlsx')

#Need to make a legend?
#Just color the values with a legend function.  
another_df = pd.DataFrame()
another_df['Legend'] = pd.Series(['Starts with U','If Value is Number'])
another_df.to_excel(writer,startrow=0, startcol=Truth.shape[1]+5) 
