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
import numpy as np
import re
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib

# plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase

    
if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(sys.executable))
print(RELATIVE_LIB_PATH)
from PlotH5 import mplInteractive

### Heatmap Word Wrapping Toolbar


class FixStrings(ToolBase):
    '''Fix words inside rectangle patches'''
    # keyboard shortcut
    default_keymap = 'w'
    description = 'Wrap Text'

    def trigger(self, *args, **kwargs):
        axs = self.figure.get_axes()
        fix_text(axs)
        self.figure.canvas.draw()
        
        
def create_bbox(blcorner,trcorner):
    '''
    Some patches in mpl do not have a .get_bbox call.. So this will make one
    '''
    return matplotlib.transforms.Bbox([list(blcorner),list(trcorner)])

def get_max_lines(annotation,patch,renderer):
    '''
    Simple function... after a few hours of thinking about it.
    Takes annotation text, strips out all newlines and double spaces.  Then
    calculates the maximum width of that rendered text in Matplotlib font point
    coordinates.  We see how many words the text contains and then calculate
    the ideal scenario of splitting the text up with newlines.  If the ideal
    split is less than the number of words, we are onto something.  Else, this
    tells me that our maximum number of lines is the number of words - 1.
    
    Input:
        annotation - the annotation class object from matplotlib
        patch - the Rectangle patch (Maybe the only one that works) class object form mpl
    
    Kwargs:
        N/A
    Returns:
        Returns maximum number of lines that should be implemented for word wrapping
    '''
    if isinstance(patch,matplotlib.patches.Rectangle):
        patch_extent = patch.get_extents()
    elif isinstance(patch,matplotlib.patches.Circle):
        # Got to inscribe the circle with a square, so that all of our text is inside
        # Also, gotta put this in MPL point coords
        gbbox = patch.get_window_extent(renderer)
        center = np.array((gbbox.xmax-gbbox.width/2,gbbox.ymax-gbbox.height/2))
        gbboxarea = gbbox.width*gbbox.height
        nggboxarea = gbboxarea/2
        ngbboxside = np.sqrt(nggboxarea)
        blcorner = list(center-ngbboxside/2)
        trcorner = list(center+ngbboxside/2)
        patch_extent = create_bbox(blcorner, trcorner)
    elif isinstance(patch,matplotlib.patches.Ellipse):
        #Got to inscribe the ellipse with a rectangle, so that all our text is inside
        gbbox = patch.get_window_extent(renderer)
        center = np.array((gbbox.xmax-gbbox.width/2,gbbox.ymax-gbbox.height/2))
        b = gbbox.height/2
        a = gbbox.width/2
        blcorner = [center[0]-a/np.sqrt(2),center[1]-b/np.sqrt(2)]
        trcorner = [center[0]+a/np.sqrt(2),center[1]+b/np.sqrt(2)]
        patch_extent = create_bbox(blcorner, trcorner)
        
    patch_width = patch_extent.width
    ogtext = annotation.get_text()
    stripped_text = ogtext.replace('\n',' ').replace('  ',' ').replace('  ',' ')
    numwords = len(stripped_text.split())
    try:
        max_width = annotation._get_rendered_text_width(stripped_text)
    except:
        return 1
    ideal_lines = np.ceil(max_width/patch_width)
    if ideal_lines < numwords:
        return int(ideal_lines)
    else:
        return numwords-1
    
                

def replace_substring_occurences(string,substring,replacement,occurences=[],**kwargs):
    '''
    This function replaces certain substring occurences with a replacement text
    
    Input:
        string - the original string
        substring - the substring that you want to replace
        replacement - the string you want to substitute in
        occurences - list of ints of the occurence number that you want to replace
                     This is not zero indexed
    
    Kwargs:
        allcombs - do every combination of occurences
        combs - do every combination of the passed occurences
    
    Return:
        Returns a list of strings that follow the criteria.  Returns a list
        based solely on the fact of the combination kwargs
    '''
    allcombs = kwargs.get('allcombs',False)
    combs = kwargs.get('combs',False)
    sublist = [m.start() for m in re.finditer(substring,string)]
    slist = []
    if allcombs:
        subcombinations = [x for l in range(1,len(sublist)+1) for x in combinations(sublist,l)]
        for combo in subcombinations:
            y = string
            for subloc in reversed(combo):
                before = y[:subloc]
                after = y[subloc+len(substring):]
                y = f'{before}{replacement}{after}'
            slist.append(y)
        return slist
    if combs:
        occurences = [o for o in occurences if o < len(sublist)]
        sublist = [sublist[x-1] for x in occurences]
        subcombinations = [x for l in range(1,len(sublist)+1) for x in combinations(sublist,l)]
        for combo in subcombinations:
            y = string
            for subloc in reversed(combo):
                before = y[:subloc]
                after = y[subloc+len(substring):]
                y = f'{before}{replacement}{after}'
            slist.append(y)
        return slist
    #This is the one I wound up using...
    y = string
    occurences = [o for o in occurences if o < len(sublist)]
    sublist = [sublist[x-1] for x in occurences]
    for subloc in reversed(sublist):
        before = y[:subloc]
        after = y[subloc+len(substring):]
        y = f'{before}{replacement}{after}'
    slist.append(y)
    return slist
                
        
def reshape_annotation_in_patch(annotation,patch,renderer):
    '''
    The goal of this function is to minimize the text in such a way that it
    maximizes the usage of the goal bounding box, while still fitting inside
    the patches bounding box.  Well documented below.
    '''
    #set the alignments to center
    annotation.set_horizontalalignment('center')
    annotation.set_verticalalignment('center')
    
    #Get the extent of the patch in terms of matplotlib points
    if isinstance(patch,matplotlib.patches.Rectangle):
        goalbbox = patch.get_extents()
    elif isinstance(patch,matplotlib.patches.Circle):
        # Got to inscribe the circle with a square, so that all of our text is inside
        # Also, gotta put this in MPL point coords
        gbbox = patch.get_window_extent(renderer)
        center = np.array((gbbox.xmax-gbbox.width/2,gbbox.ymax-gbbox.height/2))
        gbboxarea = gbbox.width*gbbox.height
        nggboxarea = gbboxarea/2
        ngbboxside = np.sqrt(nggboxarea)
        blcorner = list(center-ngbboxside/2)
        trcorner = list(center+ngbboxside/2)
        goalbbox = create_bbox(blcorner, trcorner)
    elif isinstance(patch,matplotlib.patches.Ellipse):
        #Got to inscribe the ellipse with a rectangle, so that all our text is inside
        gbbox = patch.get_window_extent(renderer)
        center = np.array((gbbox.xmax-gbbox.width/2,gbbox.ymax-gbbox.height/2))
        b = gbbox.height/2
        a = gbbox.width/2
        blcorner = [center[0]-a/np.sqrt(2),center[1]-b/np.sqrt(2)]
        trcorner = [center[0]+a/np.sqrt(2),center[1]+b/np.sqrt(2)]
        goalbbox = create_bbox(blcorner, trcorner)
    
    #set the annotation bbox center equal to the patches bbox center
    
    if isinstance(patch,matplotlib.patches.Rectangle):
        offsets = np.array((patch.get_width(),patch.get_height()))
        blcorner = np.array(patch.get_xy())
        center = blcorner+offsets / 2
    elif isinstance(patch,(matplotlib.patches.Circle,matplotlib.patches.Ellipse)):
        center = patch.center
    annotation.set_x(center[0])
    annotation.set_y(center[1])
    
    #Get the original text and fontsize in case we just want to reset everything 
    # when no solution is found
    ogtext = annotation.get_text()
    # ogfontsize = annotation.get_size()
    
    #Strip all the new lines from the text, and make sure there are no double spaces
    stripped_text = ogtext.replace('\n',' ').replace('  ',' ').replace('  ',' ')
    annotation.set_text(stripped_text)
    
    
    #setting the fontsize to 30.. this is the maximum font size that will show up
    #This also may be the greatest source of slowdown.. smaller = better
    fontsize = 30
    annotation.set_size(fontsize)
    
    #Assuming that the resulting annotation bounding box does not fit in the patch bounding box
    fits = False
    while fontsize > 2 and not fits:
        
        #Getting the maximum number of lines
        maxlines = get_max_lines(annotation, patch, renderer)
        # if maxlines == 0:
            # fontsize -= 1
            # annotation.set_size(fontsize)
        # else:
        #Finding all the locations of spaces (These have potential to be newlines)
        spacelocs = [m.start() for m in re.finditer(' ',stripped_text)]
        
        #Get the length of text with no newlines
        phrase_len = len(stripped_text)
        
        #This will house the occurences of spaces we want to convert to newlines
        occurences = []
        
        #Loop over the maxlines... Find the ideal splitting location for a newline..
        #This may not be acceptable, because it could try to split a word..
        #So we find the space location that is closest to ideal split location
        #and add it to the occurences list
        for i in range(maxlines):
            ideal_split = (i*phrase_len)/maxlines
            index = np.argmin(np.abs(np.array(spacelocs)-ideal_split))
            occurences.append(index)
            
        #Based on our split positions... we replace those occurences with newlines
        nstring = replace_substring_occurences(stripped_text, ' ', '\n', occurences)[0]
        
        #Set the annotation text to this new string so we can get the Matplotlib
        #font point coordinates to test if it now fits inside the patch bounding box
        annotation.set_text(nstring)
        nannbbox = annotation.get_window_extent(renderer)
        fits = True
        for i,corner in enumerate(nannbbox.corners()):
            if not goalbbox.contains(corner[0],corner[1]):
                fits = False
                break
            
        #If it doesn't fit... reduce fontsize by 1... and do it all again.
        if not fits:
            fontsize -= 1
            annotation.set_size(fontsize)
            
    
def fix_text(axs):
    patchesdict = {}
    #Make a mapping for each of the texts and patches
    for ax in axs:
        renderer = ax.figure.canvas.get_renderer()
        children = ax.properties()['children']
        for child in children:
            #extract the rectangle patches
            if isinstance(child,(matplotlib.patches.Rectangle,matplotlib.patches.Circle,matplotlib.patches.Ellipse)):
                patchesdict[child] = []
            #AFAIK everything after the spines is useless
            if isinstance(child, matplotlib.spines.Spine):
                break
        for patch in patchesdict:
            #get the bounds of the patch
            if isinstance(patch, matplotlib.patches.Rectangle):
                patchbbox = patch.get_bbox()
            elif isinstance(patch, matplotlib.patches.Circle):
                center = np.array(patch.center)
                blcorner = list(center-patch.radius)
                trcorner = list(center+patch.radius)
                patchbbox = create_bbox(blcorner, trcorner)
            elif isinstance(patch, matplotlib.patches.Ellipse):
                #TODO fix wrt angle of orientation
                center = np.array(patch.center)
                blcorner = [center[0]-patch.width/2,center[1]-patch.height/2]
                trcorner = [center[0]+patch.width/2,center[1]+patch.height/2]
                patchbbox = create_bbox(blcorner,trcorner)
                
            for child in children:
                #If its an annotation, check to see if it is inside the patch
                if isinstance(child,matplotlib.text.Annotation):
                    annx,anny = child.get_position()
                    if patchbbox.contains(annx,anny):
                        patchesdict[patch].append(child)
                if isinstance(child, matplotlib.spines.Spine):
                    break
        for patch in patchesdict:
            ## Looping over all annotations.. but hoping for just 1
            #only supports 1 annotation currently...
            for ann in patchesdict[patch]:
                reshape_annotation_in_patch(ann,patch,renderer)
                  
        
### Editor

class EnableEditing(ToolToggleBase):
    '''Enable Picking for all objects that allow it'''
    default_keymap = 'E'
    description = 'Enable Editing for the current Figure'
    default_toggled = False

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
