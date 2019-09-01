#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 17:44:10 2019

@author: Jordan Marlow
"""

import os
import sys
import zmq
import pandas as pd
import cPickle as pickle
import numpy as np
import threading
import time
import copy
import h5py
import socket

class MarlownianThread(threading.Thread):
    def terminate(self):
        sys.exit()

class GenericClient(object):
    def __init__(self,parent=None,**kwargs):
        super(GenericClient,self).__init__()
        self.parent = parent
        self.ZMQBIND = kwargs.get('bind','tcp://127.0.0.1:2000')

        hostname = socket.gethostname()
        self.ip = socket.gethostbyname(hostname)
        self.username = os.path.basename(os.path.expanduser('~'))

        self.running = True
        self.runningSUB = True
        self.connected = True
        self.threads = {}
        self.sendDictTemplate = {'username':self.username,'ip':self.ip,'data':'','message':'','type':''}

        self.connect()
        print 'made it this far'

### Setup Functions
    def connect(self):
        '''
        This function connects the client to the socket, and can also be used
        to try and reconnect.
        '''
        self.setupClient()
        if self.connected:
            print 'setting up listener'
            self.setupListen()

    def setupClient(self):
        '''
        This is where all of the sockets are set up.
        self.sock is a Requesting socket that can send/receive messages to/from
            the server.  This is for 1-1 communication between the client and server
            at a time.
        self.sockSUB is a Subscribing socket that can receive messages sent to
            all the clients by the server.  Very useful for information that
            everyone needs to know such as if the server is going to shut down.
        '''
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
        self.sock.connect(self.ZMQBIND)

        ip,port = self.ZMQBIND.rsplit(':',1)
        port = str(int(port)+1)
        self.context1 = zmq.Context()
        self.sockSUB = self.context1.socket(zmq.SUB)
        self.sockSUB.setsockopt(zmq.SUBSCRIBE, "")
        self.sockSUB.connect('{}:{}'.format(ip,port))

        self.poller = zmq.Poller()
        self.poller.register(self.sock,zmq.POLLIN)
        self.pollerPUB = zmq.Poller()
        self.pollerPUB.register(self.sockSUB,zmq.POLLIN)

        if self.testConnection():
            self.parent.Alert('Connected')
        else:
            self.parent.Alert('Server timed out.')

    def testConnection(self):
        '''
        This function uses the REP/REQ socket to poll the server to see if it
        is available for messaging.  It will try and poll the server for
        0.1 seconds or 100 ms before it gives up.  If the server cannot be reached
        the function will try to close all of the threads. Then self.connected
        is set to False.
        '''
        sendDict = copy.deepcopy(self.sendDictTemplate)
        sendDict['type'] = 'status'
        try:
            self.sock.send_pyobj(sendDict)

            print 'sent the obj in test connection'
            evt = self.poller.poll(100)
            if evt:
                msg = self.sock.recv_pyobj()
                if msg:
                    self.connected = True
                    return True
            try:
                self.stopThreads()
            except:
                pass

            self.context.destroy(1)
            self.context1.destroy(1)
            self.connected = False
            return False
        except:
            return False

    def setupListen(self):
        '''
        This function starts the listening thread for the PUB/SUB socket
        '''
        self.threads['ListenerSUB'] = MarlownianThread(target=self.listenSUB)
        self.threads['ListenerSUB'].daemon = True
        self.threads['ListenerSUB'].start()

### Send Function
    def send(self,package):
        '''
        This function takes a dictionary package as an argument and will put
        it in the form that the server expects to receive.

        Input:  package - A python dictionary object that doesn't necessarily have
                          to have the correct keys, however, the keys expected
                          are the following
                          {
                          'data':'python object',
                          'message':'A meaningful message',
                          'type':'A meaningful message type'
                          }
                Currently the "data" and the "type" keys are used on the server,
                however the message key is for future use.

        '''
        if isinstance(package,dict) and self.connected:
            print 'testing connection'
            if self.testConnection():
                print 'connection is on'
                sendDict = copy.deepcopy(self.sendDictTemplate)
                if 'data' in package:
                    sendDict['data'] = package['data']
                if 'message' in package:
                    sendDict['message'] = package['message']
                if 'type' in package:
                    sendDict['type'] = package['type']
                print sendDict
                self.sock.send_pyobj(sendDict)
                self.listen()
            print 'connection not on'
        else:
            self.parent.Alert('The package in the client send function is not a dictionary')

### Listener Threads
    def listen(self):
        '''
        This function is called to listen for a message from the server directly
        after the client has sent a message to the server.  This is why the server
        is expected to send a response to every message it receives.  This function
        polls the server and expects an response within the number of milliseconds
        inside the poll call.
        '''
        package = ''
        while not package:
            print package
            env = self.poller.poll(100)
            if env:
                package = self.sock.recv_pyobj()
                print package
                if 'warning' in package['type'].lower():
                    self.parent.Alert(package['message'])
                elif 'error' in package['type'].lower():
                    self.parent.Alert(package['message'])
                elif 'data' in package['type'].lower():
                    self.parent.Alert(package['message'])
                    self.parent.addDatatoTable(package['data'])
            else:
                pass

    def listenSUB(self):
        '''
        This function is threaded to listen to the PUB/SUB socket from the server.
        This is used for messagse that the server needs to relay to all connected
        clients.  It will poll the server over and over again until it gets a message.
        '''
        while self.runningSUB:
            try:
                package = ''
                env = self.pollerPUB.poll(0)
                if env:
                    package = self.sockSUB.recv_pyobj()
                    if 'shutdown' in package['type'].lower():
                        try:
                            wait = float(package['message'])
                        except:
                            wait = 120
                        self.threads['Shutdown'] = MarlownianThread(target=self.shutdown,args=(wait,))
                        self.threads['Shutdown'].daemon = True
                        self.threads['Shutdown'].start()
                    else:
                        pass
            except:
                print 'in except'
                pass

### Commands
    def stopThreads(self):
        '''
        This function will stop the only thread that is running, which is
        the PUB socket that receives shotgun messages from the server.
        By setting runningSUB = False this should stop the inf. loop and
        cause the thread to be able to join.  This also sets the connection status
        to False for the client.
        '''
        for key in self.threads.keys():
            print key
            self.runningSUB = False
            self.threads[key].join(2)
            self.connected = False
            del self.threads[key]
        self.parent.Alert('Disconnected')
        print 'terminated threads'

    def shutdown(self,wait):
        '''
        This function takes a wait time in seconds and will display it in the
        GUIs statusbar.  This task will automatically refresh the statusbar
        every second so that the user will know exactly when the server will
        shut down.
        '''
        nextupdate = wait
        start = time.time()
        while time.time() - start < wait:
            remaining = wait - (time.time()-start)
            if remaining <= nextupdate:
                nextupdate = remaining - 1
                remainmin = int(remaining)/60
                remainsec = int(remaining)%60
                self.parent.Alert('Server will be shutting down in {} minute(s) and {} second(s)'.format(remainmin,remainsec))
