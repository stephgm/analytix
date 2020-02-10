def NestedDict_fromDF(iDF,keyorder,values):
    '''
    This function takes a dataframe, rearranges it based on the keyorder and
    spits out a nested dictionary that contains a dataframe of the values
    you want.
    
    Input:
        iDF - The dataframe that you want to rearrange
        keyorder - a list or string of column names in the dataframe.  These are
                    set as the index of the dataframe, essentially a groupby
        values - a list or string of column names in the dataframe that you want
                the values of the dictionary to contain
    Kwargs:
        N/A
    Return:
        Returns a nested dictionary with the keys pertaining to the unique
        values of the columns in keyorder, whos values correspond to the values
    '''
    if not isinstance(keyorder,list):
        keyorder = [keyorder]
    if not isinstance(values,list):
        values = [values]
    for i in reversed(range(len(keyorder))):
        if keyorder[i] not in iDF:
            keyorder.pop(i)
    for i in reversed(range(len(values))):
        if values[i] not in iDF:
            values.pop(i)
    rdict = {}
    if not isinstance(iDF,pd.DataFrame):
        return rdict
    if keyorder:
        ndf = iDF.set_index(keyorder)
        def makeDict(basedict,group):
            for k,g in group:
                basedict[k] = {}
                try:
                    makeDict(basedict[k], g.droplevel(0).groupby(level=0))
                except:
                    if values:
                        basedict[k] = g[values].reset_index(drop=True)
                    else:
                        basedict[k] = []
            return basedict
        rdict = makeDict({}, ndf.groupby(level=0))
    return rdict
