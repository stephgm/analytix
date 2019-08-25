#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 15:37:53 2019

@author: hollidayhp
a function to continuously run and kill mcafee processes
"""
import os
from subprocess import Popen, PIPE
from time import sleep

while True:
    p = Popen('/bin/ps -ef | grep /opt/McAfee | grep -v grep', shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)
    for line in p.stdout:
        pid = line.rstrip().split()[1]
        #print('kill -9 '+pid.decode('utf-8'))
        os.system('kill -9 '+pid.decode('utf-8'))
        sleep(5)