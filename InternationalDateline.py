# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:07:44 2019

@author: Jordan
"""
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import split
from matplotlib import pyplot as plt

def latlonCircleRadiusKM(lat, lon, radiusKM):
    '''
    lat, lon are the center of the circle, radiusKM is the radius in Km of the circle
    This will return a list of lat lon points that define a circle, for speed sake the number of points is 180 1 every 2 degrees
    This also takes into account projection effects with the Earth, so the closer to the north pole, the more oval
    shape the circle will become.
    '''
    #earth radius in km
    R = 6378.1
    distanceKM = radiusKM/R
    latArray = []
    lonArray = []
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)
    brng = np.linspace(0,2*np.pi,180)
    lat2 = np.arcsin(np.sin(lat) * np.cos(distanceKM) 
            + np.cos(lat) * np.sin(distanceKM) * np.cos(brng))

    lon2 = lon + np.arctan2(np.sin(brng)*np.sin(distanceKM)
            * np.cos(lat),np.cos(distanceKM)-np.sin(lat)*np.sin(lat))

    lon2 = np.rad2deg(lon2)
    lat2 = np.rad2deg(lat2)
    latArray = list(lat2)
    lonArray = list(lon2)

    return latArray,lonArray


def handle_InternationalDateline(iLat,iLon):
    '''
    iLat and iLon must be iterables
    if there are no points that lie around the ID then I'll return the originals in a list [[lats]],[[lons]] that make a closed polygon
    if there are points that lie around the ID then I'll return a list of lists of separated points with new points on the dateline
    [[lats on left][lats on right]],[[lons on left],[[lons on right]]
    This keeps the output consistent no matter what happens in the function
    '''
    #Just convert to numpy arrays off the wiffle ball bat
    nlats = np.array(list(iLat))
    nlons = np.array(list(iLon))
    
    #So, this is the parameter that may need to be changed through testing. Default is -130
    lowerparam = -130
    
    #There are two checks that need to happen, the first below is to see if
    #your points are defined in such a way that makes them greater than 180 or less than -180
    #Note: This is the most straightforward test.
    checklons = (nlons < -180)|(nlons > 180)
    
    #This test is a little finnicky, because you can also have 'correct' lons
    #That belong to the same polygon. For instance a polygon that has the points
    # (179,70) and (-179,70).  This of course should be a short line on the map,
    #however it will fail the first test and wrap around the globe.
    checklons2 = (nlons < lowerparam) & (-180 < nlons)
    
    if not checklons.any() and not checklons2.any():
        #Just polygon them to make sure it's a closed shape
        polygon = Polygon(zip(nlons,nlats)).exterior.xy
        return [list(polygon[1])],[list(polygon[0])]
    nlons = np.where(nlons >= lowerparam,nlons,nlons+360)
    polygon = Polygon(zip(nlons,nlats))
    xx,yy = polygon.exterior.xy
    plt.plot(xx,yy)
    plt.show()
    line = LineString([(180,-5000),(180,5000)])
    rlats = []
    rlons = []
    for poly in split(polygon,line):
        xx,yy = np.array(poly.exterior.xy[0]),np.array(poly.exterior.xy[1])
        idx = xx > 180
        if idx.any():
            xx -= 360
        rlats.append(list(yy))
        rlons.append(list(xx))
    return rlats,rlons
    
if __name__ == '__main__':
    #Some Crazy shape from silly numbers
#    lats = np.array([0,1,2,3,4])
#    lons = np.array([182.0,-179,160,165,180])
    #Circle that doesn't cross the ID
#    lons,lats = Point(130,0).buffer(30).exterior.xy
    #Circle that crosses the ID
#    lons,lats = Point(130,0).buffer(55).exterior.xy
    #Rectangle that spans the ID
#    lats = [-40,40,-40,40]
#    lons = [160,-150,-160,150]
    #Circle made with stuff
    lats,lons = createCircleAroundWithRadius(80,-180,200)
    plt.scatter(lons,lats)
    plt.show()
    y,x = handle_InternationalDateline(lats,lons)
    for x,y in zip(x,y):
        plt.plot(x,y)
    plt.gca().set_aspect('equal')
    plt.show()