#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 00:46:41 2020

@author: Carl
"""

""" trying to parse out some matplotlib sheet... Figure to plotterator"""


import os
import sys
import matplotlib.pyplot as plt
import matplotlib
import mpl_toolkits
import numpy as np
import cartopy

debug = False

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5 import Plotterator



marker_to_array = {'.': np.array([[ 0.        , -0.25      ],
        [ 0.06630078, -0.25      ],
        [ 0.12989497, -0.22365842],
        [ 0.1767767 , -0.1767767 ],
        [ 0.22365842, -0.12989497],
        [ 0.25      , -0.06630078],
        [ 0.25      ,  0.        ],
        [ 0.25      ,  0.06630078],
        [ 0.22365842,  0.12989497],
        [ 0.1767767 ,  0.1767767 ],
        [ 0.12989497,  0.22365842],
        [ 0.06630078,  0.25      ],
        [ 0.        ,  0.25      ],
        [-0.06630078,  0.25      ],
        [-0.12989497,  0.22365842],
        [-0.1767767 ,  0.1767767 ],
        [-0.22365842,  0.12989497],
        [-0.25      ,  0.06630078],
        [-0.25      ,  0.        ],
        [-0.25      , -0.06630078],
        [-0.22365842, -0.12989497],
        [-0.1767767 , -0.1767767 ],
        [-0.12989497, -0.22365842],
        [-0.06630078, -0.25      ],
        [ 0.        , -0.25      ],
        [ 0.        , -0.25      ]]), 
    ',': np.array([[-0.49999, -0.49999],
        [ 0.50001, -0.49999],
        [ 0.50001,  0.50001],
        [-0.49999,  0.50001],
        [-0.49999, -0.49999]]), 
    'o': np.array([[ 0.        , -0.5       ],
        [ 0.13260155, -0.5       ],
        [ 0.25978994, -0.44731685],
        [ 0.35355339, -0.35355339],
        [ 0.44731685, -0.25978994],
        [ 0.5       , -0.13260155],
        [ 0.5       ,  0.        ],
        [ 0.5       ,  0.13260155],
        [ 0.44731685,  0.25978994],
        [ 0.35355339,  0.35355339],
        [ 0.25978994,  0.44731685],
        [ 0.13260155,  0.5       ],
        [ 0.        ,  0.5       ],
        [-0.13260155,  0.5       ],
        [-0.25978994,  0.44731685],
        [-0.35355339,  0.35355339],
        [-0.44731685,  0.25978994],
        [-0.5       ,  0.13260155],
        [-0.5       ,  0.        ],
        [-0.5       , -0.13260155],
        [-0.44731685, -0.25978994],
        [-0.35355339, -0.35355339],
        [-0.25978994, -0.44731685],
        [-0.13260155, -0.5       ],
        [ 0.        , -0.5       ],
        [ 0.        , -0.5       ]]), 
    'v': np.array([[-6.123234e-17, -5.000000e-01],
        [ 5.000000e-01,  5.000000e-01],
        [-5.000000e-01,  5.000000e-01],
        [-6.123234e-17, -5.000000e-01]]), 
    '^': np.array([[ 0. ,  0.5],
        [-0.5, -0.5],
        [ 0.5, -0.5],
        [ 0. ,  0.5]]), 
    '<': np.array([[-5.000000e-01,  3.061617e-17],
        [ 5.000000e-01, -5.000000e-01],
        [ 5.000000e-01,  5.000000e-01],
        [-5.000000e-01,  3.061617e-17]]), 
    '>': np.array([[ 5.00000000e-01, -9.18485099e-17],
        [-5.00000000e-01,  5.00000000e-01],
        [-5.00000000e-01, -5.00000000e-01],
        [ 5.00000000e-01, -9.18485099e-17]]), 
    '1': np.array([[ 0.  ,  0.  ],
        [ 0.  , -0.5 ],
        [ 0.  ,  0.  ],
        [ 0.4 ,  0.25],
        [ 0.  ,  0.  ],
        [-0.4 ,  0.25]]), 
    '2': np.array([[ 0.000000e+00,  0.000000e+00],
        [ 6.123234e-17,  5.000000e-01],
        [ 0.000000e+00,  0.000000e+00],
        [-4.000000e-01, -2.500000e-01],
        [ 0.000000e+00,  0.000000e+00],
        [ 4.000000e-01, -2.500000e-01]]), 
    '3': np.array([[ 0.00000000e+00,  0.00000000e+00],
        [-5.00000000e-01,  9.18485099e-17],
        [ 0.00000000e+00,  0.00000000e+00],
        [ 2.50000000e-01, -4.00000000e-01],
        [ 0.00000000e+00,  0.00000000e+00],
        [ 2.50000000e-01,  4.00000000e-01]]), 
    '4': np.array([[ 0.000000e+00,  0.000000e+00],
        [ 5.000000e-01, -3.061617e-17],
        [ 0.000000e+00,  0.000000e+00],
        [-2.500000e-01,  4.000000e-01],
        [ 0.000000e+00,  0.000000e+00],
        [-2.500000e-01, -4.000000e-01]]), 
    '8': np.array([[-0.19134172,  0.46193977],
        [-0.46193977,  0.19134172],
        [-0.46193977, -0.19134172],
        [-0.19134172, -0.46193977],
        [ 0.19134172, -0.46193977],
        [ 0.46193977, -0.19134172],
        [ 0.46193977,  0.19134172],
        [ 0.19134172,  0.46193977],
        [-0.19134172,  0.46193977]]), 
    's': np.array([[-0.5, -0.5],
        [ 0.5, -0.5],
        [ 0.5,  0.5],
        [-0.5,  0.5],
        [-0.5, -0.5]]), 
    'p': np.array([[ 3.06161700e-17,  5.00000000e-01],
        [-4.75528258e-01,  1.54508497e-01],
        [-2.93892626e-01, -4.04508497e-01],
        [ 2.93892626e-01, -4.04508497e-01],
        [ 4.75528258e-01,  1.54508497e-01],
        [ 1.53080850e-16,  5.00000000e-01]]), 
    '*': np.array([[ 3.06161700e-17,  5.00000000e-01],
        [-1.12256991e-01,  1.54508493e-01],
        [-4.75528258e-01,  1.54508497e-01],
        [-1.81635627e-01, -5.90169926e-02],
        [-2.93892626e-01, -4.04508497e-01],
        [-3.50830079e-17, -1.90983000e-01],
        [ 2.93892626e-01, -4.04508497e-01],
        [ 1.81635627e-01, -5.90169926e-02],
        [ 4.75528258e-01,  1.54508497e-01],
        [ 1.12256991e-01,  1.54508493e-01],
        [ 1.53080850e-16,  5.00000000e-01]]), 
    'h': np.array([[ 3.06161700e-17,  5.00000000e-01],
        [-4.33012702e-01,  2.50000000e-01],
        [-4.33012702e-01, -2.50000000e-01],
        [-9.18485099e-17, -5.00000000e-01],
        [ 4.33012702e-01, -2.50000000e-01],
        [ 4.33012702e-01,  2.50000000e-01],
        [ 1.53080850e-16,  5.00000000e-01]]), 
    'H': np.array([[-2.50000000e-01,  4.33012702e-01],
        [-5.00000000e-01,  2.22044605e-16],
        [-2.50000000e-01, -4.33012702e-01],
        [ 2.50000000e-01, -4.33012702e-01],
        [ 5.00000000e-01, -3.05311332e-16],
        [ 2.50000000e-01,  4.33012702e-01],
        [-2.50000000e-01,  4.33012702e-01]]), 
    '+': np.array([[-0.5,  0. ],
        [ 0.5,  0. ],
        [ 0. , -0.5],
        [ 0. ,  0.5]]), 
    'x': np.array([[-0.5, -0.5],
        [ 0.5,  0.5],
        [-0.5,  0.5],
        [ 0.5, -0.5]]), 
    'D': np.array([[-5.55111512e-17, -7.07106781e-01],
        [ 7.07106781e-01,  0.00000000e+00],
        [ 5.55111512e-17,  7.07106781e-01],
        [-7.07106781e-01,  1.11022302e-16],
        [-5.55111512e-17, -7.07106781e-01]]), 
    'd': np.array([[-3.33066907e-17, -7.07106781e-01],
        [ 4.24264069e-01,  0.00000000e+00],
        [ 2.22044605e-17,  7.07106781e-01],
        [-4.24264069e-01,  1.11022302e-16],
        [-3.33066907e-17, -7.07106781e-01]]), 
    '|': np.array([[ 0. , -0.5],
        [ 0. ,  0.5]]), 
    '_': np.array([[ 5.000000e-01, -3.061617e-17],
        [-5.000000e-01,  3.061617e-17]]), 
    'P': np.array([[-0.16666667, -0.5       ],
        [ 0.16666667, -0.5       ],
        [ 0.16666667, -0.16666667],
        [ 0.5       , -0.16666667],
        [ 0.5       ,  0.16666667],
        [ 0.16666667,  0.16666667],
        [ 0.16666667,  0.5       ],
        [-0.16666667,  0.5       ],
        [-0.16666667,  0.16666667],
        [-0.5       ,  0.16666667],
        [-0.5       , -0.16666667],
        [-0.16666667, -0.16666667],
        [-0.16666667, -0.5       ]]), 
    'X': np.array([[-0.25, -0.5 ],
        [ 0.  , -0.25],
        [ 0.25, -0.5 ],
        [ 0.5 , -0.25],
        [ 0.25,  0.  ],
        [ 0.5 ,  0.25],
        [ 0.25,  0.5 ],
        [ 0.  ,  0.25],
        [-0.25,  0.5 ],
        [-0.5 ,  0.25],
        [-0.25,  0.  ],
        [-0.5 , -0.25],
        [-0.25, -0.5 ]])}





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
    for symb in marker_to_array:
        if not arr.shape == marker_to_array[symb].shape:
            continue
        idx = np.allclose(marker_to_array[symb],arr)
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
    rows = geometry[0]
    cols = geometry[1]
    start = subgridspec.num1+1
    end = subgridspec.num2+1
    s = getAxid([rows,cols,start])
    e = getAxid([rows,cols,end])
    return tuple(np.array(e)-np.array(s)+1)

def getGetsandSets(obj):
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

def setFigAxes(obj,cmd,PlotteratorObj,attr):
    '''
    This function feeds in the 'gets' and 'sets' of axes and figs and passes them to 
    the plotterator function to parse commands.  This checks to see if the
    attribute passed is callable.  Since Plotterator will never store class instances
    we need to make sure that it is not a class instance before we parse it.
    Input:
        obj - The plotterator object we want to apply the command to
        cmd - The command that we want to apply to the obj (Typically obj.set_xxx())
        PlotteratorObj - the Plotter class instance of Plotterator
        attr - The attribute, or the value we want to pass to the command (Typically obj.get_xxx())
    Kwargs:
        N/A
    Return:
        None
    '''
    try:
        if callable(attr):
            attr = attr()
        if isinstance(attr,np.ndarray) or attr != None:
            if not 'matplotlib' in str(type(attr)) or isinstance(attr,np.ndarray):
                #special crap for geoaxis extent
                if cmd == 'set_extent':
                    if attr[0] < -180 or attr[1] > 180 or attr[2] < -90 or attr[3] > 90:
                        # attr = (-180,180,-90,90)
                        PlotteratorObj.parseCommand(obj,'set_global',[[]])
                        return
                PlotteratorObj.parseCommand(obj,f'{cmd}',[[attr]])
            else:
                if debug:
                    print(f'{attr} is class')
        else:
            if debug:
                print(f'{attr} is nan')
    except:
        if debug:
            print(f'{cmd} failed')

def setLines(axid,obj,cmd,PlotteratorObj,attr,**kwargs):
    '''
    This function feeds in the 'gets' and 'sets' of Lines and passes them to 
    the plotterator function to parse line commands.  This checks to see if the
    attribute passed is callable.  Since Plotterator will never store class instances
    we need to make sure that it is not a class instance before we parse it.
    Input:
        axid - The plotterator axis Id
        obj - The plotterator object we want to apply the command to
        cmd - The command that we want to apply to the obj (Typically obj.set_xxx())
        PlotteratorObj - the Plotter class instance of Plotterator
        attr - The attribute, or the value we want to pass to the command (Typically obj.get_xxx())
    Kwargs:
        N/A
    Return:
        None
    '''
    try:
        if callable(attr):
            attr = attr()
        if isinstance(attr,np.ndarray) or attr != None:
            if not 'matplotlib' in str(type(attr)) or isinstance(attr,np.ndarray):
                PlotteratorObj.parseLineCommand(axid,obj,f'{cmd}',[[attr]])
            else:
                if debug:
                    print(f'{attr} is class')
        else:
            if debug:
                print(f'{attr} is nan')
    except:
        if debug:
            print(f'{cmd} failed')
            
def setPatch(axid,obj,cmd,PlotteratorObj,attr):
    '''
    This function feeds in the 'gets' and 'sets' of patches and passes them to 
    the plotterator function to parse patch commands.  This checks to see if the
    attribute passed is callable.  Since Plotterator will never store class instances
    we need to make sure that it is not a class instance before we parse it.
    Input:
        axid - The plotterator axis Id
        obj - The plotterator object we want to apply the command to
        cmd - The command that we want to apply to the obj (Typically obj.set_xxx())
        PlotteratorObj - the Plotter class instance of Plotterator
        attr - The attribute, or the value we want to pass to the command (Typically obj.get_xxx())
    Kwargs:
        N/A
    Return:
        None
    '''
    try:
        if callable(attr):
            attr = attr()
        if isinstance(attr,np.ndarray) or attr != None:
            if not 'matplotlib' in str(type(attr)) or isinstance(attr,np.ndarray):
                PlotteratorObj.parsePatchCommand(axid,obj,f'{cmd}',[[attr]])
            else:
                if debug:
                    print(f'{attr} is class')
        else:
            if debug:
                print(f'{attr} is nan')
    except:
        if debug:
            print(f'{cmd} failed')
            
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
    
    

def PlotterateFig(fig):
    '''
    This function will take in a matplotlib figure object and Plotterate it.
    Some aspects of the plot may NOT carry over perfectly, however, this is a
    WIP.

    Parameters
    ----------
    fig : Matplotlib Figure

    Returns
    -------
    None.
    
    Detailed Info
    -------------
    
    Figure:
        Creates:
            1. matplotlib figure
        Issues:
            1. Need to add support for legends
    Axes:
        Creates:
            1. matplotlib axes
        Issues:
            1. Need to provide better support for legends.  Currently only basic
            ones are made..... somtimes
    Lines:
        Creates:
            1. Line plots
        Issues:
            None at the moment
    Scatter:
        Creates:
            1. Scatter plots
        Issues:
            None that I know of
    Wedges:
        Creates:
            1. Pie charts
            2. Wedge Patch
        Issues:
            None that I know of
    Rectangle:
        Creates:
            1. Bar charts
            2. Rectangle Patch
            3. Histogram
        Issues:
            None that I know of
    PatchCollection:
        Creates:
            1. Stacked Plots
        Issues:
            All the issues... Ugh
    Annotation:
        Creates:
            1. Annotations
        Issues:
            None that I know of
    Text:
        Creates:
            1. Annotations
        Issues:
            None that I know of
            
    Some more things to look at....
    Basemap plots - How to identify?  Transforms?
    3D plots - I don't think this will be hard
    Stackplots - I dont know anything
    

    '''
    xx = fig.properties()
    figsize = (xx['figwidth'],xx['figheight'])
    suptitle = fig._suptitle
    if suptitle:
        title = fig._suptitle.get_text()
    else:
        title = ''
    facecolor = xx['facecolor']
    loose = not xx['tight_layout']
    pltr = Plotterator.Plotter(figsize=figsize,facecolor=facecolor,loose=loose,title=title,
                               picker_type='interactive',picker=6)
    
    '''
    I think i need to loop over axes first, to tell whether or not there is a twin call
    '''
    twindict = {}
    
    for i,axes in enumerate(fig.properties()['axes']):
        # return axes
        mapplot = False
        excludes = []
        axesGetSets = getGetsandSets(axes)
        yy = axes.properties()
        # return yy
        '''
        Check to see if first child is quadmesh.. if so.. its a color bar. let plotterator
        handle this below
        '''
        if isinstance(yy['children'][0],matplotlib.collections.QuadMesh):
            continue
        # return yy
        Id = getAxid(yy['geometry'])
        
        rowspan,colspan = getSpan(yy['subplotspec'], yy['geometry'])
        axType = determineAxesType(axes)
        if axType == 'normal':
            pax = pltr.add_subplot(Id,rowspan,colspan)
        elif axType == '3D':
            pax = pltr.add_subplot(Id,rowspan,colspan,threeD=True)
        elif axType == 'geo':
            projection = str(type(axes.projection)).split('.')[-1][:-2]+'()'
            print(projection)
            mapplot=True
            excludes.extend(['get_xticks','get_xticklabels','get_yticks','get_yticklabels',
                             'get_xlim','get_ylim','get_xbound','get_ybound','_get_view'])
            pax = pltr.add_subplot(Id,rowspan,colspan,mapplot=True,mapproj=projection)
        
        if Id in twindict and has_twin(axes):
            pax = pltr.twin(Id)
        elif Id in twindict and not has_twin(axes):
            pass
        else:
            twindict[Id] = has_twin(axes)
        
        for cmd in axesGetSets:
            if cmd in excludes:
                continue
            attr = eval(f'axes.{cmd}')
            setFigAxes(pax, axesGetSets[cmd], pltr,attr)
        
        '''
        This is for the grids... fml
        '''
        try:
            ygridMajor = ax.yaxis._gridOnMajor
            ygridMinor = ax.yaxis._gridOnMinor
            xgridMajor = ax.xaxis._gridOnMajor
            xgridMinor = ax.xaxis._gridOnMinor
            if ygridMajor and ygridMinor and xgridMinor and xgridMajor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='both',axis='both')])
            elif ygridMajor and ygridMinor and not xgridMinor and not xgridMajor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='both',axis='y')])
            elif not ygridMajor and not ygridMinor and xgridMinor and xgridMajor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='both',axis='x')])
            elif ygridMajor and not ygridMinor and xgridMajor and not xgridMinor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='major',axis='both')])
            elif ygridMajor and not ygridMinor and not xgridMajor and not xgridMinor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='major',axis='y')])
            elif not ygridMajor and not ygridMinor and xgridMajor and not xgridMinor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='major',axis='x')])
            elif not ygridMajor and ygridMinor and not xgridMajor and xgridMinor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='minor',axis='both')])
            elif not ygridMajor and ygridMinor and not xgridMajor and not xgridMinor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='minor',axis='y')])
            elif not ygridMajor and not ygridMinor and not xgridMajor and xgridMinor:
                pltr.parseCommand(pax,'grid',[dict(b=True,which='minor',axis='x')])
        except:
            pass
        
        
        '''
        This will produce a simple legend... sometimes.. Need to make this more fancy
        '''
        lgnd = axes.get_legend()
        if lgnd:
            pltr.parseCommand(pax,'legend',[[]])
            
        for child in yy['children']:
            if mapplot:
                proj = parseCartopyTransform(child)
            else:
                proj = None
            # return child
            excludes = []
            if isinstance(child,matplotlib.spines.Spine):
                '''
                This is here because at the moment of writing this, it is
                believed that all visible portions of the plot comes before
                the Spine object in the list of children for the axes.
                '''
                break
            
            if isinstance(child,mpl_toolkits.mplot3d.art3d.Line3D):
                patch = False
                # return child
                x,y,z = child.get_data_3d()
                if mapplot:
                    line = pltr.plot3d(x, y, z, axid=pax, transform=proj)
                else:
                    line = pltr.plot3d(x,y,z,axid=pax)
            
            elif isinstance(child,mpl_toolkits.mplot3d.art3d.Path3DCollection):
                # return child
                patch = False
                marker = determineMarker(child)
                x,y,z = child._offsets3d
                array = child.get_array()
                if isinstance(array,np.ndarray):
                    color = child.get_facecolors()
                    ec = child.get_edgecolors()
                    cmap = child.get_cmap()
                    colorbar = child.colorbar
                    excludes.extend(['get_array','get_facecolor','get_facecolors',
                                     'get_fc','get_edgecolor','get_edgecolors','get_ec'])
                    if cmap:
                        cmap = cmap.name
                    if colorbar and cmap:
                        pltr.add_colorbar(pax,cmap,colorbar._label,np.array([array.min(),array.max()]))
                    if mapplot:
                        line = pltr.scatter3d(x,y,z,axid=pax,marker=marker,c=array.data,ec=ec,cmap=cmap,transform=proj)
                    else:
                        line = pltr.scatter3d(x,y,z,axid=pax,marker=marker,c=array.data,ec=ec,cmap=cmap)
                else:
                    if mapplot:
                        line = pltr.scatter3d(x,y,z,axid=pax,marker=marker,transform=proj)
                    else:
                        line = pltr.scatter3d(x,y,z,axid=pax,marker=marker)
                
            elif isinstance(child,matplotlib.lines.Line2D):
                # return child
                patch = False
                if mapplot:
                    line = pltr.plot([],[],axid=pax,transform=proj)
                else:
                    line = pltr.plot([],[],axid=pax)
            elif isinstance(child,matplotlib.collections.PathCollection):
                # return child
                patch = False
                array = child.get_array()
                marker = determineMarker(child)
                if isinstance(array,np.ndarray):
                    color = child.get_facecolors()
                    ec = child.get_edgecolors()
                    x = child.get_offsets()[:,0]
                    y = child.get_offsets()[:,1]
                    cmap = child.get_cmap()
                    colorbar = child.colorbar
                    excludes.extend(['get_array','get_facecolor','get_facecolors',
                                     'get_fc','get_edgecolor','get_edgecolors','get_ec',
                                     'get_offsets'])
                    if cmap:
                        cmap = cmap.name
                    if colorbar and cmap:
                        pltr.add_colorbar(pax,cmap,colorbar._label,np.array([array.min(),array.max()]))
                    if mapplot:
                        line = pltr.scatter(x,y,axid=pax,marker=marker,c=array.data,ec=ec,cmap=cmap,transform=proj,picker=5)
                    else:
                        line = pltr.scatter(x,y,axid=pax,marker=marker,c=array.data,ec=ec,cmap=cmap,picker=5)
                else:
                    if mapplot:
                        line = pltr.scatter([],[],axid=pax,marker=marker,transform=proj,picker=5)
                    else:
                        line = pltr.scatter([],[],axid=pax,marker=marker,picker=5)
                    
            elif isinstance(child,matplotlib.text.Annotation):
                patch = None
                text = child._text
                xy = child.xy
                va = child._verticalalignment
                ha = child._horizontalalignment
                color = child._color
                if mapplot:
                    pltr.parseCommand(pax,'annotate',[[text,xy],dict(va=va,ha=ha,color=color,transform=proj,picker=5)])
                else:
                    pltr.parseCommand(pax,'annotate',[[text,xy],dict(va=va,ha=ha,color=color,picker=5)])
                continue
            
            elif isinstance(child,matplotlib.text.Text):
                patch = None
                print(proj)
                # return child
                text = child._text
                x = child._x
                y = child._y
                va = child._verticalalignment
                ha = child._horizontalalignment
                color = child._color
                if mapplot:
                    pltr.parseCommand(pax,'text',[[x,y,text],dict(ha=ha,va=va,color=color,transform=proj,picker=5)])
                else:
                    pltr.parseCommand(pax,'text',[[x,y,text],dict(ha=ha,va=va,color=color,picker=5)])
                continue
                
            elif isinstance(child,matplotlib.patches.Wedge):
                patch = True
                if mapplot:
                    cargs =[dict(center=(0,0),
                             theta1=0,
                             theta2=0,
                             r=0,
                            transform=proj)]
                else:
                    cargs =[dict(center=(0,0),
                             theta1=0,
                             theta2=0,
                             r=0)]
                line = pltr.add_patch(pax,'Wedge',cargs)
            elif isinstance(child,matplotlib.patches.Rectangle):
                patch = True
                if mapplot:
                    cargs = [dict(xy=(0,0),
                                  width=0,
                                  height=0,
                                  transform=proj)]
                else:
                    cargs = [dict(xy=(0,0),
                                  width=0,
                                  height=0)]
                line = pltr.add_patch(pax,'Rectangle',cargs)
            elif isinstance(child,matplotlib.patches.Polygon):
                patch = True
                if mapplot:
                    cargs = [dict(xy=[[0,0],[0,1]],transform=proj)]
                else:
                    cargs = [dict(xy=[[0,0],[0,1]])]
                line = pltr.add_patch(pax, 'Polygon', cargs)
            elif isinstance(child,matplotlib.patches.Circle):
                patch = True
                if mapplot:
                    cargs = [dict(xy=[0,0],radius=0,transform=proj)]
                else:
                    cargs = [dict(xy=[0,0],radius = 0)]
                line = pltr.add_patch(pax,'Circle',cargs)
            elif isinstance(child,matplotlib.patches.Ellipse):
                patch = True
                if mapplot:
                    cargs = [dict(xy=[0,0],width=0,height=0,transform=proj)]
                else:
                    cargs = [dict(xy=[0,0],width=0,height=0)]
                line = pltr.add_patch(pax,'Ellipse',cargs)
            elif isinstance(child,matplotlib.collections.PolyCollection):
                patch = True
                paths = child.get_paths()
                points = paths[-1].vertices
                ec = child.get_edgecolor()
                fc = child.get_facecolor()[0]
                print(fc[0])
                print(ec)
                if not ec:
                    ec = fc
                else:
                    ec = ec[0]
                excludes.extend(['get_edgecolor','get_edgecolors','get_ec',
                                 'get_facecolor','get_facecolors','get_fc'])
                if mapplot:
                    cargs = [dict(xy=points,ec=ec,fc=fc,transform=proj)]
                else:
                    cargs = [dict(xy=points,ec=ec,fc=fc)]
                line = pltr.add_patch(pax,'Polygon',cargs)
                continue
            else:
                continue
            childGetSets = getGetsandSets(child)
            # return childGetSets
            for cmd in childGetSets:
                if cmd in excludes:
                    continue
                attr = eval(f'child.{cmd}')
                if patch:
                    setPatch(pax,line, childGetSets[cmd], pltr,attr)
                else:
                    setLines(pax, line, childGetSets[cmd], pltr, attr)
                    
        '''
        Set the x,y tick objs after all the plots have been set
        '''
        xticklabels = getTickLabels(axes,'x')
        yticklabels = getTickLabels(axes,'y')
        if xticklabels:        
            pltr.parseCommand(pax,'set_xticklabels',[[xticklabels]])
        if yticklabels:
            pltr.parseCommand(pax,'set_yticklabels',[[yticklabels]])
    pltr.createPlot('',PERSIST=True)
    
if __name__ == '__main__':
    x = np.random.randint(0,20,200)
    y = np.random.randint(0,25,200)
    
    if False:
        def randrange(n, vmin, vmax):
            '''
            Helper function to make an array of random numbers having shape (n, )
            with each number distributed Uniform(vmin, vmax).
            '''
            return (vmax - vmin)*np.random.rand(n) + vmin
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('what')
        ax.set_ylabel('who')
        ax.set_zlabel('when')
        n = 100
        
        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
        for m, zlow, zhigh in [('o', -50, -25)]:#, ('^', -30, -5)]:
            xs = randrange(n, 23, 32)
            ys = randrange(n, 0, 100)
            zs = randrange(n, zlow, zhigh)
            if True:
                sc = ax.scatter(xs, ys, zs, marker=m,c=xs,cmap='bone')
                cbar = fig.colorbar(sc)
                cbar.set_label('hoo')
            if False:
                ax.plot(xs,ys,zs,marker=m)
    
    if False:
        fig,ax = plt.subplots()
        x = np.random.randint(0,20,200)
        y = np.random.randint(0,25,200)
        
        if False:
            #scatter plot
            sc = ax.scatter(x,y,marker='D',c=x,s=200,ec='k',cmap=plt.cm.get_cmap('bone'),label='stuff')
            cbar = fig.colorbar(sc)
            cbar.set_label('what')
            sc2 = ax.scatter(x,y,marker='D',c=x,s=20,ec='b',cmap=plt.cm.get_cmap('jet'),zorder=2,label='what')
            ax.legend()
            cbar = fig.colorbar(sc2)
            cbar.set_label('who')
            ax2 = ax.twinx()
            ax2.scatter(y,x,marker='*',c='b',label='who')
            ax2.legend()
        if False:
            #pie chart
            cmap = plt.cm.jet
            plcolor = cmap(np.linspace(0.,1.,3))
            ax.pie([10,23,32],autopct='%.2f%%',colors=plcolor)
            
        if False:
            #basemap plot ugh here we go
            import cartopy
            import cartopy.crs as ccrs
            fig = plt.figure()
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.stock_img()

            ny_lon, ny_lat = -75, 43
            delhi_lon, delhi_lat = 77.23, 28.61
            
            plt.plot([ny_lon, delhi_lon], [ny_lat, delhi_lat],
                      color='blue', linewidth=2, marker='o',
                      transform=ccrs.Geodetic(),
                      )
            
            plt.plot([ny_lon, delhi_lon], [ny_lat, delhi_lat],
                      color='gray', linestyle='--',
                      transform=ccrs.PlateCarree(),
                      )
            
            ax.add_patch(matplotlib.patches.Polygon([[0,0],[20,0],[20,20],[0,20]],
                                                    fill = False,color='g',ls='--',
                                                    transform=ccrs.PlateCarree()))
            
            ax.add_patch(matplotlib.patches.Circle([30,30],radius=10,color='g',ls='--',
                                                   transform=ccrs.PlateCarree()))
            
            plt.text(ny_lon - 3, ny_lat - 12, 'New York',
                      horizontalalignment='right',
                      transform=ccrs.Geodetic())
            
            plt.text(delhi_lon + 3, delhi_lat - 12, 'Delhi',
                      horizontalalignment='left',
                      transform=ccrs.Geodetic())
            ax.set_extent([-50,50,-50,50])
            
        if False:
            #bar chart
            N = 5
            men_means = (20, 35, 30, 35, 27)
            men_std = (2, 3, 4, 1, 2)
            
            ind = np.arange(N)  # the x locations for the groups
            width = 0.35
            rects1 = ax.bar(ind, men_means, width, color='r', yerr=men_std)
    
            women_means = (25, 32, 34, 20, 25)
            women_std = (3, 5, 2, 3, 3)
            rects2 = ax.bar(ind + width, women_means, width, color='y', yerr=women_std)
            
            # add some text for labels, title and axes ticks
            ax.set_ylabel('Scores')
            ax.set_title('Scores by group and gender')
            ax.set_xticks(ind + width / 2)
            ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
            ax.annotate('What',(1,10),color='b')
            
            ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))
            
            
            def autolabel(rects):
                """
                Attach a text label above each bar displaying its height
                """
                for rect in rects:
                    height = rect.get_height()
                    ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                            '%d' % int(height),
                            ha='center', va='bottom')
            
            autolabel(rects1)
            autolabel(rects2)
            
        if False:
            #stack plot
            
            x = [1, 2, 3, 4, 5]
            y1 = [1, 1, 2, 3, 5]
            y2 = [0, 4, 2, 6, 8]
            y3 = [1, 3, 5, 7, 9]
            
            y = np.vstack([y1, y2, y3])
            print(y)
            
            labels = ["Fibonacci ", "Evens", "Odds"]
            ax.stackplot(x, y, labels=labels)
            
        if False:
            #histogram
            import matplotlib.mlab as mlab
            import scipy.stats
    
            mu, sigma = 100, 15
            x = mu + sigma*np.random.randn(10000)
            
            # the histogram of the data
            n, bins, patches = plt.hist(x, 50, normed=1, facecolor='green', alpha=0.75)
            
            # add a 'best fit' line
            y = scipy.stats.norm.pdf( bins, mu, sigma)
            l = plt.plot(bins, y, 'r--', linewidth=1)
            
            plt.xlabel('Smarts')
            plt.ylabel('Probability')
            plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
            plt.axis([40, 160, 0, 0.03])
            plt.grid(True)
        
    
    
    # z = PlotterateFig(fig)