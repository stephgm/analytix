#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 20:03:00 2019

@author: jacob
"""
import os
import cPickle
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

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
    """
    Plotter class allows for storing data, specifications and commands
    for matplotlib to generate plots.  Current plot types supported:
        line plot
        scatter plot
        pie chart
    The figure is built using a GridSpec.  add_subplot calls initiate each
    subplot using the starting row, col as a reference and allowing for a
    rowspan, colspan to span multiple grid squares.  Plot, scatter, pie 
    calls add data to the plot
    
    Data is stored as follows:
        fig - a dictionary of figure params, as well as any commands to be
              executed against the figure at generation.
        sub - a dictionary containing subplots information indexed by a
              2-tuple of row, col; if an axis is twinned, it will be a 3-tuple
              starting with reference row,col then an index
        sub[key]['attr'] contains attributes to be set for the subplot
        sub[key]['lines'] contains each set of data to be added to the subplot
                 lines have a type to indicate which call to make to 
                 matplotlib subplot
    """
    def __init__(self,**kwargs):
        """
        Initiates figure with some commonly used defaults. Use kwargs
        to override.
        """
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
        self.fig['picker'] = kwargs.pop('picker',False)
                
    def initAxes(self,axid,rowspan,colspan):
        """
        Initiates each axes in the sub dictionary, requires reference starting
        ax id, and a row and column span
        """
        self.sub[axid] = {'attr':{'xLabel':self.fig['defaultXLabel'],
                                  'yLabel':self.fig['defaultYLabel']},
                          'commands':[],
                          'lines':[],
                          'rowspan':rowspan,
                          'colspan':colspan}
    
    def buildExecString(self,command):
        """
        Given a command dictionary as follows:
            'cmd' - the matplotlib function as a string
            'args' - list of arguments to be fed into the function
            'kwargs' - dictionary of kwargs to be fed into function
                       can be two levels deep, which should support
                       most matplotlib function calls
        Returns the function built to be executing using exec() or eval(),
        calling object is added separately to provide flexibility
        """
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
        fig = plt.figure(facecolor=self.fig['facecolor'],
                               figsize=self.fig['figsize'])
        numrows = 1
        numcols = 1
        for rowcol in self.sub:
            if len(rowcol) == 2:
                if rowcol[0]+self.sub[rowcol]['rowspan'] > numrows:
                    numrows = rowcol[0]+self.sub[rowcol]['rowspan']
                if rowcol[1]+self.sub[rowcol]['rowspan'] > numcols:
                    numcols = rowcol[1]+self.sub[rowcol]['rowspan']
        gs = gridspec.GridSpec(numrows,numcols,figure=fig)
        setformat = False
        rowcols = self.sub.keys()
        rowcols.sort()
        for rowcol in rowcols:
            if len(rowcol) == 2:
                thisax = fig.add_subplot(gs[rowcol[0]:rowcol[0]+self.sub[rowcol]['rowspan'], 
                                            rowcol[1]:rowcol[1]+self.sub[rowcol]['colspan']])
                for line in self.sub[rowcol]['lines']:
                    self.plotCall(thisax,line)
                    if line['plottype'] == 'plot':
                        setformat = True
                if self.sub[rowcol]['commands']:
                    for command in self.sub[rowcol]['commands']:
                        execString = "thisax."+self.buildExecString(command)
                        exec(execString,{},{"thisax":thisax})
                for t in self.sub:
                    if len(t) == 3 and t[:2] == rowcol:
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
        fig.text(.97,.03,self.fig['classification'],ha='right',color='r')
        if self.fig['picker']:
            fig.canvas.mpl_connect('pick_event',on_pick)
            fig.canvas.mpl_connect('button_release_event',on_release)
        if GENPLOTTER:
            plt.show()
        else:
            if SAVEPNG:
                fig.savefig(os.path.splitext(fname)[0]+'.png',facecolor=self.fig['facecolor'],format='png')
            if SAVEPKL:
                self.savePkl(fname)
            if SHOW:
                plt.show()
            plt.close(fig)

    def savePkl(self,fname):
        cPickle.dump({'fig':self.fig,'sub':self.sub},file(os.path.splitext(fname)[0]+'pklplt','wb'),
                     cPickle.HIGHEST_PROTOCOL)
        
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

    def add_subplot(self,axid=(0,0),rowspan=1,colspan=1):
        if axid not in self.sub:
            self.initAxes(axid,rowspan,colspan)
        else:
            print('Axes location already initiated')
            return
            
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
            if 'fig' in tempDict and 'sub' in tempDict:
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
        pltr = Plotter(ncols=2)
        pltr.add_subplot((0,0))
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
#        pltr.createPlot('',SAVEPNG=False,SAVEPKL=False,SHOW=True)
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
#        pltr = Plotter()
#        fig1, ax1 = plt.subplots()
        pltr.add_subplot((0,1))
        pltr.pie(sizes,(0,1),explode=explode,labels=labels,autopct='%1.1f%%',
                 shadow=True,startangle=90)
#        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
#                shadow=True, startangle=90)
        pltr.parseCommand((0,1),'axis',[['equal']])
#        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        pltr.createPlot('',SAVEPNG=False,SAVEPKL=False,SHOW=True)
#        plt.show()
    if True:
        """
        ===========
        Grid Spec Example
        ===========
        """
        import numpy as np
        pltr = Plotter()
        pltr.parseCommand('fig','tight_layout',[])
#        fig = plt.figure(tight_layout=True)
#        gs = gridspec.GridSpec(2, 2)
        
        pltr.add_subplot((0,0),1,2)
#        ax = fig.add_subplot(gs[0, :])
        pltr.plot(np.arange(0, 1e6, 1000),np.arange(0, 1e6, 1000),'',(0,0))
#        ax.plot(np.arange(0, 1e6, 1000))
        pltr.parseCommand((0,0),'set_ylabel',[['YLabel0']])
        pltr.parseCommand((0,0),'set_xlabel',[['XLabel0']])
#        ax.set_ylabel('YLabel0')
#        ax.set_xlabel('XLabel0')
        
        for i in range(2):
            pltr.add_subplot((1,i))
#            ax = fig.add_subplot(gs[1, i]
            pltr.plot(np.arange(1., 0., -0.1) * 2000., np.arange(1., 0., -0.1),'',(1,i))
            pltr.parseCommand((1,i),'set_ylabel',[['YLabel1 %d' % i]])
            pltr.parseCommand((1,i),'set_xlabel',[['XLabel1 %d' % i]])

#            ax.plot(np.arange(1., 0., -0.1) * 2000., np.arange(1., 0., -0.1))
#            ax.set_ylabel('YLabel1 %d' % i)
#            ax.set_xlabel('XLabel1 %d' % i)
#            if i == 0:
#                for tick in ax.get_xticklabels():
#                    tick.set_rotation(55)
#        fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()
        pltr.createPlot('',SAVEPNG=False,SAVEPKL=False,SHOW=True)
        
#        plt.show()
        
    if False:
        
#        def format_axes(fig):
#            for i, ax in enumerate(fig.axes):
#                ax.text(0.5, 0.5, "ax%d" % (i+1), va="center", ha="center")
#                ax.tick_params(labelbottom=False, labelleft=False)
        
#        fig = plt.figure(constrained_layout=True)
        pltr = Plotter()
#        gs = GridSpec(3, 3, figure=fig)
        pltr.add_subplot((0,0),1,3)
#        ax1 = fig.add_subplot(gs[0, :])
        # identical to ax1 = plt.subplot(gs.new_subplotspec((0, 0), colspan=3))
        pltr.add_subplot((1,0),1,2)
#        ax2 = fig.add_subplot(gs[1, 0:0+2])
        pltr.add_subplot((1,2),2,1)
#        ax3 = fig.add_subplot(gs[1:1+2, 2:2+1])
        pltr.add_subplot((2,0))
#        ax4 = fig.add_subplot(gs[2:2+1, 0:0+1])
        pltr.add_subplot((2,1))
#        ax5 = fig.add_subplot(gs[-1, -2])
        pltr.parseCommand('fig','suptitle',[['GridSpec']])
#        fig.suptitle("GridSpec")
#        format_axes(fig)
        pltr.createPlot('',SAVEPNG=False,SAVEPKL=False,SHOW=True)
#        plt.show()