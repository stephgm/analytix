# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 01:34:35 2020

@author: cjmar
"""


import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.QtCore as Core
from PyQt5 import uic
import numpy as np
from six import string_types
plt.rcParams['toolbar'] = 'toolmanager'
import cartopy.crs as ccrs
import cartopy

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)

from PlotH5.mpltools import mplDefaults as mpld
from PlotH5.mpltools import mplUtils as mplu



if not os.path.isfile(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy')):
    np.save(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy'),plt.imread(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.png')))
BMHD = os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_21600x10800.npy')
if not os.path.isfile(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.npy')):
    np.save(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.npy'),plt.imread(os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.png')))
BMSD = os.path.join(RELATIVE_LIB_PATH,'data','bluemarble_8192x4096.npy')

class map_plot_options(Widgets.QDialog):
    def __init__(self,fig,parent=None):
        super(map_plot_options,self).__init__(parent)
        uic.loadUi(os.path.join(RELATIVE_LIB_PATH,'PlotH5','mpltools','toolbarUIs','mapplotoptions.ui'),self)
        
        self.parent = parent
        self.setWindowTitle('Map Plot Options')
        self.fig = fig
        self.axlookup = {}
        self.axlist = []
        self.makeConnections()
        self.populate_axes_combo()
        self.populate_options(0)
        
    def makeConnections(self):
        self.AxesCombo.currentIndexChanged.connect(self.populate_options)
        self.UpperLon.textChanged.connect(lambda trash:self.set_extents())
        self.LowerLon.textChanged.connect(lambda trash:self.set_extents())
        self.UpperLat.textChanged.connect(lambda trash:self.set_extents())
        self.LowerLat.textChanged.connect(lambda trash:self.set_extents())
        self.BordersChk.toggled.connect(lambda trash:self.set_cfeatures())
        self.LakesChk.toggled.connect(lambda trash:self.set_cfeatures())
        self.RiversChk.toggled.connect(lambda trash:self.set_cfeatures())
        self.OceanChk.toggled.connect(lambda trash:self.set_cfeatures())
        self.LandChk.toggled.connect(lambda trash:self.set_cfeatures())
        self.CoastlinesChk.toggled.connect(lambda trash:self.set_cfeatures())
        self.BlueMarbleHD.toggled.connect(lambda trash:self.populate_cfeatures())
        self.BlueMarbleSD.toggled.connect(lambda trash:self.populate_cfeatures())
        self.CartopyFeatures.toggled.connect(lambda trash:self.populate_cfeatures())
    
    def special_options(self):
        lonval = Gui.QDoubleValidator()
        lonval.setBottom(-180)
        lonval.setTop(180)
        lonval.setNotation(0)
        self.UpperLon.setValidator(lonval)
        self.LowerLon.setValidator(lonval)
        
        if self.projection and self.projection.startswith('NorthPolarStereo'):
            self.UpperLat.setValidator(Gui.QDoubleValidator(-61.5736, 90.0,6))
            self.LowerLat.setValidator(Gui.QDoubleValidator(-61.5736, 90.0,6))
        else:
            self.UpperLat.setValidator(Gui.QDoubleValidator(-90.0, 90.0,6))
            self.LowerLat.setValidator(Gui.QDoubleValidator(-90.0, 90.0,6))
            
            
    def Signals(self,state):
        self.UpperLat.blockSignals(state)
        self.LowerLat.blockSignals(state)
        self.UpperLon.blockSignals(state)
        self.LowerLon.blockSignals(state)
        self.CoastlinesChk.blockSignals(state)
        self.RiversChk.blockSignals(state)
        self.LakesChk.blockSignals(state)
        self.LandChk.blockSignals(state)
        self.BordersChk.blockSignals(state)
        self.OceanChk.blockSignals(state)
        self.BlueMarbleHD.blockSignals(state)
        self.BlueMarbleSD.blockSignals(state)
        self.CartopyFeatures.blockSignals(state)
    
    def populate_axes_combo(self):
        self.axlist = []
        axes = self.fig.axes
        for ax in axes:
            axtype = mplu.determineAxesType(ax)
            if axtype == 'geo':
                props = ax.properties()
                if isinstance(props['children'][0],matplotlib.collections.QuadMesh):
                    continue
                else:
                    if ax.get_title():
                        self.axlookup[ax] = f'{ax.get_title()}'
                    elif ax.get_ylabel() and ax.get_xlabel():
                        self.axlookup[ax] = f'{ax.get_ylabel()} vs. {ax.get_xlabel()}'
                    else:
                        y = ax.properties()
                        self.axlookup[ax] = str(mplu.getSpan(y['subplotspec'], y['geometry']))
                    self.axlist.append(ax)
        for i,ax in enumerate(self.axlist):
            if ax.get_ylabel() and ax.get_xlabel():
                self.AxesCombo.addItem(self.axlookup[ax])
            else:
                self.AxesCombo.addItem(str(i))
        
    def populate_options(self,index):
        self.Signals(True)
        if index < len(self.axlist):
            self.ax = self.axlist[index]
            self.projection = mplu.parseAxesCartopyTransform(self.ax)
            self.special_options()
            self.populate_extents()
            self.check_feature_type()
            self.populate_cfeatures()
        self.Signals(False)
            
    def populate_extents(self):
        extents = self.ax.get_extent(ccrs.PlateCarree())
        lowerlon,upperlon,lowerlat,upperlat = extents
        self.LowerLon.setText(str(lowerlon))
        self.UpperLon.setText(str(upperlon))
        self.LowerLat.setText(str(lowerlat))
        self.UpperLat.setText(str(upperlat))
        
    def check_feature_type(self):
        self.BlueMarbleHD.setChecked(False)
        self.BlueMarbleSD.setChecked(False)
        self.CartopyFeatures.setChecked(False)
        #assuming if any image is given, it is a blue marble
        if self.ax.images:
            imgtype = 'CFeature'
            for img in self.ax.images:
                height = img._A.shape[0]
                width = img._A.shape[1]
                if width == 8192 or height == 4096:
                    imgtype = 'SD'
                    break
                elif width == 21600 or height == 10800:
                    imgtype = 'HD'
                    break
        else:
            imgtype = 'CFeature'
        
        if imgtype == 'HD':
            self.BlueMarbleHD.setChecked(True)
        elif imgtype == 'SD':
            self.BlueMarbleSD.setChecked(True)
        else:
            self.CartopyFeatures.setChecked(True)
        self.populate_cfeatures()
            
        
    def populate_cfeatures(self):
        self.LakesChk.setChecked(False)
        self.RiversChk.setChecked(False)
        self.OceanChk.setChecked(False)
        self.LandChk.setChecked(False)
        self.BordersChk.setChecked(False)
        self.CoastlinesChk.setChecked(False)
        if self.CartopyFeatures.isChecked():
            self.CFeatureWidget.setEnabled(True)
            self.images = []
            for art in self.ax.artists:
                if isinstance(art,cartopy.mpl.feature_artist.FeatureArtist):
                    name = art._feature.name
                    if name == 'coastline':
                        self.CoastlinesChk.setChecked(True)
                    elif name == 'ocean':
                        self.OceanChk.setChecked(True)
                    elif name == 'land':
                        self.LandChk.setChecked(True)
                    elif 'boundary' in name:
                        self.BordersChk.setChecked(True)
                    elif 'lakes' == name:
                        self.LakesChk.setChecked(True)
                    elif 'rivers' in name:
                        self.RiversChk.setChecked(True)
        else:
            for i in range(len(self.ax.artists)-1,-1,-1):
                art = self.ax.artists[i]
                if isinstance(art,cartopy.mpl.feature_artist.FeatureArtist):
                    self.ax.artists.pop(i)
            self.CFeatureWidget.setEnabled(False)
        self.set_cfeatures()
            
    def set_extents(self):
        lonl = self.LowerLon.text()
        lonu = self.UpperLon.text()
        latl = self.LowerLat.text()
        latu = self.UpperLat.text()
        
        if lonl and lonu and latl and latu:
            try:
                tup = (float(lonl),float(lonu),float(latl),float(latu))
                self.ax.set_extent(tup,ccrs.PlateCarree())
            except:
                pass
    
    def set_cfeatures(self):
        for i in range(len(self.ax.artists)-1,-1,-1):
            art = self.ax.artists[i]
            if isinstance(art,cartopy.mpl.feature_artist.FeatureArtist):
                self.ax.artists.pop(i)
        if self.CartopyFeatures.isChecked():
            self.ax.images = []
            if self.OceanChk.isChecked():
                self.ax.add_feature(cartopy.feature.OCEAN)
            if self.LandChk.isChecked():
                self.ax.add_feature(cartopy.feature.LAND)
            if self.RiversChk.isChecked():
                self.ax.add_feature(cartopy.feature.RIVERS)
            if self.CoastlinesChk.isChecked():
                self.ax.add_feature(cartopy.feature.COASTLINE)
            if self.LakesChk.isChecked():
                self.ax.add_feature(cartopy.feature.LAKES)
            if self.BordersChk.isChecked():
                self.ax.add_feature(cartopy.feature.BORDERS)
        else:
            if self.BlueMarbleHD.isChecked():
                EARTH_IMG = np.load(BMHD)
            else:
                EARTH_IMG = np.load(BMSD)
            self.ax.set_global()
            self.ax.imshow(EARTH_IMG,
                  origin = 'upper',
                  transform = ccrs.PlateCarree(),
                  extent=[-180,180,-90,90])
            self.set_extents()
        
def edit_map(*args,**kwargs):
    dialog = map_plot_options(*args,**kwargs)
    dialog.exec_()