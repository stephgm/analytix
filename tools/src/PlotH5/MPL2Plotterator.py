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

print(cartopy.config['data_dir'])

if ccrs:
    CfgDir = config['repo_data_dir']
    lenCfgDir = len(CfgDir)+1
    resolution = '10m'



debug = False

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5 import Plotterator
from PlotH5.mpltools import mplUtils as mplu
from PlotH5.mpltools.toolbarUtils import add_Tool

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
            
def PlotterateFig(fig):
    '''
    This function will take in a matplotlib figure object and Plotterate it.
    Some aspects of the plot may NOT carry over perfectly, however, this is a
    WIP.
    
    Inputs:
        fig - matplotlib figure object
    Kwargs:
        N/A
    Returns:
        N/A but subject to change
    
    Figure:
        Issues:
            1. Need to add support for legends
    Axes:
        Issues:
            1. Need to provide better support for legends.  Currently only basic
            ones are made..... somtimes
    

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
        axesGetSets = mplu.getGetsandSets(axes)
        yy = axes.properties()
        # return yy
        '''
        Check to see if first child is quadmesh.. if so.. its a color bar. let plotterator
        handle this below
        '''
        if isinstance(yy['children'][0],matplotlib.collections.QuadMesh):
            continue
        # return yy
        Id = mplu.getAxid(yy['geometry'])
        
        rowspan,colspan = mplu.getSpan(yy['subplotspec'], yy['geometry'])
        axType = mplu.determineAxesType(axes)
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
        
        if Id in twindict and mplu.has_twin(axes):
            pax = pltr.twin(Id)
        elif Id in twindict and not mplu.has_twin(axes):
            pass
        else:
            twindict[Id] = mplu.has_twin(axes)
        
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
                proj = mplu.parseCartopyTransform(child)
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
                marker = mplu.determineMarker(child)
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
                    line = pltr.plot([],[],axid=pax,transform=proj,picker=5)
                else:
                    line = pltr.plot([],[],axid=pax,picker=5)
            elif isinstance(child,matplotlib.collections.PathCollection):
                # return child
                patch = False
                array = child.get_array()
                marker = mplu.determineMarker(child)
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
                            transform=proj,
                            picker=5)]
                else:
                    cargs =[dict(center=(0,0),
                             theta1=0,
                             theta2=0,
                             r=0,
                             picker=5)]
                line = pltr.add_patch(pax,'Wedge',cargs)
            elif isinstance(child,matplotlib.patches.Rectangle):
                patch = True
                if mapplot:
                    cargs = [dict(xy=(0,0),
                                  width=0,
                                  height=0,
                                  transform=proj,
                                  picker=5)]
                else:
                    cargs = [dict(xy=(0,0),
                                  width=0,
                                  height=0,
                                  picker=5)]
                line = pltr.add_patch(pax,'Rectangle',cargs)
            elif isinstance(child,matplotlib.patches.Polygon):
                patch = True
                if mapplot:
                    cargs = [dict(xy=[[0,0],[0,1]],transform=proj,picker=5)]
                else:
                    cargs = [dict(xy=[[0,0],[0,1]],picker=5)]
                line = pltr.add_patch(pax, 'Polygon', cargs)
            elif isinstance(child,matplotlib.patches.Circle):
                patch = True
                if mapplot:
                    cargs = [dict(xy=[0,0],radius=0,transform=proj,picker=5)]
                else:
                    cargs = [dict(xy=[0,0],radius = 0,picker=5)]
                line = pltr.add_patch(pax,'Circle',cargs)
            elif isinstance(child,matplotlib.patches.Ellipse):
                patch = True
                if mapplot:
                    cargs = [dict(xy=[0,0],width=0,height=0,transform=proj,picker=5)]
                else:
                    cargs = [dict(xy=[0,0],width=0,height=0,picker=5)]
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
                    cargs = [dict(xy=points,ec=ec,fc=fc,transform=proj,picker=5)]
                else:
                    cargs = [dict(xy=points,ec=ec,fc=fc,picker=5)]
                line = pltr.add_patch(pax,'Polygon',cargs)
                continue
            else:
                continue
            childGetSets = mplu.getGetsandSets(child)
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
        xticklabels = mplu.getTickLabels(axes,'x')
        yticklabels = mplu.getTickLabels(axes,'y')
        if xticklabels:        
            pltr.parseCommand(pax,'set_xticklabels',[[xticklabels]])
        if yticklabels:
            pltr.parseCommand(pax,'set_yticklabels',[[yticklabels]])
    pltr.createPlot('',PERSIST=True)
    
if __name__ == '__main__':
    x = np.random.randint(0,20,200)
    y = np.random.randint(0,25,200)
    fig = ''
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
    
    if True:
        # fig,ax = plt.subplots()
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
            # ax2 = ax.twinx()
            ax.scatter(y,x,marker='*',c='b',label='who')
            # ax2.legend()
            ax.set_ylabel('What')
        if False:
            #pie chart
            cmap = plt.cm.jet
            plcolor = cmap(np.linspace(0.,1.,3))
            ax.pie([10,23,32],autopct='%.2f%%',colors=plcolor)
            
        if True:
            #basemap plot ugh here we go
            fig = plt.figure()
            ax = plt.axes(projection=ccrs.NorthPolarStereo())
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
            # ax.set_extent([-180,180,-90,90])
            EARTH_IMG = np.load(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy'))
            ax.set_global()
            ax.imshow(EARTH_IMG,
                      origin = 'upper',
                      transform = ccrs.PlateCarree(),
                      extent=[-180,180,-90,90])
            # ax.add_feature(cfeature.COASTLINE)
            # ax.add_feature(cfeature.OCEAN)
            # ax.add_feature(cfeature.LAND)
            # ax.add_feature(cfeature.BORDERS)
            # ax.add_feature(cfeature.LAKES)
            # ax.add_feature(cfeature.RIVERS)
            add_Tool(fig, ['CartopyOptions','SubplotOptions'])
            plt.show()
            
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
        
    
    # if fig:
        # z = PlotterateFig(fig)