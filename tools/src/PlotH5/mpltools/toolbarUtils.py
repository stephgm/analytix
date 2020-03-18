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

    def makeConnection(self):
        if not self.connectionmade:
            self.xx = mplInteractive.Editing_Picker()
            self.figure.canvas.mpl_connect('pick_event',self.xx.on_pick)
            self.figure.canvas.mpl_connect('button_release_event',self.xx.on_release)
            self.connectionmade = True

    def enable(self, *args):
        self.makeConnection()
        axs = self.figure.get_axes()
        for ax in axs:
            children = ax.properties()['children']
            for child in children:
                if 'set_picker' in child.__dir__():
                    child.set_picker(5)

    def disable(self, *args):
        axs = self.figure.get_axes()
        for ax in axs:
            children = ax.properties()['children']
            for child in children:
                if 'set_picker' in child.__dir__():
                    child.set_picker(None)
                    
        
        
### Add Tool to Toolbar Section
        
def add_Tool(fig,tools=[],**kwargs):
    if 'Heatmap Word Wrap' in tools:
        fig.canvas.manager.toolmanager.add_tool('Heatmap Word Wrap', FixStrings)
        fig.canvas.manager.toolbar.add_tool('Heatmap Word Wrap', 'navigation', 3)
    if 'Editor' in tools:
        fig.canvas.manager.toolmanager.add_tool('Plot Editor', EnableEditing)
        fig.canvas.manager.toolbar.add_tool('Plot Editor', 'navigation',3)
