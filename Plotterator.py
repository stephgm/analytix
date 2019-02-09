#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:03:00 2019

@author: jacob
"""
import os
import cPickle
import matplotlib.pyplot as plt
from copy import deepcopy

STYLE_SHEET = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'gobat','ota_presentation.mplstyle')
ESI_STYLE_SHEET = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'gobat','esi_presentation.mplstyle')
plt.style.use(STYLE_SHEET)
exclude_list = ['x','y','fmt','plottype']
special_cmds = ['twinx','twiny']

def general_format_coord(current,other=None,llabel='',rlabel=''):
    def format_coord(x,y):
        display_coord = current.transData.transform((x,y))
        if not rlabel:
            rlabel = current.get_ylabel()
        if other:
            if not llabel:
                llabel = other.get_ylabel()
            inv = other.transData.inverted()
            ax_coord = inv.transform(display_coord)
            coords = [tuple(ax_coord)+(llabel,),(x,y,rlabel)]
            return ('{:<40}          {:<}'.format(*['{}: ({:.3f}, {:.3f})'.format(l,tx,ty) for tx,ty,l in coords]))
        else:
            return ('{:<40}'.format('{}: ({:.3f}, {:.3f})'.format(l,tx,ty)))
    return format_coord

ann_list = []

def on_pick(event):
    try:
        line = event.artist
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        ind = event.ind
        ax = line.axes
        ann = ax.annotate(line.get_label(),(xdata[ind[0]],ydata[ind[0]]))
        ann_list.appent(ann)
        line.figure.canvas.draw()
    except:
        pass
    
def on_release(event):
    for ann in ann_list:
        ann.remove()
        ann_list.remove(ann)
    event.canvas.draw()
    
class Plotter(object):
    def __init__(self,**kwargs):
        self.fig = {'commands':[]}
        self.sub = {}
        esistyle = kwargs.pop('esistyle',False)
        if esistyle:
            self.fig['stylesheet'] = ESI_STYLE_SHEET
        else:
            self.fig['stylesheet'] = STYLE_SHEET
        plt.style.use(self.fig['stylesheet'])
        self.fig['title'] = kwargs.pop('title','')
        self.fig['figsize'] = kwargs.pop('figsize',plt.rcParams['figure.figsize'])
        self.fig['classification'] = kwargs.pop('classy','SECRET//NOFORN')
        self.fig['facecolor'] = kwargs.pop('facecolor',plt.rcParams['figure.facecolor'])
        self.fig['defaultXLabel'] = kwargs.pop('xlabel','Time (s)')
        self.fig['defaultYLabel'] = kwargs.pop('ylabel','')
        self.fig['nrows'] = kwargs.pop('nrows',1)
        self.fig['ncols'] = kwargs.pop('ncols',1)
        for row in range(self.fig['nrows']):
            for col in range(self.fig['ncols']):
                self.initAxes((row,col))
                
    def initAxes(self,axid):
        self.sub[axid] = {'attr':{'xLabel':self.fig['defaultXLabel'],
                                  'yLabel':self.fig['defaultYLabel']},
                          'commands':[],
                          'lines':[]}
    
    def buildExecString(self,command):
        execString = command['cmd']+"("
        if command['args']:
            execString += ",".join(map(str,command['args']))
        if command['kwargs']:
            if command['args']:
                execString += ","
            for key in command['kwargs']:
                if isinstance(command['kwargs'][key],dict):
                    execString += key+"=dict("+".".join([k+"="+str(command['kwargs'][key][k])
                                                             for k in command['kwargs'][key]])
                else:
                    execString += key+"="+str(command['kwargs'][key])
                execString += ","
            execString = execString[:-1]
        execString += ")"
        return execString
    
    def createPlot(self,fname,**kwargs):
        SAVEPNG = kwargs.pop('SAVEPNG',True)
        SAVEPKL = kwargs.pop('SAVEPKL',True)        
        SHOW = kwargs.pop('SHOW',False)
        GENPLOTTER = kwargs.pop('GENPLOTTER',False)
        plt.style.use(self.fig['stylesheet'])
        fig, ax = plt.subplots(self.fig['nrows'],self.fig['ncols'],
                               facecolor=self.fig['facecolor'],
                               figsize=self.fig['figsize'])
        if self.fig['nrows'] > 1 and self.fig['ncols'] > 1:
            reftype = 2
        elif max([self.fig['nrows'],self.fig['ncols']]) == 1:
            reftype = 0
        else:
            reftype == 1
        setformat = False
        for row in range(self.fig['nrows']):
            for col in range(self.fig['ncols']):
                if reftype == 2:
                    thisax = ax[row][col]
                elif reftype == 1:
                    thisax = ax[row+col]
                else:
                    thisax = ax
                for line in self.sub[(row,col)]['lines']:
                    self.plotCall(thisax,line)
                    if line['plottype'] == 'plot':
                        setformat = True
                if self.sub[(row,col)]['commands']:
                    for command in self.sub[(row,col)]['commands']:
                        execString = "thisax."+self.buildExecString(command)
                        exec(execString,{},{"thisax":thisax})
                for t in self.sub:
                    if len(t) == 3 and t[:2] == (row,col):
                        for command in self.sub[t]['commands']:
                            if command['cmd'].startswith('twin'):
                                execString = "thisax."+self.buildExecString(command)
                                ax2 = eval(execString,{},{"thisax":thisax})
                        for line in self.sub[t]['lines']:
                            self.plotCall(ax2,line)
                            if line['plottype'] == 'plot':
                                setformat = True
                        if self.sub[t]['commands']:
                            for command in self.sub[t]['commands']:
                                if command['cmd'] not in special_cmds:
                                    execString = "ax2."+self.buildExecString(command)
                                    exec(execString,{},{"ax2":ax2})
                        if setformat:
                            ax2.format_coord = general_format_coord(ax2,thisax)
                if setformat:
                    thisax.format_coord = general_format_coord(thisax)
        if self.fig['commands']:
            for command in self.fig['commands']:
                execString = "fig."+self.buildExecString(command)
                exec(execString,{},{"fig":fig})
        fig.suptitle(self.fig['title'])
        fig.text(.03,.97,self.fig['classification'],ha='left',color='r')
        fig.text(.97,.03,self.fig['classification'],ha='left',color='r')
        if GENPLOTTER:
            plt.show()
        else:
            if SAVEPNG:
                fig.savefig(os.path.splitext(fname)[0]+'.png',facecolor=self.fig['facecolor'],format='png')
            if SAVEPKL:
                cPickle.dump({'fig':self.fig,'sub':self.sub},file(os.path.splitext(fname)[0]+'pklplt','wb'),
                             cPickle.HIGHEST_PROTOCOL)
            if SHOW:
                plt.show()
            plt.close(fig)

    def plotCall(self,ax,line):
        if line['plottype'] == 'plot':
            ax.plot(line['x'],line['y'],line['fmt'],
                        **{k:line[k] for k in line
                           if k not in exclude_list})
        elif line['plottype'] == 'scatter':
            ax.scatter(line['x'],line['y'],
                        **{k:line[k] for k in line
                           if k not in exclude_list})
        elif line['plottype'] == 'pie':
            ax.pie(line['x'],
                        **{k:line[k] for k in line
                           if k not in exclude_list})
            
    def plot(self,x,y,fmt='',axid=(0,0),**kwargs):
        # Attempt to set the reference to the correct axis,
        # return with message if invalid
        # axid not required, will default to single subplot
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
        else:
            print('Invalid axis reference.')
            return
        # last entry in axis lines if a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'plot'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['fmt'] = fmt
        self.sub[axid]['lines'][-1].update(kwargs)

    def scatter(self,x,y,axid=(0,0),**kwargs):
        # Attempt to set the reference to the correct axis,
        # return with message if invalid
        # axid not required, will default to single subplot
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
        else:
            print('Invalid axis reference.')
            return
        # last entry in axis lines if a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'scatter'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1].update(kwargs)

    def pie(self,sizes,axid=(0,0),**kwargs):
        # Attempt to set the reference to the correct axis,
        # return with message if invalid
        # axid not required, will default to single subplot
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
        else:
            print('Invalid axis reference.')
            return
        # last entry in axis lines if a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'pie'
        self.sub[axid]['lines'][-1]['x'] = sizes
        self.sub[axid]['lines'][-1].update(kwargs)
        
    def twin(self,axid=(0,0),axis='x',**kwargs):
        if axid in self.sub:
            cnt = 0
            for t in self.sub:
                if len(t) == 3 and t[:2] == axid:
                    cnt+=1
            newref = axid+(cnt,)
            self.initAxes(newref)
            self.parseCommand(newref,'twin{}'.format(axis),[kwargs])
            return newref
        else:
            print('Invalid axis reference.')
            return []
        
    def retrievePlot(self,fname):
        if os.path.isfile(fname):
            tempDict = cPickle.load(file(fname,'rb'))
            if 'fig' in tempDict and sub in 'tempDict':
                self.fig = deepcopy(tempDict['fig'])
                self.sub = deepcopy(tempDict['sub'])
            else:
                print('Invalid file.')
        else:
            print('Invalid file.')
            
    def parseCommand(self,obj,cmd,cargs):
        if obj != 'fig' and not (isinstance(obj,tuple) and obj in self.sub):
            print('Unrecognized reference object.')
            return
        if not isinstance(cmd,str) or not isinstance(cargs,list):
            print(obj,cmd,cargs)
            print('Invalid input to parseCommand.')
            return
        # OK now do stuff
        if obj == 'fig':
            thisthing = self.fig
        else:
            thisthing = self.sub[obj]
        thisthing['commands'].append({'cmd':cmd,'args':[],'kwargs':{}})
        for carg in cargs:
            if isinstance(carg,list):
                for car in carg:
                    if isinstance(car,str):
                        thisthing['commands'][-1]['args'].append("'''"+car+"'''")
                    else:
                        thisthing['commands'][-1]['args'].append(car)
            elif isinstance(carg,dict):
                for car in carg:
                    if isinstance(carg[car],dict):
                        thisthing['commands'][-1]['kwargs'][car] = {}
                        for k in carg[car]:
                            if isinstance(carg[car][k],str):
                                thisthing['commands'][-1]['kwargs'][car][k] = "'''"+carg[car][k]+"'''"
                            else:
                                thisthing['commands'][-1]['kwargs'][car][k] = carg[car][k]
                    else:
                        if isinstance(carg[car],str):
                            thisthing['commands'][-1]['kwargs'][car] = "'''"+carg[car]+"'''"
                        else:
                            thisthing['commands'][-1]['kwargs'][car] = carg[car]

if __name__ == '__main__':
    if False:
        """
        Demo of scatter plot with varying marker colors and sizes.
        """
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cbook
        
        # Load a numpy record array from yahoo csv data with fields date,
        # open, close, volume, adj_close from the mpl-data/example directory.
        # The record array stores python datetime.date as an object array in
        # the date column
        datafile = cbook.get_sample_data('/home/jacob/anaconda2/pkgs/matplotlib-1.5.1-np110py27_0/lib/python2.7/site-packages/matplotlib/mpl-data/sample_data/goog.npy')
        try:
            # Python3 cannot load python2 .npy files with datetime(object) arrays
            # unless the encoding is set to bytes. However this option was
            # not added until numpy 1.10 so this example will only work with
            # python 2 or with numpy 1.10 and later
            price_data = np.load(datafile, encoding='bytes').view(np.recarray)
        except TypeError:
            price_data = np.load(datafile).view(np.recarray)
        price_data = price_data[-250:]  # get the most recent 250 trading days
        
        delta1 = np.diff(price_data.adj_close)/price_data.adj_close[:-1]
        
        # Marker size in units of points^2
        volume = (15 * price_data.volume[:-2] / price_data.volume[0])**2
        close = 0.003 * price_data.close[:-2] / 0.003 * price_data.open[:-2]
        pltr = Plotter()
    #    fig, ax = plt.subplots()
        pltr.scatter(delta1[:-1], delta1[1:], c=close, s=volume, alpha=0.5)
    #    ax.scatter(delta1[:-1], delta1[1:], c=close, s=volume, alpha=0.5)
        pltr.parseCommand((0,0),'set_xlabel',[[r'$\Delta_i$'],dict(fontsize=15)])
        pltr.parseCommand((0,0),'set_ylabel',[[r'$\Delta_{i+1}$'],dict(fontsize=15)])
        pltr.parseCommand((0,0),'set_title',[['Volume and percent change']])
    #    ax.set_xlabel(r'$\Delta_i$', fontsize=15)
    #    ax.set_ylabel(r'$\Delta_{i+1}$', fontsize=15)
    #    ax.set_title('Volume and percent change')
        pltr.parseCommand((0,0),'grid',[[True]])
    #    ax.grid(True)
    #    fig.tight_layout()
        pltr.parseCommand('fig','tight_layout',[])
    #    plt.show()        
        pltr.createPlot('',SAVEPNG=False,SAVEPKL=False,SHOW=True)
    if True:
        """
        ===============
        Basic pie chart
        ===============
        
        Demo of a basic pie chart plus a few additional features.
        
        In addition to the basic pie chart, this demo shows a few optional features:
        
            * slice labels
            * auto-labeling the percentage
            * offsetting a slice with "explode"
            * drop-shadow
            * custom start angle
        
        Note about the custom start angle:
        
        The default ``startangle`` is 0, which would start the "Frogs" slice on the
        positive x-axis. This example sets ``startangle = 90`` such that everything is
        rotated counter-clockwise by 90 degrees, and the frog slice starts on the
        positive y-axis.
        """
        import matplotlib.pyplot as plt
        
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
        sizes = [15, 30, 45, 10]
        explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        pltr = Plotter()
#        fig1, ax1 = plt.subplots()
        pltr.pie(sizes,explode=explode,labels=labels,autopct='%1.1f%%',
                 shadow=True,startangle=90)
#        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
#                shadow=True, startangle=90)
        pltr.parseCommand((0,0),'axis',[['equal']])
#        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        pltr.createPlot('',SAVEPNG=False,SAVEPKL=False,SHOW=True)
#        plt.show()