#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERSION HISTORY
Date            Author              Version Number          Modification
--------        ------------        --------------          -------------
11 JUL 2019     J.Divoll            1.0                     Intial version tracking added, included handling for lack of version number
                                                            and for new style BlueMarble referencing
26 NOV 2019     C.Marlow            1.1                     Added new picker type and kwarg for fig
"""

versionNumber = 1.2

import sys
import os

if __name__ == '__main__':
    if os.name == 'posix':
        try:
            from subprocess import check_output
            with open('/dev/tty') as tty:
                h,w = list(map(int,check_output(['stty','size'],stdin=tty).split()))
        except:
            w = 140
    else:
        w = 140
    NOTES = '*'*w
    NOTES +=\
"""
usage: Plotterator.py <dir 1> <dir N> <file 1> <file N> <options>

option: -nt <##>
        Number of threads
        --max-threads Thread all jobs
"""
    NOTES += '*'*w
    if len(sys.argv) == 1:
        print(NOTES)
        sys.exit(0)

import glob
import pickle
import numpy as np
import matplotlib
from copy import deepcopy
#from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib import table
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from multiprocessing import cpu_count, Pool

try:
    import cartopy
    import cartopy.crs as ccrs
    from cartopy import config
    from cartopy.io.shapereader import Reader
    import cartopy.feature as cfeature
    if os.name == 'posix':
        cartopy.config['data_dir'] = f'{os.environ["TOOL_LOCAL"]}/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages/cartopy'
    else:
        cartopy.config['data_dir'] = os.path.join(os.path.dirname(sys.executable),'Lib','site-packages','cartopy')
except:
    ccrs = None

if ccrs:
    CfgDir = config['repo_data_dir']
    lenCfgDir = len(CfgDir)+1
    resolution = '10m'


if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from misc_functions.numpy_utils import multiDims
from PlotH5.mpltools.toolbarUtils import add_Tool
from PlotH5 import mplInteractive

if not os.path.isfile(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy')):
    np.save(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy'),plt.imread(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.png')))

if not os.path.isfile(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.npy')):
    np.save(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.npy'),plt.imread(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.png')))
global LOADED_BM
LOADED_BM = False

global BlueMarbleImg
BlueMarbleImg = {'bluemarblehd':None,'bluemarblesd':None}

STYLE_SHEET = os.path.join(RELATIVE_LIB_PATH,'gobat','ota_presentation.mplstyle')
ESI_STYLE_SHEET = os.path.join(RELATIVE_LIB_PATH,'gobat','esi_presentation.mplstyle')
plt.style.use(STYLE_SHEET)
exclude_list = ['x','y','z','fmt','plottype','bins','height','width','left','bottom','align','commands']
special_cmds = ['twinx','twiny','get_legend']
PICKERTOLERANCE = 5
figTitleFD = {
             'family':'sans',
             'color':'black',
             'fontweight':'bold',
             'fontsize':'24',
             'size':'24',
             'weight':'bold'
             }

figAxisFD =  {
             'family':'sans',
             'color':'black',
             'size':'20',
             'weight':'bold'
             }

figTitleFDSmall = {
             'family':'sans',
             'color':'black',
             'size':'16',
             'weight':'bold'
             }

figClassFD = {
             'family':'sans',
             'color':'red',
             'size':'18',
             'weight':'bold'
             }

def general_format_coord(current,other=None,llabel='',rlabel='',**kwargs):
    def format_coord(x,y):
        display_coord = current.transData.transform((x,y))
        rlabel = current.get_ylabel()
        if other:
            llabel = other.get_ylabel()
            inv = other.transData.inverted()
            ax_coord = inv.transform(display_coord)
            coords = [tuple(ax_coord)+(llabel,),(x,y,rlabel)]
            fcoords = ['{}: ({:.3f}, {:3f})'.format(l,tx,ty) for tx,ty,l in coords]
            return ('{:<40}{}{:>}'.format(fcoords[0],space,fcoords[1]))
        else:
            return ('{:<40}'.format('{}: ({:.3f}, {:.3f})'.format(rlabel,x,y)))
    return format_coord

ann_list = []

def on_pick(event):
    try:
        if isinstance(event.artist,Line2D):
            line = event.artist
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            ind = event.ind
            ax = line.axes
            ann = ax.annotate(line.get_label(),(xdata[ind[0]],ydata[ind[0]]),zorder=5000)
            ann_list.append(ann)
            line.figure.canvas.draw()
        elif isinstance(event.artist,matplotlib.collections.PathCollection):
            collection = event.artist
            ind = event.ind
            xy = collection.get_offsets()
            ax = collection.axes
            ann = ax.annotate(collection.get_label(),(xy[ind[0]][0],xy[ind[0]][1]),zorder=5000)
            ann_list.append(ann)
            fig = collection.get_figure()
            fig.canvas.draw()
    except:
        pass

def on_release(event):
    for ann in ann_list:
        ann.remove()
        ann_list.remove(ann)
    event.canvas.draw()

def PNGerator(flist,**kwargs):
    nthreads = kwargs.get('nthreads',1)
    if (nthreads > 1 and nthreads > cpu_count()) or nthreads < 1:
        nthreads = cpu_count()
    if isinstance(flist,str):
        flist = [flist]
    if isinstance(flist,list):
        if nthreads > 1:
            pool = Pool(nthreads)
        for fname in flist:
            if os.path.isfile(fname) and os.path.splitext(fname)[1] == '.pklplt':
                if nthreads > 1:
                    pool.apply_async(pngthread,args=(fname,))
                else:
                    pngthread(fname)
        if nthreads > 1:
            pool.close()
            pool.join()
    else:
        print('Invalid input.  Provide single file name string or list of filename strings')

def pngthread(fname):
    pltr = Plotter()
    pltr.retrievePlot(fname)
    pltr.createPlot(fname,SAVEPNG=True,SAVEPKL=False)

class Plotter(object):
    '''
    Plotter class allows for storing data, specifications and commands
    for matplotlib to generate plots. Current plot types supported:
        line plot
        scatter plot
        3d scatter plot
        pie chart
        stack plot
        histogram
        cartopy map plot
        bar chart
        horizontal bar chart
    The figure is built using a Gridspec.  Calls to add_subplot initiate each
    subplot using the starting row, col as a reference and allowing for a
    rowspan, colspan to span multiple grid sectors.  Plot, scatter, pie,
    scatter3d, hist, stackplot, bar, barh calls add data to the plot.

    Data is stored as follows:
        fig = a dictionary of figure params, as well as any commands to be
              executed against the figure at generation.
        sub = a dictionary containing subplots information indexed by a
              2-tuple of row,col; if an axis is twinned or a colorbar is
              added, it will be a 3-tuple starting with the reference
              row, col, then an index
        sub[key]['lines'] = contains each set of data to be added to the
              subplot, lines have a type to indicate which call to make
              to each matplotlib subplot
        lines = pointers to all the line objects for all the plots, so
              they can be programmatically separated from the subplot
        cbs = colorbar instances to be used in subplots
    '''
    def __init__(self,**kwargs):
        '''
        Initiates figure with some commonly used defaults.  Use kwargs to override.
        '''
        self.fig = {'commands':[]}
        self.sub = {}
        self.lines = []
        self.cbs = []
        self.version = versionNumber
        esistyle = kwargs.get('esistyle',False)
        if esistyle:
            self.fig['stylesheet'] = os.path.basename(ESI_STYLE_SHEET)
        else:
            self.fig['stylesheet'] = os.path.basename(STYLE_SHEET)
        plt.style.use(os.path.join(RELATIVE_LIB_PATH,'gobat',os.path.basename(self.fig['stylesheet'])))
        self.fig['title'] = kwargs.get('title','')
        self.fig['figsize'] = kwargs.get('figsize',plt.rcParams['figure.figsize'])
        self.fig['classification'] = kwargs.get('classy','SECRET//NOFORN')
        self.fig['facecolor'] = kwargs.get('facecolor',plt.rcParams['figure.facecolor'])
        self.fig['picker'] = kwargs.get('picker',True)
        self.fig['picker_type'] = kwargs.get('picker_type','original')
        self.fig['customlegend'] = None
        # list of axis that will share (zooming, panning, etc.)
        self.fig['sharing'] = []
        self.fig['tools'] = kwargs.get('tools',[])
        # Whether or not to use tight layout
        self.fig['loose'] = kwargs.get('loose',False)

    def initAxes(self,axid,rowspan,colspan,threeD=False,colorbar={},combinelegend=False,mapplot=False,mapproj='PlateCarree()',table=None):
        '''
        Initiates each axes in the sub dictionary, requires reference starting
        axid, and a row and column spans.
        '''
        self.sub[axid] = {'commands':[],
                          'lines':[],
                          'patches':[],
                          'features':[],
                          'cfeatures':[],
                          'texts':[],
                          'rowspan':rowspan,
                          'colspan':colspan,
                          '3d':threeD,
                          'colorbar':colorbar,
                          'combinelegend':combinelegend,
                          'mapplot':mapplot,
                          'mapproj':mapproj,
                          'mapimg':None,
                          'table':table,
                          'customlegend':None}

    def buildExecString(self,command):
        '''
        Given a command dictionary as follows:
            'cmd' = the matplotlib function as a string
            'args' = list of arguments to be fed into the function
            'kwargs' = dictionary of kwargs to fed into the function
                       can be two levels deep, which should support
                       most matplotlib function calls
        Returns the function built to be executed using exec() or eval(),
        calling object is added separately to provide flexibility
        '''
        execString = command['cmd']+'('
        if command['args']:
            execString += ','.join(map(str,[multiDims(arg,[])
                                            for arg in command['args']]))

        if command['kwargs']:
            if command['args']:
                execString += ','
            execString += self.buildKwargs(command['kwargs'])
            execString = execString[:-1]
        execString += ')'
        return execString.replace('transform=','transform=ccrs.')

    def buildKwargs(self,kwargs):
        execString = ''
        for key in kwargs:
            if key == 'transform':
                execString += key + '=' + kwargs[key].strip('\'')
            elif isinstance(kwargs[key],dict):
                execString += key+'=dict('+','.join([k+'='+str(multiDims(kwargs[key][k],[]))
                                                      for k in kwargs[key]])+')'
            elif isinstance(kwargs[key], str) or isinstance(kwargs[key],str):
                execString += key+'='+str(kwargs[key])
            else:
                execString += key+'='+str(multiDims(kwargs[key],[]))
            execString += ','
        return execString

    # def multiDims(self,arr,newlist):
    #     if isinstance(arr,np.ndarray):
    #         if arr.ndim > 2:
    #             for nextarr in arr:
    #                 newlist.append([])
    #                 self.multiDims(nextarr, newlist[-1])
    #         elif arr.ndim == 2:
    #             for nextarr in arr:
    #                 newlist.append(list(nextarr))
    #         else:
    #             newlist = list(arr)
    #         return newlist
    #     else:
    #         return arr

    def createPlot(self,fname,**kwargs):
        global LOADED_BM
        global BlueMarbleImg
        if self.version < 1.0:
            # handling for versions that did not track lines separately
            try:
                if self.lines:
                    pass
            except:
                self.lines = []
            for rowcol in self.sub:
                for line in self.sub[rowcol]['lines']:
                    self.lines.append(line)
            # handling for versions that did not track colorbars separately
            try:
                if self.cbs:
                    pass
            except:
                self.cbs = []
            # handling for versions that did not have default to tight layout
            if 'loose' not in self.fig:
                self.fig['loose'] = False
            # handling for old style blue marble image
            for rowcol in self.sub:
                if 'mapplot' in self.sub[rowcol] and self.sub[rowcol]['mapplot'] and self.sub[rowcol]['mapimg'] and self.sub[rowcol]['mapimg'] not in BlueMarbleImg:
                    if os.path.basename(self.sub[rowcol]['mapimg']) == 'bluemarble_21600x10800.png':
                        self.sub[rowcol]['mapimg'] = 'bluemarblehd'
                    elif os.path.basename(self.sub[rowcol]['mapimg']) == 'bluemarble_8192x4096.png':
                        self.sub[rowcol]['mapimg'] = 'bluemarblesd'
                    else:
                        # well sheit, set it to sd for speed
                        self.sub[rowcol]['mapimg'] = 'bluemarblesd'
        if self.version < 1.1:
            self.fig['picker_type'] = 'original'
        
        if self.version < 1.2:
            self.fig['tools'] = []
        self.version = versionNumber #updating Plot version.  Happens after all necessary changes happen

        # This ends the version discrepency handlin' as best we know, dingleberries remain below

        SAVEPNG = kwargs.get('SAVEPNG',False)
        SAVEPKL = kwargs.get('SAVEPKL',False)
        # Show waits for the plot to be closed
        SHOW = kwargs.get('SHOW',False)
        # Persist returns without closing allowing multiple plots to open
        PERSIST = kwargs.get('PERSIST',False)
        # Saveonly is the quickest, bypassing matplotlib entirely
        SAVEONLY = kwargs.get('SAVEONLY',True)
        # Canvas returns a canvas object that can be used in a gui
        CANVAS = kwargs.get('CANVAS',False)
        # This is here to override the SAVEONLY kwarg in case you don't want
        # to SAVEONLY
        if SAVEPNG or SHOW or PERSIST or CANVAS:
            SAVEONLY = False
        self.fig['loose'] = kwargs.get('loose',self.fig['loose'])
        if SAVEONLY:
            self.savePkl(fname)
            return
        plt.style.use(os.path.join(RELATIVE_LIB_PATH,'gobat',os.path.basename(self.fig['stylesheet'])))
        fig = plt.figure(facecolor=self.fig['facecolor'],
                         figsize=self.fig['figsize'])
        global space
        space = ' '*(int(self.fig['figsize'][0])*15)
        numrows = 1
        numcols = 1
        for rowcol in self.sub:
            if len(rowcol) == 2:
                if rowcol[0]+self.sub[rowcol]['rowspan'] > numrows:
                    numrows = rowcol[0]+self.sub[rowcol]['rowspan']
                if rowcol[1]+self.sub[rowcol]['colspan'] > numcols:
                    numcols = rowcol[1]+self.sub[rowcol]['colspan']
        gs = gridspec.GridSpec(numrows, numcols,figure=fig)
        setformat = False
        rowcols = list(self.sub.keys())
        rowcols.sort()
        theaxes = {}
        for rowcol in rowcols:
            if len(rowcol) == 2:
                cm = []
                othAx = {}
                if self.sub[rowcol]['3d']:
                    theaxes[rowcol] = fig.add_subplot(gs[rowcol[0]:rowcol[0]+self.sub[rowcol]['rowspan'],
                                                         rowcol[1]:rowcol[1]+self.sub[rowcol]['colspan']],
                                                         picker=PICKERTOLERANCE,
                                                         projection = '3d')
                elif 'mapplot' in self.sub[rowcol] and self.sub[rowcol]['mapplot']:
                    theaxes[rowcol] = fig.add_subplot(gs[rowcol[0]:rowcol[0]+self.sub[rowcol]['rowspan'],
                                                         rowcol[1]:rowcol[1]+self.sub[rowcol]['colspan']],
                                                      projection=eval('ccrs.{}'.format(self.sub[rowcol]['mapproj']),{'ccrs':ccrs}))
                    lonScale = None
                    if 'central_longitude' in self.sub[rowcol]['mapproj']:
                        cloc = self.sub[rowcol]['mapproj'].find('central_longitude')+len('central_longitude')+1
                        loc = self.sub[rowcol]['mapproj'].find(',',cloc)
                        if loc > -1:
                            lonScale = 1. - float(self.sub[rowcol]['mapproj'][cloc:loc])/360.
                        else:
                            loc = self.sub[rowcol]['mapproj'].find(')',cloc)
                            if loc > -1:
                                lonScale = 1. - (float(self.sub[rowcol]['mapproj'][cloc:loc])/360.)
                else:
                    theaxes[rowcol] = fig.add_subplot(gs[rowcol[0]:rowcol[0]+self.sub[rowcol]['rowspan'],
                                                         rowcol[1]:rowcol[1]+self.sub[rowcol]['colspan']],
                                                         picker=PICKERTOLERANCE)
                for t in self.sub:
                    if len(t) == 3 and t[:2] == rowcol:
                        for command in self.sub[t]['commands']:
                            if command['cmd'].startswith('twin'):
                                execString = 'thisax.'+self.buildExecString(command)
                                othAx[t] = eval(execString,{},{'thisax':theaxes[rowcol]})
                cbs = [(rc,self.sub[rc]['colorbar']['colorbarname'],self.sub[rc]['colorbar']['cbardata']) for rc in rowcols
                       if len(rc) == 3 and rc[:2] == rowcol and self.sub[rc]['colorbar'] and 'colorbarname' in self.sub[rc]['colorbar']]
                for rc,cb,dt in cbs:
                    thisSC = plt.cm.ScalarMappable(cmap = plt.cm.get_cmap(cb))
                    thisSC.set_array(dt)
                    cm.append(thisSC)
                for line in deepcopy(self.sub[rowcol]['lines']):
                    if 'cmap' in line and line['cmap']:
                        line['cmap'] = plt.cm.get_cmap(line['cmap'])
                    if 'transform' in line:
                        line['transform'] = eval('ccrs.{}'.format(line['transform']),{'ccrs':ccrs})
                    sc = self.plotCall(theaxes[rowcol],line)
                    if line['plottype'] == 'plot':
                        setformat = True
                if self.sub[rowcol]['commands']:
                    for command in self.sub[rowcol]['commands']:
                        if not (command['cmd'].startswith('get_legend') or command['cmd'].startswith('legend')) and not (command['cmd'] == 'legend'):
                            execString = 'thisax.'+self.buildExecString(command)
                            exec(execString,{'ccrs':ccrs},{'thisax':theaxes[rowcol]})
                if 'patches' in self.sub[rowcol] and self.sub[rowcol]['patches']:
                    for patch in self.sub[rowcol]['patches']:
                        execString = 'thisax.add_patch(mpatches.{})'.format(self.buildExecString(patch))
                        thepatch = eval(execString,{'ccrs':ccrs,'mpatches':mpatches},{'thisax':theaxes[rowcol]})
                        if 'commands' in patch and patch['commands']:
                            for command in patch['commands']:
                                execString = f'thepatch.{self.buildExecString(command)}'
                                exec(execString,{'ccrs':ccrs,'mpatches':mpatches},{'thepatch':thepatch})
                if 'texts' in self.sub[rowcol] and self.sub[rowcol]['texts']:
                    for text in self.sub[rowcol]['texts']:
                        execString = 'thisax.text{}'.format(self.buildExecString(text))
                        thetext = eval(execString,{'ccrs':ccrs},{'thisax':theaxes[rowcol]})
                        if 'commands' in text and text['commands']:
                            for command in text['commands']:
                                execString = f'thetext.{self.buildExecString(command)}'
                                exec(execString,{'ccrs':ccrs},{'thetext':thetext})
                for t in self.sub:
                    if len(t) == 3 and t[:2] == rowcol and not self.sub[t]['colorbar']:
                        for line in deepcopy(self.sub[t]['lines']):
                            if 'cmap' in line and line['cmap']:
                                line['cmap'] = plt.cm.get_cmap(line['cmap'])
                            if 'transform' in line:
                                line['transform'] = eval('ccrs.{}'.format(line['transform']),{'ccrs':ccrs})
                            sc = self.plotCall(othAx[t],line)
                            if line['plottype'] == 'plot':
                                setformat = True
                        if self.sub[t]['commands']:
                            for command in self.sub[t]['commands']:
                                if command['cmd'] not in special_cmds and not([scmd for scmd in special_cmds if command['cmd'].startswith(scmd)]):
                                    execString = 'othAx[t].'+self.buildExecString(command)
                                    exec(execString,{'ccrs':ccrs},{'othAx':othAx,'t':t})
                        if 'patches' in self.sub[t] and self.sub[t]['patches']:
                            for patch in self.sub[t]['patches']:
                                execString = 'othAx[t].add_patch(mpatches.{})'.format(self.buildExecString(patch))
                                thepatch = eval(execString,{'ccrs':ccrs,'mpatches':mpatches},{'othAx':othAx,'t':t})
                                if 'commands' in patch and patch['commands']:
                                    for command in patch['commands']:
                                        execString = f'thepatch.{self.buildExecString(command)}'
                                        exec(execString,{'ccrs':ccrs,'mpatches':mpatches},{'thepatch':thepatch})
                        if 'texts' in self.sub[rowcol] and self.sub[rowcol]['texts']:
                            for text in self.sub[rowcol]['texts']:
                                execString = 'othAx[t].text{}'.format(self.buildExecString(text))
                                thetext = eval(execString,{'ccrs':ccrs},{'othAx':othAx,'t':t})
                                if 'commands' in text and text['commands']:
                                    for command in text['commands']:
                                        execString = f'thetext.{self.buildExecString(command)}'
                                        exec(execString,{'ccrs':ccrs},{'thetext':thetext})
                        if setformat:
                            othAx[t].format_coord = general_format_coord(othAx[t], theaxes[rowcol])
                        lng = othAx[t].get_legend()
                        if lng:
                            for command in self.sub[t]['commands']:
                                if command['cmd'].startswith('get_legend'):
                                    execString = 'othAx[t].'+self.buildExecString(command)
                                    exec(execString,{'ccrs':ccrs},{'othAx':othAx,'t':t})
                            lng.set_draggable(True)
                h = []
                l = []
                if 'combinelegend' in self.sub[rowcol] and self.sub[rowcol]['combinelegend']:
                    h,l = theaxes[rowcol].get_legend_handles_labels()
                    for t in othAx:
                        h1,l1 = othAx[t].get_legend_handles_labels()
                        h+=h1
                        l+=l1
                if 'customlegend' in self.sub[rowcol] and self.sub[rowcol]['customlegend']:
                    h,l = self.sub[rowcol]['customlegend']
                    h = [eval('Line2D(hndl[0],hndl[1],{})'.format(self.buildKwargs(hndl[2])[:-1]),{'Line2D':Line2D},{'hndl':hndl})
                              for hndl in h]
                if self.sub[rowcol]['commands']:
                    for command in self.sub[rowcol]['commands']:
                        if command['cmd'] == 'legend':
                            if h:
                                execString = 'thisax.legend(h,l,'+self.buildExecString(command)[7:]
                                exec(execString,{'ccrs':ccrs},{'thisax':theaxes[rowcol],'h':h,'l':l})
                            else:
                                execString = 'thisax.'+self.buildExecString(command)
                                exec(execString,{'ccrs':ccrs},{'thisax':theaxes[rowcol]})
                lng = theaxes[rowcol].get_legend()
                if lng:
                    if self.sub[rowcol]['commands']:
                        for command in self.sub[rowcol]['commands']:
                            if command['cmd'].startswith('get_legend'):
                                execString = 'thisax.'+self.buildExecString(command)
                                exec(execString,{'ccrs':ccrs},{'thisax':theaxes[rowcol]})
                    lng.set_draggable(True)
                thiscb = None
                for i,(rc,cb,dt) in enumerate(cbs):
                    thiscb = fig.colorbar(cm[i])
                    thiscb.set_label(self.sub[rc]['colorbar']['label'])
                for rc in rowcols:
                    if len(rc) == 3 and rc[:2] == rowcol and self.sub[rc]['colorbar'] and 'LSCFL' in self.sub[rc]['colorbar']: # Heatmap stuff
                        cbinfo = self.sub[rc]['colorbar'] # for brevity
                        cmap = LinearSegmentedColormap.from_list(cbinfo['LSCFL'][0],cbinfo['LSCFL'][1],**cbinfo['LSCFL'][2])
                        p = theaxes[rowcol].pcolor(cbinfo['cbardata'][0],cmap=cmap,**cbinfo['cbardata'][1])
                        thiscb = fig.colorbar(p,**cbinfo['cb'])
                    if len(rc) == 3 and rc[:2] == rowcol and self.sub[rc]['colorbar'] and 'commands' in self.sub[rc]:
                        if thiscb:
                            if self.sub[rc]['commands']:
                                for command in self.sub[rc]['commands']:
                                    execString = 'thiscb.'+self.buildExecString(command)
                                    exec(execString,{'ccrs':ccrs},{'thiscb':thiscb})
                if 'mapplot' in self.sub[rowcol] and self.sub[rowcol]['mapplot'] and self.sub[rowcol]['mapimg']:
                    if not LOADED_BM:
                        LOADED_BM = True
                        BlueMarbleImg['bluemarblehd'] = np.load(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy'))
                        BlueMarbleImg['bluemarblesd'] = np.load(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.npy'))
                    EARTH_IMG = BlueMarbleImg[self.sub[rowcol]['mapimg']]
                    if lonScale:
                        theaxes[rowcol].set_global()
                    theaxes[rowcol].imshow(EARTH_IMG,
                                           origin = 'upper',
                                           transform = ccrs.PlateCarree(),
                                           extent=[-180,180,-90,90])
                if 'mapplot' in self.sub[rowcol] and 'features' in self.sub[rowcol] and self.sub[rowcol]['features']:
                    for feature in self.sub[rowcol]['features']:
                        featOfStrength = cfeature.ShapelyFeature(Reader(os.path.join(CfgDir,feature['fname'])).geometries(),
                                                                 eval('ccrs.{}'.format(feature['transform']),{'ccrs':ccrs}),
                                                                 **feature['kwargs'])
                        theaxes[rowcol].add_feature(featOfStrength)
                if 'mapplot' in self.sub[rowcol] and 'cfeatures' in self.sub[rowcol] and self.sub[rowcol]['cfeatures']:
                    for feature in self.sub[rowcol]['cfeatures']:
                        featOfStrength = eval('cfeature.{}'.format(feature['fname']),{'cfeature':cfeature})
                        theaxes[rowcol].add_feature(featOfStrength)
                if 'table' in self.sub[rowcol] and self.sub[rowcol]['table']:
                    self.fig['loose'] = True
                    execString = '(thisax.'+self.buildExecString(self.sub[rowcol]['table']['command'][1:])
                    the_table = eval('table.table'+execString,{'table':table},{'thisax':theaxes[rowcol]})
                    if 'cellParams' in self.sub[rowcol]['table'] and (self.sub[rowcol]['table']['cellParams']['cellFontsize'] or
                                                                      self.sub[rowcol]['table']['cellParams']['cellHeight']):
                        prop = the_table.properties()
                        cells = prop['child_artists']
                        for cell in cells:
                            if self.sub[rowcol]['table']['cellParams']['cellFontSize']:
                                cell.set_fontsize(self.sub[rowcol]['table']['cellParams']['cellFontSize'])
                                cell.set_height(cell.get_height()*self.sub[rowcol]['table']['cellParams']['cellHeight'])

                if setformat:
                    theaxes[rowcol].format_coord = general_format_coord(theaxes[rowcol])

        gotTitle = False
        figlng = None
        figh = []
        figl = []
        if 'customlegend' in self.fig and self.fig['customlegend']:
            figh, figl = self.fig['customlegend']
            figh = [eval('Line2D(hndl[0],hndl[1],{})'.format(self.buildKwargs(hndl[2])[:-1]),{'Line2D':Line2D},{'hndl':hndl})
                    for hndl in figh]
        if self.fig['commands']:
            for command in self.fig['commands']:
                if not(command['cmd'].startswith('get_legend') or command['cmd'].startswith('legend')) and not(command['cmd'].startswith('legend')):
                    if 'title' in command['cmd']:
                        gotTitle = True
                    execString = 'fig.'+self.buildExecString(command)
                    exec(execString,{'ccrs':ccrs},{'fig':fig})
            for command in self.fig['commands']:
                if command['cmd'] == 'legend':
                    if figh:
                        execString = 'fig.legend(figh,figl,'+self.buildExecString(command)[:7]
                        figlng = eval(execString,{'ccrs':ccrs},{'fig':fig,'figh':figh,'figl':figl})
                    else:
                        execString = 'fig.'+self.buildExecString(command)
                        figlng = eval(execString,{'ccrs':ccrs},{'fig':fig})
        if figlng:
            if self.fig['commands']:
                for command in self.fig['commands']:
                    if command['cmd'].startswith('get_legend('):
                        execString = 'fig.'+self.buildExecString(command)
                        exec(execString,{'ccrs':ccrs},{'fig':fig})
                    elif command['cmd'].startswith('legend('):
                        execString = 'fig.'+self.buildExecString(command)
                        exec(execString,{'ccrs':ccrs},{'fig':fig})
            figlng.set_draggable(True)
        if not gotTitle and self.fig['title']:
            fig.suptitle(self.fig['title'])
        if self.fig['classification'].lower().find('secret') != -1:
            classycolor = 'r'
        else:
            classycolor = '#006400'
        fig.text(.03,.97,self.fig['classification'],fontdict=figClassFD,ha='left',color=classycolor,picker=PICKERTOLERANCE)
        fig.text(.97,.03,self.fig['classification'],fontdict=figClassFD,ha='right',color=classycolor,picker=PICKERTOLERANCE)
        if 'sharing' in self.fig and self.fig['sharing']:
            for share in self.fig['sharing']:
                if share['source'] in self.sub and share['target'] in self.sub:
                    execString = 'ax1.get_shared_{}_axes().join(ax1,ax2)'.format(share['axis'])
                    exec(execString,{},{'ax1':theaxes[share['target']],'ax2':theaxes[share['source']]})
        if self.fig['picker']:
            if self.fig['picker_type'] == 'original':
                fig.canvas.mpl_connect('pick_event',on_pick)
                fig.canvas.mpl_connect('button_release_event',on_release)
            elif self.fig['picker_type'] == 'interactive':
                xx = mplInteractive.Editing_Picker()
                fig.canvas.mpl_connect('pick_event',xx.on_pick)
                fig.canvas.mpl_connect('button_release_event',xx.on_release)
        if not self.fig['loose']:
            fig.tight_layout(rect=(0,0.03,1,0.97))
        if CANVAS:
            return fig
        if PERSIST:
            if self.tools:
                add_Tool(fig,self.fig['tools'])
            fig.show()
        else:
            if SAVEPNG:
                fig.savefig(os.path.splitext(fname)[0]+'.png',facecolor=self.fig['facecolor'],format='png')
            if SAVEPKL:
                self.savePkl(fname)
            if SHOW:
                fig.show()
            plt.close(fig)

    def savePkl(self,fname):
        try:
            if self.lines:
                pass
        except:
            self.lines = []
            for rowcol in self.sub:
                for line in self.sub['lines']:
                    self.lines.append(line)
        try:
            if self.cbs:
                pass
        except:
            self.cbs = []
        pickle.dump({'fig':self.fig,'sub':self.sub,'lines':self.lines,'cbs':self.cbs,'version':self.version},
                    open(os.path.splitext(fname)[0]+'.pklplt','wb'),
                    2)

    def plotCall(self,ax,line):
        if line['plottype'] == 'plot':
            sc = ax.plot(line['x'],line['y'],line['fmt'],
                         **{k:line[k] for k in line if k not in exclude_list})[0]
        elif line['plottype'] == 'plot3d':
            sc = ax.plot(line['x'],line['y'],line['z'],line['fmt'],
                         **{k:line[k] for k in line if k not in exclude_list})[0]
        elif line['plottype'] == 'scatter':
            sc = ax.scatter(line['x'],line['y'],
                            **{k:line[k] for k in line if k not in exclude_list})
        elif line['plottype'] == 'pie':
            sc = ax.pie(line['x'],
                        **{k:line[k] for k in line if k not in exclude_list})
        elif line['plottype'] == 'scatter3d':
            sc = ax.scatter(line['x'],line['y'],line['z'],
                            **{k:line[k] for k in line if k not in exclude_list})
        elif line['plottype'] == 'stackplot':
            sc = ax.stackplot(line['x'],line['y'],
                              **{k:line[k] for k in line if k not in exclude_list})
        elif line['plottype'] == 'hist':
            sc = ax.hist(line['x'],line['bins'],
                         **{k:line[k] for k in line if k not in exclude_list})
        elif line['plottype'] == 'bar':
            sc = ax.bar(line['x'],line['height'],width=line['width'],bottom=line['bottom'],align=line['align'],
                        **{k:line[k] for k in line if k not in exclude_list})
        elif line['plottype'] == 'barh':
            sc = ax.barh(line['x'],line['width'],height=line['height'],left=line['left'],align=line['align'],
                         **{k:line[k] for k in line if k not in exclude_list})

        if 'commands' in line and line['commands'] and line['plottype'] in ('plot','plot3d','scatter','scatter3d'):
            for command in line['commands']:
                execString = 'sc.'+self.buildExecString(command)
                exec(execString,{'ccrs':ccrs},{'sc':sc})

        return sc

    def add_subplot(self,axid=(0,0),rowspan=1,colspan=1,threeD=False,combinelegend=False,mapplot=False,mapproj='PlateCarree()'):
        if axid not in self.sub:
            self.initAxes(axid, rowspan, colspan, threeD,{},combinelegend,mapplot,mapproj)
            return axid
        else:
            print('Axes location already initiated')
            return axid

    def plot(self,x,y,fmt='',axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to the correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'plot'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['fmt'] = fmt
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def plot3d(self,x,y,z,fmt='',axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to the correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'plot3d'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['z'] = z
        self.sub[axid]['lines'][-1]['fmt'] = fmt
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def scatter(self,x,y,axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'scatter'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def scatter3d(self,x,y,z,axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'scatter3d'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['z'] = z
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def pie(self,sizes,fmt='',axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'pie'
        self.sub[axid]['lines'][-1]['x'] = sizes
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def stackplot(self,x,y,axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'stackplot'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def hist(self,x,bins,axid=(0,0),**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'hist'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['bins'] = bins
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def bar(self,x,height,axid=(0,0),width=0.8,bottom=None,align='center',**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'bar'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['height'] = height
        self.sub[axid]['lines'][-1]['width'] = width
        self.sub[axid]['lines'][-1]['bottom'] = bottom
        self.sub[axid]['lines'][-1]['align'] = align
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def barh(self,x,width,axid=(0,0),height=0.8,left=None,align='center',**kwargs):
        '''
        Attempt to set the reference to correct axis,
        return with message if invalid
        axid not required, will default to single subplot
        '''
        if axid in self.sub:
            self.sub[axid]['lines'].append({})
            self.lines.append(self.sub[axid]['lines'][-1])
        else:
            print('Invalid axis reference')
            return
        # last entry in axis lines is a blank dictionary
        self.sub[axid]['lines'][-1]['plottype'] = 'barh'
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['width'] = width
        self.sub[axid]['lines'][-1]['height'] = height
        self.sub[axid]['lines'][-1]['left'] = left
        self.sub[axid]['lines'][-1]['align'] = align
        self.sub[axid]['lines'][-1]['picker'] = PICKERTOLERANCE
        self.sub[axid]['lines'][-1]['commands'] = []
        self.sub[axid]['lines'][-1].update(kwargs)

        return len(self.sub[axid]['lines'])-1

    def add_colorbar(self,axid=(0,0),colorbarname='jet',label='',dateridonteventknower=np.array([0,1]),**kwargs):
        if axid in self.sub:
            cnt = 0
            for t in self.sub:
                if len(t) == 3 and t[:2] == axid:
                    cnt+=1
            newref = axid+(cnt,)
            if isinstance(colorbarname, str): # this is the default expected case
                self.initAxes(newref, 1,1,False,{'colorbarname':colorbarname,
                                                 'label':label,
                                                 'cbardata':dateridonteventknower})
            else: # this is the heatmap style
                cb = kwargs.get('cb',{})
                if len(colorbarname) == 2:
                    colorbarname.append({})
                if len(dateridonteventknower) == 1:
                    dateridonteventknower.append({})
                self.initAxes(newref, 1, 1,False,{'LSCFL':colorbarname,
                                                  'cbardata':dateridonteventknower,
                                                  'cb':cb})
            return newref
        else:
            print('Invalid axis reference')
            return

    def twin(self,axid=(0,0),axis='x',**kwargs):
        if axid in self.sub:
            cnt = 0
            for t in self.sub:
                if len(t) == 3 and t[:2] == axid:
                    cnt += 1
            newref = axid+(cnt,)
            self.initAxes(newref, 1, 1)
            self.parseCommand(newref,'twin{}'.format(axis),[kwargs])
            return newref
        else:
            print('Invalid axis reference')
            return []

    def share(self,source,target,axis='x'):
        if axis not in ('x','y','both'):
            print('Invalid share axis designation. Use "x", "y", or "both".')
        else:
            if 'sharing' not in self.fig:
                self.fig['sharing'] = []
            if axis == 'both':
                self.fig['sharing'].append({'source':source,'target':target,'axis':'x'})
                self.fig['sharing'].append({'source':source,'target':target,'axis':'y'})
            else:
                self.fig['sharing'].append({'source':source,'target':target,'axis':axis})

    def add_map(self,filename,axid=(0,0),**kwargs):
        if filename.lower() not in BlueMarbleImg:
            print('{} not in dictionary'.format(filename.lower()))
        elif axid not in self.sub:
            print('Invalid axis reference')
        elif not self.sub[axid]['mapplot']:
            print('Subplot is not a Map Plot')
        else:
            self.sub[axid]['mapimg'] = filename.lower()
        return

    def add_patch(self,obj,cmd,cargs):
        if obj != 'fig' and not (isinstance(obj,tuple) and obj in self.sub):
            print('Unrecognized reference object add_patch ',obj,cmd,cargs)
            return
        if not isinstance(cmd,str) or not isinstance(cargs, list):
            print(obj,cmd,cargs)
            print('Invalid input to parseCommand')
            return
        # Ok now do stuff
        if obj == 'fig':
            thisthing = self.fig
        else:
            thisthing = self.sub[obj]
        # cmd is the thing that creates it, commands are the set_call stuff
        thisthing['patches'].append({'cmd':cmd,'args':[],'kwargs':{},'commands':[]})
        theobject = thisthing['patches'][-1]
        self.commandParsing(theobject,cargs)
        return len(thisthing['patches'])-1

    def add_text(self,obj,cargs):
        if obj != 'fig' and not (isinstance(obj,tuple) and obj in self.sub):
            print('Unrecognized reference object in add_text call ',obj,cargs)
            return
        if not isinstance(cargs, list):
            print(obj,cargs)
            print('Invalid input to add_text')
            return
        # Ok now do stuff
        if obj == 'fig':
            thisthing = self.fig
        else:
            thisthing = self.sub[obj]
        # cmd is the thing that creates it, commands are the set_call stuff
        thisthing['texts'].append({'cmd':'','args':[],'kwargs':{},'commands':[]})
        theobject = thisthing['texts'][-1]
        self.commandParsing(theobject,cargs)
        return len(thisthing['texts'])-1

    def add_feature(self,filename,transform,axid=(0,0),**kwargs):
        if not os.path.isfile(os.path.join(CfgDir,filename[lenCfgDir:])):
            print('{} not in cartopy config dir'.format(filename))
        elif axid not in self.sub:
            print('Invalid axis reference')
        elif not self.sub[axid]['mapplot']:
            print('Subplot is not a Map Plot')
        else:
            self.sub[axid]['features'].append({'fname':filename[lenCfgDir:],'transform':transform,'kwargs':kwargs})

    def add_cfeature(self,featurename,axid=(0,0),**kwargs):
        if not cfeature:
            print('cartopy.feature not loaded')
        elif axid not in self.sub:
            print('Invalid axis reference')
        elif not self.sub[axid]['mapplot']:
            print('Subplot is not a Map Plot')
        else:
            self.sub[axid]['cfeatures'].append({'fname':featurename,'kwargs':kwargs})

    def add_table(self,axid,
                  cellText=None, cellColours=None,
                  cellLoc='right', colWidths=None,
                  rowLabels=None, rowColours=None, rowLoc='left',
                  colLabels=None, colColours=None, colLoc='center',
                  loc='bottom', bbox=None, edges='closed',
                  cellFontSize=None, cellHeight=None,
                  kwargs={}):
        if not isinstance(axid,tuple) and axid in self.sub:
            print('Unrecognized reference object in add_table call ',axid)
            return
        # Ok now do stuff
        self.sub[axid]['table'] = {'ax':axid,'command':{'cmd':'','args':[cellText,cellColours,
                                                                         "'''"+cellLoc+"'''",colWidths,
                                                                         rowLabels,rowColours,"'''"+rowLoc+"'''",
                                                                         colLabels,colColours,"'''"+colLoc+"'''",
                                                                         "'''"+loc+"'''",bbox,"'''"+edges+"'''"],
                                                        'kwargs':kwargs},
                                   'cellParams':{'cellFontSize':cellFontSize,
                                                 'cellHeight':cellHeight}}

    def add_customlegend(self,obj,handles,labels,**kwargs):
        if obj != 'fig' and not (isinstance(obj,tuple) and obj in self.sub):
            print('Unrecognized reference object in add_customlegend ',obj,handles,labels)
            return
        if not isinstance(handles,list) or not isinstance(labels,list) or len(handles) != len(labels):
            print(obj,handles,labels)
            print('Invalid input to parseCommand')
            return
        # Ok now do stuff
        if obj == 'fig':
            thisthing = self.fig
        else:
            thisthing = self.sub[obj]
        newhandles = []
        for a,b,c in handles:
            newc = {}
            for k in c:
                if isinstance(c[k],dict):
                    newc[k] = {}
                    for k1 in c[k]:
                        if isinstance(c[k][k1],str):
                            newc[k][k1] = "'''"+c[k][k1]+"'''"
                        else:
                            newc[k][k1] = c[k][k1]
                elif isinstance(c[k],str):
                    newc[k] = "'''"+c[k]+"'''"
                else:
                    newc[k] = c[k]
            newhandles.append((a,b,newc))
        thisthing['customlegend'] = (newhandles,labels)
        self.parseCommand(obj,'legend',[kwargs])

    def retrievePlot(self,fname):
        if os.path.isfile(fname):
            tempDict = pickle.load(open(fname,'rb'),encoding='latin1')
            if 'fig' in tempDict and 'sub' in tempDict:
                self.fig = deepcopy(tempDict['fig'])
                self.sub = deepcopy(tempDict['sub'])
                if 'lines' in tempDict:
                    self.lines = deepcopy(tempDict['lines'])
                if 'cbs' in tempDict:
                    self.cbs = deepcopy(tempDict['cbs'])
                if 'version' in tempDict:
                    self.version = deepcopy(tempDict['version'])
                else: # set version to prior to version tracking if there's no version
                    self.version = 0.9
            else:
                print('Invalid file.')
        else:
            print('Invalid file.')

    def parseCommand(self,obj,cmd,cargs):
        if obj != 'fig' and not (isinstance(obj,tuple) and obj in self.sub):
            print('Unrecognized reference object in parseCommand ',obj,cmd,cargs)
            return
        if not isinstance(cmd,str):
            print(obj,cmd,cargs)
            print('Invalid input to parseCommand')
            return
        # Ok now do stuff
        if obj == 'fig':
            thisthing = self.fig
        else:
            thisthing = self.sub[obj]
        thisthing['commands'].append({'cmd':cmd,'args':[],'kwargs':{}})
        theobject = thisthing['commands'][-1]
        self.commandParsing(theobject,cargs)

    def parseLineCommand(self,axid,obj,cmd,cargs):
        if not (isinstance(axid,tuple) and axid in self.sub) and \
            not (isinstance(obj,int) and obj < len(self.sub[axid]['lines'])):
            print('Unrecognized reference object in parseLineCommand ',axid,obj,cmd,cargs)
            return
        if not isinstance(cmd,str):
            print(axid,obj,cmd,cargs)
            print('Invalid input to parseLineCommand')
            return
        # Ok now do stuff
        thisthing = self.sub[axid]['lines'][obj]
        thisthing['commands'].append({'cmd':cmd,'args':[],'kwargs':{}})
        theobject = thisthing['commands'][-1]
        self.commandParsing(theobject,cargs)

    def parsePatchCommand(self,axid,obj,cmd,cargs):
        if not (isinstance(axid,tuple) and axid in self.sub) and \
            not (isinstance(obj,int) and obj < len(self.sub[axid]['patches'])):
            print('Unrecognized reference object in parsePatchCommand ',axid,obj,cmd,cargs)
            return
        if not isinstance(cmd,str):
            print(axid,obj,cmd,cargs)
            print('Invalid input to parsePatchCommand')
            return
        # Ok now do stuff
        thisthing = self.sub[axid]['patches'][obj]
        thisthing['commands'].append({'cmd':cmd,'args':[],'kwargs':{}})
        theobject = thisthing['commands'][-1]
        self.commandParsing(theobject,cargs)

    def parseTextCommand(self,axid,obj,cmd,cargs):
        if not (isinstance(axid,tuple) and axid in self.sub) and \
            not (isinstance(obj,int) and obj < len(self.sub[axid]['patches'])):
            print('Unrecognized reference object in parseTextCommand ',axid,obj,cmd,cargs)
            return
        if not isinstance(cmd,str):
            print(axid,obj,cmd,cargs)
            print('Invalid input to parseTextCommand')
            return
        # Ok now do stuff
        thisthing = self.sub[axid]['texts'][obj]
        thisthing['commands'].append({'cmd':cmd,'args':[],'kwargs':{}})
        theobject = thisthing['commands'][-1]
        self.commandParsing(theobject,cargs)

    def commandParsing(self,theobject,cargs):
        for carg in cargs:
            if isinstance(carg,list):
                for car in carg:
                    if isinstance(car,str):
                        theobject['args'].append("'''"+car+"'''")
                    elif isinstance(car,np.ndarray):
                        theobject['args'].append(multiDims(car,[]))
                    else:
                        theobject['args'].append(car)
            elif isinstance(carg,dict):
                for car in carg:
                    if isinstance(carg[car],dict):
                        theobject['kwargs'][car] = {}
                        for k in carg[car]:
                            if isinstance(carg[car][k],str):
                                theobject['kwargs'][car][k] = "'''"+carg[car][k]+"'''"
                            elif isinstance(car, np.ndarray):
                                theobject['kwargs'][car][k] = multiDims(carg[car][k],[])
                            else:
                                theobject['kwargs'][car][k] = carg[car][k]
                    else:
                        if isinstance(carg[car], str):
                            theobject['kwargs'][car] = "'''"+carg[car]+"'''"
                        elif isinstance(car,np.ndarray):
                            theobject['kwargs'][car] = multiDims(carg[car],[])
                        else:
                            theobject['kwargs'][car] = carg[car]

    def reparseCommand(self,obj,cmd,cargs):
        if obj != 'fig' and not (isinstance(obj,tuple) and obj in self.sub):
            print('Unrecognized reference object in reparseCommand ',obj,cmd,cargs)
            return
        if not isinstance(cmd, str) or not isinstance(cargs,list):
            print(obj,cmd,cargs)
            print('Invalid input to parseCommand')
            return

        return
        #For now, don't do stuff
        #Ok now do stuff
        if obj == 'fig':
            thisthing = self.fig
        else:
            thisthing = self.sub[obj]
        thisthing['commands'] = [c for c in thisthing['commands']
                                 if c['cmd'] != cmd]
        self.parseCommand(obj, cmd, cargs)

if __name__ == '__main__':
    if True:
        pltr = Plotter(combinelegend=True)
        ax = pltr.add_subplot()
        x = np.random.randint(0,100,20)
        y = np.random.randint(0,100,20)
        z = np.random.randint(0,100,20)
        pltr.plot(x,y,label='FML')
#        pltr.parseCommand(ax,'text',[[.5,.5,'CarlIsAnIdiot']])
        pltr.add_text(ax,'',[[.5,.5,'CarlIsAnIdiot']])
                      #,c=x,cmap='jet')
#        pltr.add_colorbar((0,0),'jet','Mine',x)
#        pltr.parseCommand((0,0),'legend',[[]])
#        ax1 = pltr.add_subplot((1,0))
#        patchnum = pltr.add_patch(ax1,'Rectangle',[[[0,0],10,10]])
#        pltr.parsePatchCommand(ax1,patchnum,'set_color',[['orange']])
#        pltr.parseCommand(ax1,'set_title',[['FUCK']])
#        linenum = pltr.plot3d(y,x,y,axid=ax1,label='FYL')
#        pltr.parseLineCommand(ax1,linenum,'set_color',[['purple']])
#        l = ['Fudgemylife']
#        h = [([0],[0],dict(markerfacecolor='r',marker='d',color='w'))]
#        pltr.add_customlegend(ax1,h,l,loc='best')
#        ax2 = pltr.add_subplot((2,0))
#        linenum2 = pltr.scatter(y,y,ax2,label='fudge dragon')
#        pltr.parseLineCommand(ax2,linenum2,'set_color',[['red']])
#        pltr.parseCommand(ax2, 'legend', [[]])
#        pltr.share(ax1,ax2,axis='both')
#        ax3 = pltr.add_subplot((3,0))
#        pltr.pie([10,13,14],axid=ax3,autopct='%1.1f%%',labels=['log','bush','branch'])
#        pltr.parseCommand(ax3, 'legend', [[]])
        pltr.createPlot('', PERSIST=True)



