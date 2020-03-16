#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 13:15:01 2020

@author: Carl Marlow
"""


'''
Matplotlib Utils.  Contains a class that adds doodads to the mpl toolbar

'''

import numpy as np
import re
from itertools import combinations
import matplotlib.pyplot as plt
import matplotlib

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from collections import OrderedDict
import struct
import binascii
from six import string_types

mplcolors = ['black','green','red','blue','orange','white','yellow']
cmaps = sorted(m for m in plt.cm.datad if not m.endswith("_r"))

namedcolorsRGBlookup = {}
x = matplotlib.colors.get_named_colors_mapping()
for key in x:
    if not isinstance(x[key],tuple):
        namedcolorsRGBlookup[key.replace('xkcd:','')]=matplotlib.colors.to_rgb(x[key])
    elif isinstance(x[key],tuple) and isinstance(x[key][0],str) and '#' in x[key][0]:
        namedcolorsRGBlookup[key.replace('xkcd:','')]=tuple(map(lambda x: np.array(x)/255.,struct.unpack('BBB',x[key][0].strip('#'))))
    else:
        namedcolorsRGBlookup[key.replace('xkcd:','')]=tuple(map(float,x[key]))

namedcolorsHEXlookupfromNAME = {}
for key in x:
    namedcolorsHEXlookupfromNAME[key.replace('xkcd:','')] = matplotlib.colors.to_hex(x[key])
#    if isinstance(x[key],string_types):
#        namedcolorsHEXlookupfromNAME[key.replace('xkcd:','')]=x[key]
#    elif isinstance(x[key],tuple):
#        break
#        val = np.array(x[key])*255.
#        val = '#%02x%02x%02x' % tuple(val)
#        namedcolorsHEXlookupfromNAME[key.replace('xkcd:','')]=val

namedcolorsNAMElookupfromHEX = {}
for k,v in namedcolorsHEXlookupfromNAME.items():
    namedcolorsNAMElookupfromHEX[str(v)] = k

namedcolorsNAMElookup = {}
for k,v in namedcolorsRGBlookup.items():
    namedcolorsNAMElookup[str(v)]=k

plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase


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
    
    #set the annotation bbox center equal to the patches bbox center
    
    if isinstance(patch,matplotlib.patches.Rectangle):
        offsets = np.array((patch.get_width(),patch.get_height()))
        blcorner = np.array(patch.get_xy())
        center = blcorner+offsets / 2
    elif isinstance(patch,matplotlib.patches.Circle):
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
            if isinstance(child,(matplotlib.patches.Rectangle,matplotlib.patches.Circle)):
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
        
def makeRGBAfromReturn(cname,alpha,**kwargs):
    rgb = namedcolorsRGBlookup[cname]
    rgba = tuple(rgb,) + tuple([float(alpha)])
    return rgba

class RGBAWidget(Widgets.QWidget):
    def __init__(self,origvalue,parent=None,**kwargs):
        super(RGBAWidget,self).__init__(parent)

        if isinstance(origvalue,string_types) and '#' not in origvalue and isinstance(eval('origvalue'),string_types):
            origvalue = namedcolorsRGBlookup[origvalue]
        elif isinstance(origvalue,string_types) and '#' not in origvalue and isinstance(eval('origvalue'),tuple):
            origvalue = eval(origvalue)
        elif isinstance(origvalue,string_types):
            origvalue = namedcolorsNAMElookupfromHEX[origvalue]
            origvalue = namedcolorsRGBlookup[origvalue]
        if not isinstance(origvalue,tuple):
            print('thhis is not a tuple')


        self.makeAlpha = kwargs.get('alpha',True)
        self.givenAlpha = kwargs.get('rgba',True)
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)

        self.ColorCombo = self.buildCombo(namedcolorsRGBlookup.keys(),origvalue)
        self.layout.addWidget(self.ColorCombo,0,0)

        if self.makeAlpha:
            self.layout.addWidget(Widgets.QLabel('Alpha'),0,1)
            self.AlphaLine = Widgets.QLineEdit()
            self.AlphaLine.setReadOnly(True)
            self.AlphaLine.setValidator(Gui.QDoubleValidator())
            self.layout.addWidget(self.AlphaLine)
            if self.givenAlpha:
                self.AlphaLine.setText(str(origvalue[-1]))
            else:
                self.AlphaLine.setText('1.')

    def buildCombo(self,items,origval):
        widget = Widgets.QComboBox()
        widget.addItems(items)
        #do a reverse lookup since you will be given rgba
        if self.givenAlpha:
            #Strip off the alpha part
            origval = origval[:-1]
        reversedlookup = namedcolorsNAMElookup[str(origval)]
        index = widget.findText(reversedlookup)
        widget.setCurrentIndex(index)
        return widget

class TextOptions(Widgets.QDialog):
    def __init__(self,artist,parent=None):
        super(TextOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Text options')

        self.setupTextOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupTextOptions(self):
        self.widgets = OrderedDict()
        self.widgets['Text'] = Widgets.QLineEdit(self.artist.get_text())
        self.widgets['Text Color'] = RGBAWidget(self.artist.get_color(),alpha=False,rgba=False)
        self.widgets['Text Size'] = Widgets.QLineEdit(str(self.artist.get_fontsize()))
        self.widgets['Text Size'].setValidator(Gui.QDoubleValidator())
        self.widgets['Text Font'] = Widgets.QComboBox()
        self.widgets['Text Font'].addItems(['impact','dejavu sans'])

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])


    def Accept(self):
        #Just to make sure it is still clickable when user stupidly sets it to nothing and hits okay
        if not self.widgets['Text'].text():
            self.widgets['Text'].setText(' ')
        self.artist.set_text(self.widgets['Text'].text())
        self.artist.set_color(namedcolorsRGBlookup[self.widgets['Text Color'].ColorCombo.currentText()])
        self.artist.set_fontsize(self.widgets['Text Size'].text())
        self.artist.set_fontname({self.widgets['Text Font'].currentText()})
        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()

class CollectionsOptions(Widgets.QDialog):
    def __init__(self,artist,legend,parent=None):
        super(CollectionsOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Scatter Options')

        self.hascbar = self.determineColorbar()

        self.setupLineOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()
        self.legline = ''

        for line in legend.get_lines():
            if line.get_label() == self.artist.get_label():
                self.legline = line
                break

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def determineColorbar(self):
        #TODO Most likely this will work.. unless all your values are the same with the colorbar
        colors = self.artist.get_facecolor()
        if len(colors) == 1:
            return False
        else:
            return True


    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupLineOptions(self):
        self.widgets = OrderedDict()

        if not self.hascbar:
            self.widgets['Marker Face Color'] = RGBAWidget(tuple(self.artist.get_facecolor()[0]))
            self.widgets['Marker Edge Color'] = RGBAWidget(tuple(self.artist.get_edgecolor()[0]))
        else:
            self.buildCombo('Color Map',cmaps,self.artist.get_cmap().name)
        self.widgets['Marker Size'] = Widgets.QLineEdit(str(self.artist.get_sizes()[0]))
        self.widgets['Marker Size'].setValidator(Gui.QDoubleValidator())

        self.widgets['Line Label'] = Widgets.QLineEdit(self.artist.get_label())

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])

    def Accept(self):
        #Need to make a color to rgb mapper
        if not self.hascbar:
            self.artist.set_facecolors(np.array(makeRGBAfromReturn(self.widgets['Marker Face Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Face Color'].AlphaLine.text())))
            self.artist.set_edgecolors(np.array(makeRGBAfromReturn(self.widgets['Marker Edge Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Edge Color'].AlphaLine.text())))
        else:
            self.artist.set_cmap(matplotlib.cm.get_cmap(self.widgets['Color Map'].currentText()))

        self.artist.set_sizes(np.array([float(self.widgets['Marker Size'].text())]))

        self.artist.set_label(self.widgets['Line Label'].text())

        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()

class Line2DOptions(Widgets.QDialog):
    def __init__(self,artist,legend,parent=None):
        super(Line2DOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('2D Line Options')

        self.setupLineOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()
        self.legline = ''

        for line in legend.get_lines():
            if line.get_label() == self.artist.get_label():
                self.legline = line
                break

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupLineOptions(self):
        self.widgets = OrderedDict()

        self.widgets['Line Color'] = RGBAWidget(self.artist.get_color(),alpha=False,rgba=False)

        self.buildCombo('Marker',['','.','*'],self.artist.get_marker())
        self.widgets['Marker Face Color'] = RGBAWidget(self.artist.get_markerfacecolor(),alpha=False,rgba=False)
        self.widgets['Marker Edge Color'] = RGBAWidget(self.artist.get_markeredgecolor(),alpha=False,rgba=False)
        self.widgets['Marker Size'] = Widgets.QLineEdit(str(self.artist.get_markersize()))
        self.widgets['Marker Size'].setValidator(Gui.QDoubleValidator())
        self.widgets['Marker Edge Width'] = Widgets.QLineEdit(str(self.artist.get_markeredgewidth()))
        self.widgets['Marker Edge Width'].setValidator(Gui.QDoubleValidator())

        self.buildCombo('Line Style',['-','-.',':','--'],self.artist.get_linestyle())
        self.widgets['Line Width'] = Widgets.QLineEdit(str(self.artist.get_linewidth()))
        self.widgets['Line Width'].setValidator(Gui.QDoubleValidator())

        self.widgets['Line Label'] = Widgets.QLineEdit(self.artist.get_label())

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])

    def Accept(self):
        self.artist.set_color(namedcolorsHEXlookupfromNAME[self.widgets['Line Color'].ColorCombo.currentText()])
        if self.legline:
            self.legline.set_color(namedcolorsHEXlookupfromNAME[self.widgets['Line Color'].ColorCombo.currentText()])

        self.artist.set_marker(self.widgets['Marker'].currentText())
        self.artist.set_markerfacecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Face Color'].ColorCombo.currentText()])
        self.artist.set_markeredgecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Edge Color'].ColorCombo.currentText()])
        self.artist.set_markersize(self.widgets['Marker Size'].text())
        self.artist.set_markeredgewidth(self.widgets['Marker Edge Width'].text())
        if self.legline:
            self.legline.set_marker(self.widgets['Marker'].currentText())
            self.legline.set_markerfacecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Face Color'].ColorCombo.currentText()])
            self.legline.set_markeredgecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Edge Color'].ColorCombo.currentText()])
            self.legline.set_markersize(self.widgets['Marker Size'].text())
            self.legline.set_markeredgewidth(self.widgets['Marker Edge Width'].text())

        self.artist.set_linestyle(self.widgets['Line Style'].currentText())
        self.artist.set_linewidth(self.widgets['Line Width'].text())
        if self.legline:
            self.legline.set_linestyle(self.widgets['Line Style'].currentText())
            self.legline.set_linewidth(self.widgets['Line Width'].text())

        self.artist.set_label(self.widgets['Line Label'].text())
        if self.legline:
            self.legline.set_label(self.widgets['Line Label'].text())

        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()

class PatchesOptions(Widgets.QDialog):
    def __init__(self,artist,parent=None):
        super(PatchesOptions,self).__init__(parent)
        self.parent = parent
        self.artist = artist
        self.layout = Widgets.QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Scatter Options')

        self.hascbar = self.determineColorbar()

        self.setupLineOptions()

        self.Ok = Widgets.QPushButton('Ok')
        self.Cancel = Widgets.QPushButton('Cancel')
        self.layout.addWidget(self.Ok)
        self.layout.addWidget(self.Cancel)
        self.makeConnections()

    def makeConnections(self):
        self.Ok.clicked.connect(lambda trash:self.Accept())
        self.Cancel.clicked.connect(lambda trash:self.Reject())

    def determineColorbar(self):
        #TODO Most likely this will work.. unless all your values are the same with the colorbar
        colors = self.artist.get_facecolor()
        if len(colors) == 1:
            return False
        else:
            return True

    def buildCombo(self,name,items,origval):
        self.widgets[name] = Widgets.QComboBox()
        self.widgets[name].addItems(items)
        index = self.widgets[name].findText(origval)
        self.widgets[name].setCurrentIndex(index)

    def setupLineOptions(self):
        self.widgets = OrderedDict()

        if not self.hascbar:
            self.widgets['Marker Face Color'] = RGBAWidget(tuple(self.artist.get_facecolor()[0]))
            self.widgets['Marker Edge Color'] = RGBAWidget(tuple(self.artist.get_edgecolor()[0]))
        else:
            self.buildCombo('Color Map',cmaps,self.artist.get_cmap().name)

        for key in self.widgets:
            self.layout.addWidget(Widgets.QLabel(key))
            self.layout.addWidget(self.widgets[key])

    def Accept(self):
        #Need to make a color to rgb mapper
        if not self.hascbar:
            self.artist.set_facecolor(makeRGBAfromReturn(self.widgets['Marker Face Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Face Color'].AlphaLine.text()))
            self.artist.set_edgecolor(makeRGBAfromReturn(self.widgets['Marker Edge Color'].ColorCombo.currentText(),
                                                                   self.widgets['Marker Edge Color'].AlphaLine.text()))
        else:
            self.artist.set_cmap(matplotlib.cm.get_cmap(self.widgets['Color Map'].currentText()))

        self.artist.figure.canvas.draw()
        self.close()

    def Reject(self):
        self.close()



# fig,ax = plt.subplots()
class Editing_Picker(object):
    def __init__(self,*args,**kwargs):
        self.ann_list = []
        
    def on_pick(self,event):
        if event.mouseevent.button == 1:
            if isinstance(event.artist,matplotlib.text.Text):
                text = event.artist
                dialog = TextOptions(text)
                dialog.exec_()
    
            elif isinstance(event.artist,matplotlib.lines.Line2D):
                line = event.artist
                legend = event.artist.axes.legend()
                dialog = Line2DOptions(line,legend)
                dialog.exec_()
    
            elif isinstance(event.artist,matplotlib.collections.PathCollection):
                collection = event.artist
                legend = event.artist.axes.legend()
                dialog = CollectionsOptions(collection,legend)
                dialog.exec_()
    
            elif isinstance(event.artist,matplotlib.collections.PolyCollection):
                patch = event.artist
                dialog = PatchesOptions(patch)
                dialog.exec_()
    
            else:
                print(event.artist)
        elif event.mouseevent.button == 2:
            try:
                line = event.artist
                xdata = line.get_xdata()
                ydata = line.get_ydata()
                ind = event.ind
                ax = line.axes
                ann = ax.annotate(line.get_label(),(xdata[ind[0]],ydata[ind[0]]))
                self.ann_list.append(ann)
                line.figure.canvas.draw()
            except:
                pass
    
    def on_release(self,event):
        for ann in self.ann_list:
            ann.remove()
            self.ann_list.remove(ann)
        event.canvas.draw()
    
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
            self.xx = Editing_Picker()
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
