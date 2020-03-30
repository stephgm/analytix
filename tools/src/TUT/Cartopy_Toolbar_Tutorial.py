# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 11:22:24 2020

@author: cjmar
"""


import os
import sys

if not hasattr(sys, 'frozen'):
    RELATIVE_LIB_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if __name__ == '__main__':
        sys.path.append(RELATIVE_LIB_PATH)
        sys.path.pop(0)
else:
    RELATIVE_LIB_PATH = os.path.dirname(sys.executable)
    
from PlotH5.Plotterator import Plotter
from misc_functions import InternationalDateline as ID


if __name__ == '__main__':
    
    #Lets make Circles around Huntsville and Los Angeles with a radius of 500km

    #Here we get the center of our circles (just the central lat lon points)
    HSV_Lat,HSV_Lon = (34.73,-86.58)
    LA_Lat,LA_Lon = (34.05,-118.24)
    
    #Now we make the circles using the International Dateline utils.  Returns list of lats and lons for plotting
    HSV_lats,HSV_lons = ID.circleLatLons(HSV_Lat,HSV_Lon,500)
    LA_lats,LA_lons = ID.circleLatLons(LA_Lat,LA_Lon,500)
    
    #Now we have our data, lets make a plot
    #Instantiate a Plotterator object and make a map plot
    pltr = Plotter(title='Cartopy Tutorial',classy='Unclassified',tools=['CartopyOptions'])
    pax = pltr.add_subplot(mapplot=True)
    
    #We just want to add patches, so we will do that with plotterator
    
    #Note: Matplotlib has a circle patch option, however, the transforms of Cartopy make it such that the patch that is
    # applied by matplotlib will not be transformed.  Also the 'radius' of that circle will be constant in lat lon deltas,
    # which is wrong.  Thats why we add a polygon with lat lons from the International Dateline utility
    
    #Also, Lats and lons will need to be zipped together
    pltr.add_patch(pax,'Polygon',[[list(zip(HSV_lons,HSV_lats))],dict(color='purple')])
    pltr.add_patch(pax,'Polygon',[[list(zip(LA_lons,LA_lats))],dict(color='red')])
    pltr.parseCommand(pax,'set_global',[[]])
    pltr.createPlot('',PERSIST=True)
    
    
    '''
    The rest of this is just text, because there's nothing else to show in code.
    
    You'll notice that there are indeed two circle patches on the axes of the plot,
    however, you cannot really tell where they are in a geographical sense.
    
    You should notice a 'globe-like' button in the matplotlib toolbar.  Click that,
    and look near the bottom where it says 'Cartopy Features'.  Those check boxes
    indicate certain features that can be turned on and turned off.  Just mess
    around with it.  
    
    '''
    
    
    
    
    
    
    
    
    
    
    