#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 17:50:14 2020

@author: marlowcj
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib
import numpy as np


if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5 import Plotterator

def Spider_Plot(dictionary,outdir='',**kwargs):
    '''
    This function creates a spider plot.  Takes a dictionary of the form
    d = {Label:{Metric Name1:value, Metric Name2:value2}, Label2: etc..}
    
    Input:
        dictionary - a nested dictionary of the metric name then label (maybe missile_name)
                     then the values (Which correspond to a ration pass/total)
        outdir - The full path to save the pklplot
        Kwargs:
            outline - Make a circle outline to indicate 100% success, else create a line at 90 degrees
            show - Show make the plot persist from plotterator
            perp_annotation - make annotations perpindicular to the spokes, else parallel
            **kwargs - Plotterator kwargs
        Returns:
            Returns nothing, just opens a plot.
    '''
    outline = kwargs.get('outline',True)
    show = kwargs.get('show',True)
    perp_annotation = kwargs.get('perp_annotation',True)
    if dictionary:
        metric_num = len(dictionary[list(dictionary.keys())[0]])
        item_num = len(dictionary.keys())
        if metric_num:
            totals = [0]*metric_num
            angles = np.linspace(0,2*np.pi,metric_num+1)
            # make the spokes
            pltr = Plotterator.Plotter(**kwargs)
            pax = pltr.add_subplot()
            for angle in angles:
                x = np.cos(angle)
                y = np.sin(angle)
                pltr.plot([0,x],[0,y],axid=pax,lw=2,ls='-',color='k')
            if not outline:
                pltr.plot([0,0],[0,1],axid=pax,lw=2,ls='--',color=(0,0,0,.5))
                pltr.parseCommand(pax,'annotate',[['100%',(0,1)],dict(ha='center',va='bottom')])
            else:
                pltr.add_patch(pax, 'Circle', [[(0,0),1],dict(lw=1,edgecolor=(0,0,0,.5),label='100% Success',fill=False)])
            for j,key in enumerate(dictionary):
                xs = []
                ys = []
                for i,key2 in enumerate(dictionary[key]):
                    if j == 0:
                        textx = 1.4*np.cos(angles[i])
                        texty = 1.4*np.sin(angles[i])
                        rot = np.rad2deg(angles[i])
                        if perp_annotation:
                            if rot > 180 and rot < 360:
                                rot += 180
                            rot -= 90
                            textx = 1.4*np.cos(angles[i])
                            texty = 1.4*np.sin(angles[i])
                            ha = 'center'
                            va = 'center'
                        else:
                            if rot > 90 and rot < 270:
                                rot += 180
                            textx = 1.1*np.cos(angles[i])
                            texty = 1.1*np.sin(angles[i])
                            if angles[i] > np.pi/2 and angles[i] < 3*np.pi/2:
                                ha = 'right'
                                va = 'center'
                            else:
                                ha = 'left'
                                va = 'center'
                        
                        pltr.parseCommand(pax,'annotate',[[key2,(textx,texty)],dict(rotation=rot,va=va,ha=ha,rotation_mode='anchor',zorder=2)])
                    x = dictionary[key][key2]*np.cos(angles[i])
                    y = dictionary[key][key2]*np.sin(angles[i])
                    xs.append(x)
                    ys.append(y)
                    totals[i] += dictionary[key][key2]
                xs.append(xs[0])
                ys.append(ys[0])
                pltr.plot(xs,ys,axid=pax,label=key,zorder=1)
            #make the polygon of the averages
            xs = []
            ys = []
            for i,total in enumerate(totals):
                avg = total/item_num
                x = avg*np.cos(angles[i])
                y = avg*np.sin(angles[i])
                xs.append(x)
                ys.append(y)
            pltr.add_patch(pax, 'Polygon', [[np.array([xs,ys]).T],dict(closed=True,facecolor=(1,0,1,1),edgecolor='k',lw=1)])
            
            pltr.parseCommand(pax,'set_aspect',[['equal']])
            pltr.parseCommand(pax, 'set_xlim', [[-3,3]])
            pltr.parseCommand(pax, 'set_ylim', [[-3,3]])
            pltr.parseCommand(pax, 'legend', [[]])
            pltr.parseCommand(pax, 'get_xaxis().set_visible',[[False]])
            pltr.parseCommand(pax, 'get_yaxis().set_visible',[[False]])
            save = os.path.isdir(os.path.dirname(outdir))
            pltr.createPlot(outdir, PERSIST=show,SAVEPKL=save,SAVEPNG=save)

if __name__ == '__main__':
    d = {'Scud-b':{'TOF':.3,'Burnout Time':.4,'Apogee':1.0,'Incredibly Long Title':.5,'HiggletyPiggley':.6},
         'Scud-c':{'TOF':.5,'Burnout Time':.8,'Apogee':1.0,'Incredibly Long Title':.5,'HiggletyPiggley':.2}}
    Spider_Plot(d,title='Spyder Plot for Missile IDs',tools=['Editor'],perp_annotation=False)
                        
                        
                        
                        