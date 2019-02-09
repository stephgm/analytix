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
exclude_list = ['x','y','fmt']
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
        for row in range(self.fig['nrows']):
            for col in range(self.fig['ncols']):
                if reftype == 2:
                    thisax = ax[row][col]
                elif reftype == 1:
                    thisax = ax[row+col]
                else:
                    thisax = ax
                for line in self.sub[(row,col)]['lines']:
                    thisax.plot(line['x'],line['y'],line['fmt'],
                                **{k:line[k] for k in line
                                   if k not in exclude_list})
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
                            ax2.plot(line['x'],line['y'],line['fmt'],
                                        **{k:line[k] for k in line
                                           if k not in exclude_list})
                        if self.sub[t]['commands']:
                            for command in self.sub[t]['commands']:
                                if command['cmd'] not in special_cmds:
                                    execString = "ax2."+self.buildExecString(command)
                                    exec(execString,{},{"ax2":ax2})
                        ax2.format_coord = general_format_coord(ax2,thisax)
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
        self.sub[axid]['lines'][-1]['x'] = x
        self.sub[axid]['lines'][-1]['y'] = y
        self.sub[axid]['lines'][-1]['fmt'] = fmt
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
        thisthing['commands'].append({'cmd':'','args':[],'kwargs':{}})
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
    pass
        