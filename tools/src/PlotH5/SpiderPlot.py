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
import pandas as pd


if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5 import Plotterator




def Spider_Plot(metric_df,criteria,label,outdir='',**kwargs):
    '''
    This function creates a spider plot.  Takes a dataframe with the metrics as
    the column names.  These values will be normalized with respect to the maximum
    values for each metric.  The criteria is a dictionary with keys as the metrics,
    which will contain a list of 2 values a minimum accepted value and maximum accepted
    value.  These will be normalized wrt to the maximum values of the metric_df
    and will be used to create the polygon patch in the plot.
    
    Input:
        metric_df - a dataframe that contains metrics as column names
        criteria - a dictionary with metrics as keys that contain an iterable of min and max
                   acceptable values.  criteria = {'Metric1':[min,max],'Metric2':[min,max]...}
        outdir - the full path to the directory you want to save the pklplt and or xlsx file
        
    Kwargs:
        outline - Make a circle outline to indicate the maximum value boundary
        show - make the plot persist in plotterator
        perp_annotation - make annotations perpindicular to the spokes, else parallel
        export - True/False export the normalized dataframe to an xlsx file
        **kwargs - Plotterator kwargs
    Returns:
        Returns nothing, makes a plotterated plot
    '''

    outline = kwargs.get('outline',True)
    show = kwargs.get('show',False)
    perp_annotation = kwargs.get('perp_annotation',True)
    export = kwargs.get('export',True)
    
    if metric_df.shape[0]:
        stat_df = metric_df.describe()
        max_df = stat_df.loc['max']
        min_df = stat_df.loc['min']
        range_df = max_df - min_df
        normalized_df = pd.DataFrame()
        for metric in range_df.index:
            normalized_df[metric] = (metric_df[metric] - min_df.loc[metric]) / range_df.loc[metric]
        normalized_df = normalized_df.fillna(0)
        polys = {}
        metric_list = list(metric_df)
        for metric in criteria:
            if metric in metric_list:
                metric_list.remove(metric)
            if metric in min_df:
                polys[metric] = (np.array(criteria[metric]) - min_df[metric])/range_df[metric]
    
        poly_df = pd.DataFrame(polys)
        poly_df = poly_df.fillna(0)
        num_metrics = poly_df.shape[1]
        angles = np.linspace(0,2*np.pi,num_metrics+1)[:-1]
        title = kwargs.pop('title',f'{label} Metric Evaluation')
        pltr = Plotterator.Plotter(title=title,**kwargs)
        pax = pltr.add_subplot()
        for angle in angles:
            x = np.cos(angle)
            y = np.sin(angle)
            pltr.plot([0,x],[0,y],axid=pax,lw=2,ls='-',color='k')
        if not outline:
            pltr.plot([0,0],[0,1],axid=pax,lw=2,ls='--',color=(0,0,0,.5))
            pltr.parseCommand(pax,'annotate',[['Max Range',(0,1)],dict(ha='center',va='bottom')])
        else:
            pltr.add_patch(pax, 'Circle', [[(0,0),1],dict(lw=1,edgecolor=(0,0,0,.5),label='Max Boundary',fill=False)])
        
        for i in range(normalized_df.shape[0]):
            vals = normalized_df.iloc[i].values
            xs = list(vals*np.cos(angles))
            ys = list(vals*np.sin(angles))
            xs.append(xs[0])
            ys.append(ys[0])
            pltr.plot(xs,ys,axid=pax)
        
        min_poly = np.min(poly_df).values
        max_poly = np.max(poly_df).values
        
        minpxs = min_poly*np.cos(angles)
        minpys = min_poly*np.sin(angles)
        maxpxs = max_poly*np.cos(angles)
        maxpys = max_poly*np.sin(angles)
        
        pltr.add_patch(pax, 'Polygon', [[np.array([maxpxs,maxpys]).T],dict(closed=True,facecolor=(1,0,1,1),edgecolor='k',lw=1)])
        pltr.add_patch(pax, 'Polygon', [[np.array([minpxs,minpys]).T],dict(closed=True,facecolor=(1,1,1,1),edgecolor='k',lw=1)])        
    
        pltr.parseCommand(pax,'set_aspect',[['equal']])
        pltr.parseCommand(pax, 'set_xlim', [[-3,3]])
        pltr.parseCommand(pax, 'set_ylim', [[-3,3]])
        pltr.parseCommand(pax, 'legend', [[]])
        pltr.parseCommand(pax, 'get_xaxis().set_visible',[[False]])
        pltr.parseCommand(pax, 'get_yaxis().set_visible',[[False]])
        save = os.path.isdir(outdir)
        if save:
            outfile = os.path.join(outdir,f'{label}_Metric_SpiderPlot.pklplt')
            if export:
                outxlsx = os.path.join(outdir,f'{label}_Normalized_Metrics.xlsx')
        else:
            outfile = ''
            if export:
                outxlsx = os.path.join(os.path.expanduser('~'),f'{label}_Normalized_Metrics.xlsx')
                print('No valid out directory was given, but you still want to export the normalized values.  Exporting to {outxlsx}')
        if export:
            for metric in metric_list:
                normalized_df[metric] = metric_df[metric]
            normalized_df.to_excel(outxlsx)
        pltr.createPlot(outdir, PERSIST=show,SAVEPKL=save,SAVEPNG=save)
    
        pltr.createPlot('', PERSIST=True)

        return poly_df


if __name__ == '__main__':
    # d = {'Scud-b':{'TOF':.3,'Burnout Time':.4,'Apogee':1.0,'Incredibly Long Title':.5,'HiggletyPiggley':.6},
         # 'Scud-c':{'TOF':.5,'Burnout Time':.8,'Apogee':1.0,'Incredibly Long Title':.5,'HiggletyPiggley':.2}}
    # Spider_Plot(d,title='Spyder Plot for Missile IDs',tools=['Editor'],perp_annotation=False)
    d = {}
    criteria = {}
    size = 1000
    for key in 'Apogee Burnout TOF Precession_Rate Orientation'.split():
        d[key] = np.random.randint(-10,5000,size)
        criteria[key] = [np.average(d[key])*1.05,np.average(d[key])*.95]
    metric_df = pd.DataFrame(d)
    mname = ['ScudB']*size
    mname[-1] = 'ScudC'
    metric_df['Missile Name'] = np.array(mname)
    
    print(metric_df)
    xx = Spider_Plot2(metric_df, criteria, 'Test',outdir = '/home/marlowcj/Desktop',export=True)
                        
                        
                        
                        
