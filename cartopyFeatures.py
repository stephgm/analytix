#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 21:36:06 2019

@author: hollidayh
"""
import os
import sys
import cartopy
#print(cartopy.config['data_dir'])
#sys.exit(0)
if os.name == 'posix':
    cartopy.config['data_dir'] = '/storage/data/local/lib/python'+str(sys.version_info.major)+'.7/site-packages/cartopy'
else:
    cartopy.config['data_dir'] = os.path.join(os.path.dirname(sys.executable),'Lib','site-packages','cartopy')
print(cartopy.config['data_dir'])
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt


def main():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    # focused
    #ax.set_extent([-20, 60, -40, 45], crs=ccrs.PlateCarree())
    ax.set_global()
    ax.set_aspect('equal')
    ax.set_adjustable('datalim')
    # this adds nice rendering of the water
    #ax.stock_img()
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    plt.show()


if __name__ == '__main__':
    main()
