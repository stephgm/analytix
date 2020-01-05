# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 18:07:25 2019

@author: Jordan
"""

import matplotlib.pyplot as plt
import matplotlib
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from collections import OrderedDict
import numpy as np
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
        self.legline.set_color(namedcolorsHEXlookupfromNAME[self.widgets['Line Color'].ColorCombo.currentText()])

        self.artist.set_marker(self.widgets['Marker'].currentText())
        self.artist.set_markerfacecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Face Color'].ColorCombo.currentText()])
        self.artist.set_markeredgecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Edge Color'].ColorCombo.currentText()])
        self.artist.set_markersize(self.widgets['Marker Size'].text())
        self.artist.set_markeredgewidth(self.widgets['Marker Edge Width'].text())
        self.legline.set_marker(self.widgets['Marker'].currentText())
        self.legline.set_markerfacecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Face Color'].ColorCombo.currentText()])
        self.legline.set_markeredgecolor(namedcolorsHEXlookupfromNAME[self.widgets['Marker Edge Color'].ColorCombo.currentText()])
        self.legline.set_markersize(self.widgets['Marker Size'].text())
        self.legline.set_markeredgewidth(self.widgets['Marker Edge Width'].text())

        self.artist.set_linestyle(self.widgets['Line Style'].currentText())
        self.artist.set_linewidth(self.widgets['Line Width'].text())
        self.legline.set_linestyle(self.widgets['Line Style'].currentText())
        self.legline.set_linewidth(self.widgets['Line Width'].text())

        self.artist.set_label(self.widgets['Line Label'].text())
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

def on_pick(event):
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

# ax.scatter([1,2,3,4],[4,5,6,7],picker=5,label='FUN',c='red',cmap=None)
# sc = ax.scatter([5,6,7,8],[4,5,6,7],picker=5,label='Not Fun',c=[1,2,3,4],cmap=plt.cm.get_cmap('flag'))
# fig.colorbar(sc).set_label('nol',picker=5)
# ax.plot([5,6,10,11],[10,11,12,13],picker=5,label='Not Fun',c='blue')
# ax.stackplot([1,2,3,4],[4,5,6,7],picker=5,color='blue')
# ax.legend()
# ax.set_ylabel('Yes',picker=5)
# ax.set_xlabel('No',picker=5)
# ax.set_title('This is a Plot',picker=5)

# fig.canvas.mpl_connect('pick_event',on_pick)

# plt.show()


