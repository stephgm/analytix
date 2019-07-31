# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 19:16:14 2019

@author: Jordan
"""

import os
import numpy as np
import glob
import h5py

#NEED TO ChECK IF REFERENT DIR AND DATA DIR ARE FOUND should be done in getMetrics cant find common metrics

#Get the directory from the user
directory = os.path.join(os.path.expanduser('~'),'Desktop','Data')

files = os.listdir(directory)
#This is gonna be for the metric map
MetricsMap = {}

#use this to populate a combo box for the user to select
uniqueData = np.unique(map(lambda x: x.split('run')[0],files))
#Then pop up a list box to select the runs that you want to do,
#set this to some class variable
selectedRuns = glob.glob(os.path.join(directory,uniqueData[1]+'*'))

#This function will get all the common metrics thta can be done and populate a combo box
#use the uewrlrid.h5 to do this instead of the dat files.
def getMetrics():
    folders = selectedRuns
    metrics = []
    for i,folder in enumerate(folders):
        print folder
        metrics.append([])
        if glob.glob(os.path.join(folder,'102*.txt')):
            metrics[i].append('102')
    print metrics
    setlist = map(set,metrics)
    commonmetrics = set.intersection(*setlist)
    print commonmetrics
    
    #Gotta find the metrics for the referent data
    
    return commonmetrics

selectedMetric = list(getMetrics())[0]

#def mapMetricsToFileNum():
    

def mapMetricsToFields():
    global MetricsMap
    #The key should be the actual metric name
    MetricsMap['102'] = {'102':'Time'}

mapMetricsToFields()

#This will take the common metric that was selected and gather the data associated with it
def accumulateData():
    if selectedMetric:
        files = glob.glob(os.path.join(directory,uniqueData[1]+'*','uewrlrid.h5'))
        print files
        print MetricsMap[selectedMetric].keys()
#        h5py.h5f.open()
        
accumulateData()