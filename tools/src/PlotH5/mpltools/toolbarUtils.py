#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 13:15:01 2020

@author: Carl Marlow
"""


'''
Matplotlib Utils.  Contains a class that adds doodads to the mpl toolbar

'''
import sys
import os
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(sys.executable))
from PlotH5 import mplInteractive
from PlotH5.mpltools import PatchWordWrap
from PlotH5.mpltools import SubplotOptions
from PlotH5.mpltools import MapPlotOptions

### Heatmap Word Wrapping Toolbar

class FixStrings(ToolBase):
    '''Fix words inside rectangle patches'''
    # keyboard shortcut
    default_keymap = 'w'
    description = 'Wrap Text'
    image = os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarIcons','wordwrap.png')

    def trigger(self, *args, **kwargs):
        axs = self.figure.get_axes()
        PatchWordWrap.fix_text(axs)
        self.figure.canvas.draw()
        
### Subplot Options

class SubPlotOptions(ToolBase):
    '''Enable Editing of a few options for axes'''
    default_keymap = 'A'
    description = 'Subplot options for current Figure (Eg. Set X limit)'
    image = os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarIcons','settings.jpg')
    
    def trigger(self,*args,**kwargs):
        SubplotOptions.edit_subplots(self.figure)
        self.figure.canvas.draw()
        
### Cartopy Options

class CartopyOptions(ToolBase):
    '''Enable Options for Cartopy Plots'''
    default_keymap = 'M'
    description = 'Map Plot Options for Current Axes'
    image = os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarIcons','globe.png')
    
    def trigger(self,*args,**kwargs):
        MapPlotOptions.edit_map(self.figure)
        self.figure.canvas.draw()

### Editor

class EnableEditing(ToolToggleBase):
    '''Enable Picking for all objects that allow it'''
    default_keymap = 'E'
    description = 'Enable Editing for the current Figure'
    default_toggled = False
    image = os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarIcons','plotedit.png')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connectionmade = False
        self.xx = mplInteractive.Editing_Picker()

    def makeConnection(self):
        if not self.connectionmade:
            self.cid_pe = self.figure.canvas.mpl_connect('pick_event',self.xx.on_pick)
            self.cid_bre = self.figure.canvas.mpl_connect('button_release_event',self.xx.on_release)
            self.connectionmade = True

    def enable(self, *args):
        self.makeConnection()
        axs = self.figure.get_axes()
        fig_children = self.figure.properties()['children']
        for child in fig_children:
            if 'set_picker' in child.__dir__():
                child.set_picker(5)
        for ax in axs:
            ax.set_ylabel(ax.get_ylabel(),picker=5)
            ax.set_xlabel(ax.get_xlabel(),picker=5)
            children = ax.properties()['children']
            for child in children:
                if 'set_picker' in child.__dir__():
                    child.set_picker(5)

    def disable(self, *args):
        axs = self.figure.get_axes()
        fig_children = self.figure.properties()['children']
        for child in fig_children:
            if 'set_picker' in child.__dir__():
                child.set_picker(None)
        for ax in axs:
            ax.set_ylabel(ax.get_ylabel(),picker=None)
            ax.set_xlabel(ax.get_ylabel(),picker=None)
            children = ax.properties()['children']
            for child in children:
                if 'set_picker' in child.__dir__():
                    child.set_picker(None)
        self.figure.canvas.mpl_disconnect(self.cid_pe)
        self.figure.canvas.mpl_disconnect(self.cid_bre)
        self.connectionmade = False


### Add Tool to Toolbar Section

def add_Tool(fig,tools=[],**kwargs):
    if not isinstance(tools,list):
        tools = [tools]
    if 'Heatmap Word Wrap' in tools:
        fig.canvas.manager.toolmanager.add_tool('Heatmap Word Wrap', FixStrings)
        fig.canvas.manager.toolbar.add_tool('Heatmap Word Wrap', 'navigation', 3)
    if 'Editor' in tools:
        fig.canvas.manager.toolmanager.add_tool('Plot Editor', EnableEditing)
        fig.canvas.manager.toolbar.add_tool('Plot Editor', 'navigation',3)
    if 'SubplotOptions' in tools:
        fig.canvas.manager.toolmanager.add_tool('Subplot Options',SubPlotOptions)
        fig.canvas.manager.toolbar.add_tool('Subplot Options', 'navigation',3)
    if 'CartopyOptions' in tools:
        fig.canvas.manager.toolmanager.add_tool('Cartopy Options',CartopyOptions)
        fig.canvas.manager.toolbar.add_tool('Cartopy Options','navigation',3)
