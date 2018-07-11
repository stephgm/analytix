#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 16:02:53 2018

@author: hollidayh
"""

import sys
import zmq
#import socket
context = zmq.Context()
socket = context.socket(zmq.SUB)
# We can connect to several endpoints if we desire, and receive from all.
socket.connect('tcp://127.0.0.1:2000')

# We must declare the socket as of type SUBSCRIBER, and pass a prefix filter.
# Here, the filter is the empty string, wich means we receive all messages.
# We may subscribe to several filters, thus receiving from all.
if sys.version_info.major == 2:
    socket.setsockopt(zmq.SUBSCRIBE,'')
else:
    socket.setsockopt_unicode(zmq.SUBSCRIBE,'')

while True:
    try:
        message = socket.recv_pyobj()
    except KeyboardInterrupt:
        print('KeyboardInterrupt said done')
        break
    print(message)
    if isinstance(message,str) and message == 'quit':
        print('Shutting down ...')
        break
