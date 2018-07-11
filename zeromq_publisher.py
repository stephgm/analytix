#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 15:59:39 2018

@author: hollidayh
"""

import sys
import time
import zmq
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://127.0.0.1:2000')

# Allow clients to connect before sending data
time.sleep(1)
while True:
    if sys.version_info.major == 2:
        iString = raw_input('Enter Data: ')
    else:
        iString = input('Enter Data :')
    if iString == 'quit':
        socket.send_pyobj('quit')        
        sys.exit(0)
    socket.send_pyobj(iString)
    if iString == 'stop':
        break
socket.send_pyobj({1:[1,2,3]})
time.sleep(4)
socket.send_pyobj({})
socket.send_pyobj({'this':['that',1,5.1,'four'],'that':'/path/to/stuff'})
socket.send_pyobj('stop')
