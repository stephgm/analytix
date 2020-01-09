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
from matplotlib.artist import *
from matplotlib.transforms import *
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from collections import OrderedDict
import numpy as np
import struct
import binascii
from six import string_types
import inspect

debug = False

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5 import Plotterator


x = np.linspace(0,100,50)

# fig = plt.figure(constrained_layout=True)
fig,ax = plt.subplots()
# gs = fig.add_gridspec(3, 2)

# ax1 = fig.add_subplot(gs[0,1])
# ax2 = fig.add_subplot(gs[0:,0])

ax.plot(x,x,c='r',ls=':',marker='*')
ax.annotate('What',xy=(10,10))
ax.text(20,20,'WHO')
ax.scatter(x,x**2,c='b',label='fuc',marker='*')
# ax2.scatter(x,x**2,c='g',label='fuc')
# ax.legend()
ax.plot(x,x**3,c='g')

ax.pie([10,23,32])

# ax.set_xlabel('what')
# ax.set_xlabel('who')

labels = ['G1', 'G2', 'G3', 'G4', 'G5']
men_means = [20, 34, 30, 35, 27]
women_means = [25, 32, 34, 20, 25]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

rects1 = ax.bar(x - width/2, men_means, width, label='Men')
rects2 = ax.bar(x + width/2, women_means, width, label='Women')

# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Scores')
# ax.set_title('Scores by group and gender')
# ax.set_xticks(x)
# ax.set_xticklabels(labels)
# ax.legend()

# x = [1, 2, 3, 4, 5]
# y1 = [1, 1, 2, 3, 5]
# y2 = [0, 4, 2, 6, 8]
# y3 = [1, 3, 5, 7, 9]

# y = np.vstack([y1, y2, y3])

# # labels = ["Fibonacci ", "Evens", "Odds"]

# ax.stackplot(x, y1, y2, y3, labels=labels)
# ax.legend(loc='upper left')
# ax.stackplot(x,y)
fig.suptitle('WHOO')


def getAxid(geometry):
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
    gets = []
    sets = []
    for o in dir(obj):
        ## No need to set data for Lines.. has set_xdata and set_ydata
        if 'set_data' in o:
            continue
        ## This shits whenever I run it
        elif '_setstate' in o:
            continue
        ## This is the Marker type for scatters... need to figure this out and remove
        elif 'set_paths' in o:
            continue
        if 'get' in o:
            gets.append(o)
        if 'set' in o:
            sets.append(o)
    gets = map(lambda x: x.replace('get','set'),gets)
    h = list(set(gets).intersection(set(sets)))
    return h

def getGetsandSets2(obj):
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
                
                

def setFigAxes(obj,cmd,PlotteratorObj,attr):
    try:
        if callable(attr):
            attr = attr()
        if isinstance(attr,np.ndarray) or attr != None:
            if not 'matplotlib' in str(type(attr)) or isinstance(attr,np.ndarray):
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

def setLines(axid,obj,cmd,PlotteratorObj,attr):
    try:
        if callable(attr):
            attr = attr()
        if isinstance(attr,np.ndarray) or attr != None:
            if not 'matplotlib' in str(type(attr)) or isinstance(attr,np.ndarray):
                if cmd in ['set_radius','set_center','set_theta1','set_theta2']:
                    print(attr,cmd)
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
    try:
        if callable(attr):
            attr = attr()
        if isinstance(attr,np.ndarray) or attr != None:
            if not 'matplotlib' in str(type(attr)) or isinstance(attr,np.ndarray):
                if cmd in ['set_radius','set_center','set_theta1','set_theta2']:
                    print(attr,cmd)
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

def newMPLtoPl(fig):
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
            2. Annotations need to be looked at
    Lines:
        Creates:
            1. Line plots
        Issues:
            None at the moment
    Scatter:
        Creates:
            1. Scatter plots
        Issues:
            1. Markers need to be figured out
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
            1. This is super basic.  Gotta be able to set more things than pos
            and text
    Text:
        Creates:
            1. Annotations
        Issues:
            1. This is super basic.  Gotta be able to set more things than pos
            and text
    

    '''
    xx = fig.properties()
    figsize = (xx['figwidth'],xx['figheight'])
    title = fig._suptitle.get_text()
    facecolor = xx['facecolor']
    loose = not xx['tight_layout']
    pltr = Plotterator.Plotter(figsize=figsize,facecolor=facecolor,loose=loose,title=title)
    for i,axes in enumerate(fig.properties()['axes']):
        axesGetSets = getGetsandSets2(axes)
        yy = axes.properties()
        # return yy
        Id = getAxid(yy['geometry'])
        rowspan,colspan = getSpan(yy['subplotspec'], yy['geometry'])
        pax = pltr.add_subplot(Id,rowspan,colspan)
        for cmd in axesGetSets:
            attr = eval(f'axes.{cmd}')
            setFigAxes(pax, axesGetSets[cmd], pltr,attr)
        '''
        This will produce a simple legend... sometimes.. Need to make this more fancy
        '''
        lgnd = axes.get_legend()
        if lgnd:
            pltr.parseCommand(pax,'legend',[[]])
        for child in yy['children']:
            # return child
            if isinstance(child,matplotlib.spines.Spine):
                '''
                This is here because at the moment of writing this, it is
                believed that all visible portions of the plot comes before
                the Spine object in the list of children for the axes.
                '''
                break
            if isinstance(child,matplotlib.lines.Line2D):
                patch = False
                line = pltr.plot([],[],axid=pax)
            elif isinstance(child,matplotlib.collections.PathCollection):
                patch = False
                line = pltr.scatter([],[],axid=pax,marker='*')
            elif isinstance(child,matplotlib.text.Annotation):
                patch = None
                text = child._text
                xy = child.xy
                pltr.parseCommand(pax,'annotate',[[text,xy]])
                continue
            elif isinstance(child,matplotlib.text.Text):
                patch = None
                text = child._text
                x = child._x
                y = child._y
                pltr.parseCommand(pax,'text',[[x,y,text]])
                continue
                
            elif isinstance(child,matplotlib.patches.Wedge):
                patch = True
                cargs =[dict(center=(0,0),
                         theta1=0,
                         theta2=0,
                         r=0)]
                line = pltr.add_patch(pax,'Wedge',cargs)
            elif isinstance(child,matplotlib.patches.Rectangle):
                patch = True
                cargs = [dict(xy=(0,0),
                              width=0,
                              height=0)]
                line = pltr.add_patch(pax,'Rectangle',cargs)
            elif isinstance(child,matplotlib.collections.PolyCollection):
                pass
                # return child
            else:
                continue
            childGetSets = getGetsandSets2(child)
            for cmd in childGetSets:
                attr = eval(f'child.{cmd}')
                if patch:
                    setPatch(pax,line, childGetSets[cmd], pltr,attr)
                else:
                    setLines(pax, line, childGetSets[cmd], pltr, attr)
    pltr.createPlot('',PERSIST=True)
    
z = newMPLtoPl(fig)


