#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 02:26:06 2020

@author: klinetry
"""
import numpy as np
import re
from itertools import combinations
import time

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
    patch_extent = patch.get_window_extent(renderer)
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
    goalbbox = patch.get_window_extent(renderer)
    
    #set the annotation bbox center equal to the patches bbox center
    blcorner = np.array(patch.get_xy())
    offsets = np.array((patch.get_width(),patch.get_height()))
    center = blcorner+offsets / 2
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
            
    
def fix_text(event):
    start = time.time()
    patchesdict = {}
    axs = event.canvas.figure.axes
    #Make a mapping for each of the texts and patches
    for ax in axs:
        children = ax.properties()['children']
        for child in children:
            #extract the rectangle patches
            if isinstance(child,matplotlib.patches.Rectangle):
                patchesdict[child] = []
            #AFAIK everything after the spines is useless
            if isinstance(child, matplotlib.spines.Spine):
                break
        for patch in patchesdict:
            #get the bounds of the patch
            patchbbox = patch.get_bbox()
            for child in children:
                #If its an annotation, check to see if it is inside the patch
                if isinstance(child,matplotlib.text.Annotation):
                    annx,anny = child.get_position()
                    if patchbbox.contains(annx,anny):
                        patchesdict[patch].append(child)
        print('setup done',time.time()-start)
        start = time.time()
        renderer = ax.figure.canvas.get_renderer()
        for patch in patchesdict:
            ## Looping over all annotations.. but hoping for just 1
            #only supports 1 annotation currently...
            for ann in patchesdict[patch]:
                reshape_annotation_in_patch(ann,patch,renderer)
        print('reshaped',time.time()-start)
                
                        
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib
    
    fig,ax = plt.subplots()
    
    rstrings = ['This is a long sentence written by Carl','This sentence contains a long word: Supercalifragilisticexpialidocious',
                'This sentence contains normal size words','I am a short','what is this life']
    
    width = 1
    height = 1
    gridsize = 4
    for i in range(gridsize):
        for j in range(gridsize):
            patch = matplotlib.patches.Rectangle((i,j), width, height,lw=1,ls='-',edgecolor='k',facecolor='g')
            ax.add_patch(patch)
            ax.annotate(np.random.choice(rstrings, 1)[0],(i*width+.1,j*height+.1))
    
    ax.set_xlim((-0,gridsize))
    ax.set_ylim((-0,gridsize))
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])
    plt.connect('resize_event', fix_text)
    plt.show()


## unused functions.. but they exist now because of failed/slow attempts
def get_word_sizes(annotation):
    '''
    Gets the size of words in the annotation in Matplotlib font point coordinates
    '''
    text = annotation.get_text()
    words = text.split()
    lengths = list(map(annotation._get_rendered_text_width,words))
    worddict = {}
    for i,word in enumerate(words):
        if word != words[-1]:
            word = word+' '
        worddict[word] = lengths[i]
    return worddict
