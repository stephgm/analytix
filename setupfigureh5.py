#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:03:00 2019

@author: jacob
"""
import sys
import os
import numpy
import h5py
import matplotlib.pyplot as plt


ESI_STYLE_SHEET = 'matplotlibrc'
STYLE_SHEET = 'matplotlibrc'
exclude_list = ['fmt','x','y']

class Plotter(object):
    def __init__(self, **kwargs):
        self.fig = {}
        self.ax = []
        esistyle = kwargs.pop('esistyle',False)
        if esistyle:
            self.fig['stylesheet'] = ESI_STYLE_SHEET
        else:
            self.fig['stylesheet'] = STYLE_SHEET
        self.fig['title'] = kwargs.pop('title','')
        self.fig['figsize'] = kwargs.pop('figsize',plt.rcParams['figure.figsize'])
        self.fig['classification'] = kwargs.pop('classy','SECRET//NOFORN')
        self.fig['facecolor'] = kwargs.pop('facecolor',plt.rcParams['figure.facecolor'])
        self.fig['defaultXLabel'] = kwargs.pop('xlabel','Time (s)')
        self.fig['defaultYLabel'] = kwargs.pop('ylabel','')
        self.fig['nrows'] = kwargs.pop('nrows',1)
        self.fig['ncols'] = kwargs.pop('ncols',1)
        # if there's mutiple rows and cols, make nest lists of dictionarys
        # ax[row][col] = {}
        # else make a single list (even for only one subplot)
        # ax[row or col] = {}
        # roughly approximates the way matplotlib works
        if self.fig['nrows'] > 1 and self.fig['ncols'] > 1:
            self.deeper = True
            for row in range(self.fig['nrows']):
                self.ax.append([])
                for col in range(self.fig['ncols']):
                    self.ax[-1].append({'x':[0],'y':[0],'fmt':'.-',
                                        'xLabel':self.fig['defaultXLabel'],
                                        'yLabel':self.fig['defaultYLabel']})
        else:
            self.deeper = False
            for row in range(max([self.fig['nrows'],self.fig['ncols']])):
                self.ax.append({'x':[0],'y':[0],'fmt':'.-',
                                'xLabel':self.fig['defaultXLabel'],
                                'yLabel':self.fig['defaultYLabel']})
           
    def createPlot(self,fname,**kwargs):
        SAVE = kwargs.pop('SAVE',True)
        SHOW = kwargs.pop('SHOW',False)
        plt.style.use(self.fig['stylesheet'])
        fig, ax = plt.subplots(self.fig['nrows'],self.fig['ncols'],
                               facecolor=self.fig['facecolor'],
                               figsize=self.fig['figsize'])
        
        if self.deeper:
            axProps = list(ax[0][0].properties().keys())
            for row in range(self.fig['nrows']):
                for col in range(self.fig['ncols']):
                    ax[row][col].plot(self.ax[row][col]['x'],
                                      self.ax[row][col]['y'],
                                      self.ax[row][col]['fmt'],
                                      **{k:self.ax[row][col][k]
                                          for k in self.ax[row][col]
                                          if k in axProps}) 
        else:
            if max([self.fig['nrows'],self.fig['ncols']]) == 1:
                axProps = list(ax.properties().keys())
                ax.plot(self.ax[0]['x'],
                          self.ax[0]['y'],
                          self.ax[0]['fmt'],
                          **{k:self.ax[0][k]
                              for k in self.ax[0]
                              if k in axProps}) 
            else:
                axProps = list(ax[0].properties().keys())
                for row in range(max([self.fig['nrows'],self.fig['ncols']])):
                    ax[row].plot(self.ax[row]['x'],
                                      self.ax[row]['y'],
                                      self.ax[row]['fmt'],
                                      **{k:self.ax[row][k]
                                          for k in self.ax[row]
                                          if k in axProps}) 
        fig.suptitle(self.fig['title'])
        fig.text(.03, .97, self.fig['classification'], ha='left', color='r')
        fig.text(.97, .03, self.fig['classification'], ha='right', color='r')
        if SAVE:
            fig.savefig(os.path.splitext(fname)[0]+'.png',facecolor=self.fig['facecolor'],format='png')
            self.savePlot(os.path.splitext(fname)[0]+'.h5')
        if SHOW:
            plt.show()
        plt.close(fig)
        
    def plot(self,x,y,axid=0,fmt='.-',**kwargs):
        # attempt to set the reference to the correct axis object,
        # return with message if invalid
        # axid not required, will default to single subplot
        if (isinstance(axid, tuple) or isinstance(axid, list))\
                and len(axid) == 2 and self.deeper == True\
                and axid[0] < len(self.ax) and axid[0] >= 0\
                and axid[1] < len(self.ax[axid[0]]) and axid[1] >=0:
            ax = self.ax[axid[0]][axid[1]]
        elif isinstance(axid, int) and self.deeper == False\
                and axid < len(self.ax) and axid >= 0:
            ax = self.ax[axid]
        else:
            print('Invalid axis reference.')
            return
        # ax will now point to a dictionary that can received the params
        ax['x'] = x
        ax['y'] = y
        ax['fmt'] = fmt
        ax.update(kwargs)
        
    def savePlot(self,fname):
        with h5py.File(fname,'w') as fid:
            fid.attrs.create('fig',data=str(self.fig))
            agrp = fid.create_group('ax')
            if self.deeper:
                for row in range(self.fig['nrows']):
                    rgrp = agrp.create_group(str(row))
                    for col in range(self.fig['ncols']):
                        cgrp = rgrp.create_group(str(col))
                        cgrp.create_dataset('xdata',data=self.ax[row][col]['x'])
                        cgrp.create_dataset('ydata',data=self.ax[row][col]['y'])
                        cgrp.attrs.create('setup',data=str({k:self.ax[row][col][k]
                                                            for k in self.ax[row][col]
                                                            if k not in ['x','y']}))
            else:
                for row in range(max([self.fig['nrows'],self.fig['ncols']])):
                    rgrp = agrp.create_group(str(row))
                    rgrp.create_dataset('xdata',data=self.ax[row]['x'])
                    rgrp.create_dataset('ydata',data=self.ax[row]['y'])
                    rgrp.attrs.create('setup',data=str({k:self.ax[row][k]
                                                        for k in self.ax[row]
                                                        if k not in ['x','y']}))
    
    def retrievePlot(self,fname):
        if os.path.isfile(fname):
            with h5py.File(fname,'r') as fid:
                if 'fig' not in fid.attrs or 'ax' not in fid:
                    print('Invalid HDF5 file for plotting.')
                    return
                else:
                    exec "self.fig="+fid.attrs['fig']
                    r = fid['ax'].keys()[0]
                    c = fid['ax'][r].keys()[0]
                    self.deeper = isinstance(fid['ax'][r][c],h5py.Group)
                    self.ax = []
                    if self.deeper:
                        for row in fid['ax']:
                            self.ax.append([])
                            for col in fid['ax'][row]:
                                self.ax[-1].append({})
                                exec "self.ax[-1][-1]="+fid['ax'][row][col].attrs['setup']
                                self.ax[-1][-1]['x'] = fid['ax'][row][col]['xdata'][...]
                                self.ax[-1][-1]['y'] = fid['ax'][row][col]['ydata'][...]
                    else:
                        for row in fid['ax']:
                            self.ax.append({})
                            exec "self.ax[-1]="+fid['ax'][row].attrs['setup']
                            self.ax[-1]['x'] = fid['ax'][row]['xdata'][...]
                            self.ax[-1]['y'] = fid['ax'][row]['ydata'][...]
        else:
            print('Invalid file.')
            
if __name__ == '__main__':
    # Single Subplot
    newPlotter = Plotter()
    newPlotter.plot(numpy.arange(100.),numpy.arange(100.),axid=1,fmt='--',lw=3,ms=20)
    newPlotter.createPlot('',SHOW=True,SAVE=False)
    # Multiple Columns
    newPlotter = Plotter(nrows=1,ncols=2)
    newPlotter.plot(numpy.arange(100.),numpy.arange(100.),axid=0,fmt='--',lw=3,ms=20)
    newPlotter.plot(numpy.arange(200.),numpy.arange(200.),axid=1,fmt='.-',lw=3,ms=20)
    newPlotter.createPlot('',SHOW=True,SAVE=False)
    # Multiple Rows, and a title
    newPlotter = Plotter(nrows=2,ncols=1,title='Call it something')
    newPlotter.plot(numpy.arange(100.),numpy.arange(100.),axid=0,fmt='--',lw=3,ms=20)
    newPlotter.plot(numpy.arange(200.),numpy.arange(200.),axid=1,fmt='.-',lw=3,ms=20)
    newPlotter.createPlot('',SHOW=True,SAVE=False)
    # Multiple Columns and rows
    newPlotter = Plotter(nrows=3,ncols=2)
    for r in range(3):
        for c in range(2):
            newPlotter.plot(numpy.arange(100.*(r-c)),numpy.arange(100.*(r-c)),axid=(r,c),lw=r,ms=c)
    newPlotter.createPlot('testout.png',SHOW=True,SAVE=True)
    # Reopen and replot
    newPlotter = Plotter()
    newPlotter.retrievePlot('testout.h5')
    newPlotter.createPlot('testout.png',SHOW=True,SAVE=False)

    