#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 23:32:10 2020

@author: marlowcj
"""
import os
import sys
import matplotlib.pyplot as plt
import matplotlib
import mpl_toolkits
import numpy as np
import cartopy
from scipy import spatial
import difflib

debug = False

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5.mpltools import mplDefaults as mpld

def get_closest_name_rgb(rgb):
    '''
    This function takes in an rgb value and returns the closest named color
    that is in the mpld.namecolorsNAMElookup dictionary
    '''
    rgblist = list(mpld.RGBtoName.keys())
    tree = spatial.KDTree(rgblist)
    idx = tree.query(rgb)[-1]
    color = tuple(rgblist[idx])
    name = mpld.RGBtoName[color]
    return name

def get_closest_name_name(name):
    '''
    This function takes in a named color and checks to see if it is in the matplotlib
    names that I have rgb values for.  If it is it gets returned, else a best match
    is done with fuzzy string logic.  If that fails... just return red.
    '''
    if name in mpld.NametoRGB:
        return name
    bestmatch = difflib.get_close_matches(name, list(mpld.NametoRGB.keys()))
    if bestmatch:
        return bestmatch[0]
    else:
        return 'r'
    
def convert_hex_to_rgb(hexval):
    '''
    This function takes in a hexval color fmt: #ff00ff and returns the rgb value
    like matplotlib wants it (normalized to 1) - (1,0,1).
    '''
    hexval = hexval.strip('#')
    rgb = tuple(int(hexval[i:i+2], 16) for i in (0, 2, 4))
    #normalize to 1
    rgb = np.array(rgb)/255
    return tuple(rgb)
    
def get_compliment_rgb(rgb,**kwargs):
    '''
    Takes an rgb value and finds its compliment... returns a matplotlib color name by default
    '''
    
    get_rgb = kwargs.get('get_rgb',False)
    if not isinstance(rgb,(list,tuple)):
        return rgb
    r,g,b = rgb
    if isinstance(r,int) and isinstance(g,int) and isinstance(b,int) and (r>1 or g>1 or b>1):
        norm = 255
    else:
        norm = 1
    nr = np.abs(r-norm)
    ng = np.abs(g-norm)
    nb = np.abs(b-norm)
    if get_rgb:
        return tuple([nr,ng,nb])
    if tuple([nr,ng,nb]) in mpld.RGBtoName:
        return mpld.RGBtoName[tuple([nr,ng,nb])]
    rgblist = list(mpld.RGBtoName.keys())
    tree = spatial.KDTree(rgblist)
    idx = tree.query(np.array([nr,ng,nb])/norm)[1]
    color = tuple(rgblist[idx])
    name = mpld.RGBtoName[color]
    return name

def determineMarker(lineObj):
    '''
    Function takes in a line object from axes.properties()['children'],
    but specifically this object must be a path.PathCollection (or scatter plot).
    Since the markers are stored as class instances, we need to compare them with
    extracted values.
    Input:
        lineObj - path.PathCollection object
    Kwargs:
        N/A
    Return:
        Returns the marker type of a scatter plot.  If it cannot be discerned 'o' will
        be returned
    '''
    arr = lineObj.get_paths()[0].vertices
    for symb in mpld.marker_to_array:
        if not arr.shape == mpld.marker_to_array[symb].shape:
            continue
        idx = np.allclose(mpld.marker_to_array[symb],arr)
        if idx :
            return symb
    return 'o'

def getTickLabels(axesobj,axes):
    '''
    This will look at an axes ticklabels and return the list of normal string values
    
    Input:
        axesobj - Matpltolib axes object
        axes - either 'x' or 'y' for x or y ticklabels
    Kwargs:
        N/A
        
    '''
    textobjs = eval(f'axesobj.get_{axes}ticklabels()')
    labels = []
    rt = False
    for t in textobjs:
        labels.append(t._text)
    for label in labels:
        if label:
            rt = True
            break
    if rt:
        return labels
    else:
        return []
    
def getAxid(geometry):
    '''
    This function takes an Axes geometry, which is found in the 
    axes.properties()['geometry']
    and returns the gridspec Id in terms that Plotterator stores it's axid
    
    Input:
        geometry - axes.properties()['geometry'] tuple
    Kwargs:
        N/A
    Returns:
        The row and column in which the plot should be located in a Plotterator fig.
    '''
    rows = geometry[0]
    cols = geometry[1]
    pos = geometry[2]
    npos = pos
    j = 0
    while npos > cols:
        npos = npos - cols
        j+=1
    else:
        npos = npos - cols
        j+=1
    row = j-1
    col = npos + cols - 1
    return (row,col)

def getSpan(subgridspec,geometry):
    '''
    Finds the span of an axes in a figure
    Input:
        subgridspec - subgridspec value in the axes properties dict
        geometry - the geometry value in the axes properties dict
    Kwargs:
        N/A
    Return:
        Returns the tuple of (rowspan,colspan)
    '''
    rows = geometry[0]
    cols = geometry[1]
    start = subgridspec.num1+1
    end = subgridspec.num2+1
    s = getAxid([rows,cols,start])
    e = getAxid([rows,cols,end])
    return tuple(np.array(e)-np.array(s)+1)

def getGetsandSets(obj):
    '''
    This function finds the set and get functions of a matplotlib object.
    Returns a dictionary of the get command with the set command
    
    Input:
        obj - matplotlib object
    Kwargs:
        N/A
    Return:
        Returns a dictionary with keys as the gets and values as the set 
    '''
    sets = []
    attrdict = {}
    for o in dir(obj):
        if o.startswith('_set') or o.startswith('set'):
            if 'set_data' in o:
                continue
            if '_setstate' in o:
                continue
            if 'set_paths' in o:
                continue
            if o == 'set':
                continue
            sets.append(o)
    for s in sets:
        for o in dir(obj):
            if s.startswith('_set'):
                checkstr = s.split('_set_')[-1]
            elif s.startswith('set'):
                checkstr = s.split('set_')[-1]
            if o.startswith('_get'):
                checkdir = o.split('_get_')[-1]
            elif o.startswith('get'):
                checkdir = o.split('get_')[-1]
            else:
                checkdir = o
            if checkdir == checkstr:
                attrdict[o] = s
            
            # Stupid special cases that I've noticed
            # For wedges
            if o == 'r' and checkstr == 'radius':
                attrdict[o] = s
    return attrdict
                
def has_twin(ax):
    '''
    Currently just tells if there is a twin or not..  Doesn't tell x or y.
    
    Loops over the axes in the figure and sees if the bounding box of the passed
    axes is equivalent to any of the other axes.  If so, I'm assuming that they are
    twinned.
    Input:
        ax - Matplotlib axes to check whether it has a twin
    Kwargs:
        N/A
    Return:
        Return [True,False]
    '''
    for other_ax in ax.figure.axes:
        if other_ax is ax:
            continue
        if other_ax.bbox.bounds == ax.bbox.bounds:
            return True
    return False

def determineAxesType(axes):
    '''
    This function takes in a matplotlib axes object.  Determines the type of axes
    that it is.
    
    Input:
        axes - Matpotlib axes object
    Kwargs:
        N/A
    Returns:
        Returns a string based off the axes type.
        3D - A 3D axes
        geo - a cartopy axes
        normal - neither of the other two
    '''
    if '3D' in str(type(axes)):
        return '3D'
    elif isinstance(axes,cartopy.mpl.geoaxes.GeoAxesSubplot):
        return 'geo'
    else:
        return 'normal'
    
def parseCartopyTransform(child):
    '''
    This should only get called if mapplot = True, thus the following
    code should work, however, I have noticed that some objects don't have
    a _a.source_projection attribute.
    
    Input:
        child - A child from an axes.properties()['children'] list
        
    Kwargs:
        N/A
    
    Return:
        Returns the string of the cartopy projection in a way plotterator wants it.
        Returns PlateCarree if it cannot be discerned
    '''
    
    try:
        proj = str(type(child._transform._a.source_projection)).split(' object')[0]
        proj = proj.split('.')[-1][:-2]+'()'
        return proj
    except:
        return 'PlateCarree()'
    
def parseAxesCartopyTransform(axes):
    '''
    This function gets the axes cartopy transform and puts it in a format that
    Plotterator wants.
    
    Input:
        axes - a matplotlib axes object
    Kwargs:
        N/A
    Return:
        Returns the string of the cartopy projection in a way plotterator wants it.
        Returns PlateCarree if it cannot discern
    '''
    
    try:
        proj = str(type(axes.projection))
        if 'cartopy.crs' in proj:
            proj = proj.split('.')[-1]
            proj = f'{proj}()'
            return proj
        else:
            return 'PlateCarree()'
    except:
        return 'PlateCarree()'
    