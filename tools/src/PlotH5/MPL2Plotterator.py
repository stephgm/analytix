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
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from collections import OrderedDict
import numpy as np
import struct
import binascii
from six import string_types


if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5 import Plotterator


x = np.linspace(0,100,50)

fig = plt.figure(constrained_layout=True)
# fig,ax = plt.subplots()
gs = fig.add_gridspec(3, 2)

ax1 = fig.add_subplot(gs[0,1])
ax2 = fig.add_subplot(gs[0:,0])

ax1.plot(x,x,c='r',ls=':',marker='*')
ax2.scatter(x,x**2,c=x,ls='-',label='fuc',cmap=plt.cm.get_cmap('jet'))
# ax2.scatter(x,x**2,c='g',label='fuc')
ax2.legend()
ax1.plot(x,x**3,c='g')
ax1.set_xlabel('what')
ax2.set_xlabel('who')
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
    

def MPLtoPlotterator(fig):
    xx = fig.properties()
    
    figsize = (xx['figwidth'],xx['figheight'])
    title = fig._suptitle.get_text()
    facecolor = xx['facecolor']
    loose = not xx['tight_layout']
    
    pltr = Plotterator.Plotter(figsize=figsize,facecolor=facecolor,loose=loose,title=title)
    for i,axes in enumerate(xx['axes']):
        yy = axes.properties()
        Id = getAxid(yy['geometry'])
        rowspan,colspan = getSpan(yy['subplotspec'], yy['geometry'])
        xlabel = yy['xlabel']
        ylabel = yy['ylabel']
        yticklabels = list(map(lambda x: x._text,yy['yticklabels']))
        xticklabels = list(map(lambda x: x._text,yy['xticklabels']))
        # yticklines = yy['yticklines']
        # xticklines = yy['xticklines']
        yscale = yy['yscale']
        xscale = yy['xscale']
        ylim = yy['ylim']
        xlim = yy['xlim']
        title = yy['title']
        facecolor = yy['facecolor']
        legend = yy['legend']
        
        pax = pltr.add_subplot(Id,rowspan,colspan)
        pltr.parseCommand(pax,'set_xlabel',[[xlabel]])
        pltr.parseCommand(pax,'set_ylabel',[[ylabel]])
        pltr.parseCommand(pax,'set_yticklabels',[[yticklabels]])
        pltr.parseCommand(pax, 'set_xticklabels', [[xticklabels]])
        # pltr.parseCommand(pax,'set_yticklines',[[yticklines]])
        # pltr.parseCommand(pax,'set_xticklines',[[xticklines]])
        pltr.parseCommand(pax, 'set_yscale', [[yscale]])
        pltr.parseCommand(pax, 'set_xscale', [[xscale]])
        pltr.parseCommand(pax,'set_ylim',[[ylim]])
        pltr.parseCommand(pax,'set_xlim',[[xlim]])
        pltr.parseCommand(pax,'set_title',[[title]])
        pltr.parseCommand(pax,'set_facecolor',[[facecolor]])
        
        if legend:
            pltr.parseCommand(pax, 'legend', [[]])
        
        for child in yy['children']:
            if isinstance(child,matplotlib.lines.Line2D):
                z = child.properties()
                xdata = z['xdata']
                ydata = z['ydata']
                color = z['color']
                linewidth = z['linewidth']
                markeredgecolor = z['markeredgecolor']
                markeredgewidth = z['markeredgewidth']
                markerfacecolor = z['markerfacecolor']
                markerfacecoloralt = z['markerfacecoloralt']
                marker = z['marker']
                markersize = z['markersize']
                linestyle = z['linestyle']
                label = z['label']
                zorder = z['zorder']
                pltr.plot(xdata,ydata,
                         axid=pax,
                         c=color,
                         lw=linewidth,
                         ls=linestyle,
                         marker=marker,
                         markeredgecolor=markeredgecolor,
                         markeredgewidth=markeredgewidth,
                         markerfacecolor=markerfacecolor,
                         markerfacecoloralt=markerfacecoloralt,
                         markersize=markersize,
                         label=label,
                         zorder=zorder)
            elif isinstance(child,matplotlib.collections.PathCollection):
                z = child.properties()
                xdata = z['offsets'][:,0]
                ydata = z['offsets'][:,1]
                carraytype = type(z['array'])
                if carraytype != None:
                    markerfacecolor = z['array']
                    markeredgecolor = None
                else:
                    markerfacecolor = z['facecolor']
                    markeredgecolor = z['edgecolor']
                markersize = z['sizes']
                cmapname = z['cmap'].name
                label = z['label']
                zorder = z['zorder']
                pltr.scatter(xdata,ydata,
                             axid=pax,
                             c=markerfacecolor,
                             s=markersize,
                             cmap=cmapname,
                             edgecolor=markeredgecolor,
                             label=label,
                             zorder=zorder)
                
    pltr.createPlot('', PERSIST=True)    
    return yy,xx,z
    
yy,xx,z = MPLtoPlotterator(fig)


