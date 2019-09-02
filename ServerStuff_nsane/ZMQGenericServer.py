#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:54:39 2019

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

class GenericServer(object):
    def __init__(self,**kwargs):
        super(GenericServer,self).__init__()

        self.ZMQBIND = kwargs.get('bind','tcp://127.0.0.1:2000')

        self.running = True
        self.clients = {}
        self.Checkout = {}
        self.threads = []
        self.readPollyPocketXML()
        self.sendDictTemplate = {'data':'','message':'','type':''}
        self.socketSetup()
        self.run()

    def socketSetup(self):
        '''
        This is where all of the sockets are set up.
        self.sock is a Reporting socket that can send/receive messages to/from
            the clients.  This is for 1-1 communication between each client at a
            time.
        self.sockPUB is a Publishing socket that can send/receive messages to/from
            the clients.  This communicates to all of the clients at once.
            Very useful for information that everyone needs to know such as
            if the server is going to shut down.
        '''
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REP)
        self.sock.bind(self.ZMQBIND)

        #Add 1 to the port for shotgun messages
        ip,port = self.ZMQBIND.rsplit(':',1)
        port = str(int(port)+1)
        self.context1 = zmq.Context()
        self.sockPUB = self.context1.socket(zmq.PUB)
        self.sockPUB.bind('{}:{}'.format(ip,port))

        self.pollerrcv = zmq.Poller()
        self.pollerrcv.register(self.sock,zmq.POLLIN)

        self.startUp()

    def startUp(self):
        '''
        This functions sole purpose is to broadcast out to all of the clients
        that may have been listening while the server was shut down so that
        an inventory of all the files that are still open by clients can be
        catalogued.
        '''
        sendDict = copy.deepcopy(self.sendDictTemplate)
        sendDict['type'] = 'inventory'
        print sendDict
        self.sockPUB.send_pyobj(sendDict)
        print 'message sent'

    def shutDown(self,wait):
        '''
        This function will shut down the server.  Since all the spawned threads
        are set to Daemon = True, a simple sys.exit will kill multiple birds with
        one call.

        The function takes a wait time as an argument and then relays the message
        to the clients via a PUB/SUB connection, which is like a shotgun message.
        The clients will then notify their respective GUIs of the shutdown with
        a countdown timer.  The wait argument passed to the client is purposefully
        offset by 10 seconds to allow for any last minute processes to finish
        for the server before it is officially shutdown.  (Might add in
        auto pushing or something, and this allows time for that to happen.)

        Input:  wait - A string that is a number which represents how many
                       seconds to wait before shutting down the server.

        '''
        try:
            wait = int(wait)
        except:
            wait = 120
        print('The server will shut down in {} seconds').format(wait)
        sendDict = copy.deepcopy(self.sendDictTemplate)
        sendDict['type'] = 'shutdown'
        sendDict['message'] = '{}'.format(wait-10)
        self.sockPUB.send_pyobj(sendDict)
        start = time.time()
        time.sleep(wait)
        #TODO might need to do something else because I'm thinking of running this in thread
        self.running = False
        sys.exit()
        return

    def readPollyPocketXML(self):
        '''
        This will read Polly Pockets xml file so that we know where to grab files
        from our data on the server.  This dissociates the clients path to the
        data from how the server will retrieve it.
        '''
        #TODO take out the return for work
        self.dictionary = {'test':os.getcwd()}
        return

        import xml.etree.ElementTree as et
        xmlfile = os.path.join(RELATIVE_LIB_PATH,'gobat','database','dbMissions.xml')
        xtree = et.parse(xmlfile)
        xroot = xtree.getroot()
        self.dictionary = {}
        for event in xroot.iter('event'):
            for child in event:
                if child.tag == 'name':
                    self.dictionary[child.text()] = []
                    currevent = child.text()
                if child.tag == 'ExecutionPath':
                    if os.path.isdir(child.text):
                        self.dictionary[currevent]=child.text
        return

    def checkCheckout(self,event,run,filename,group,dset):
        '''
        This is a convenience function used to see if the file is already checked out
        '''
        checkkey = '{}:::{}:::{}'.format(event,run,filename,group,dset)
        isCheckedOut = False
        openby = ''
        for key in self.Checkout.keys():
            if checkkey in self.Checkout[key]:
                isCheckedOut = True
                openby = self.clients[key]
                break
        return openby

    def run(self):
        '''
        The big enchalada.  This is the main loop of the class.  This while loop
        listens for messages from the clients and responds in ANY situation.

        The python object that is received MUST be a dictionary and MUST have the
        follwing keys and values

        {
        'username':'your username',
        'ip':'your ip address',
        'message':'A useful message',
        'type':'The type of message',
        'data':'Python object you want to send'
        }

        The type is the main thing here, and it is checked in order to perform
        a specific action by the server.

        Message is hardly used, however, it is there for future use.

        NOTE:
            Every time a message is received from the client, a message MUST
            be sent back or the client will wait for a new message indefinitely.
            All of these messages are sent on the self.sock socket.


        '''
        self.startUp()
        while self.running:
            env = self.pollerrcv.poll(0)
            if env:
                sendDict = copy.deepcopy(self.sendDictTemplate)
                package = ''
                package = self.sock.recv_pyobj()
                if isinstance(package,dict):
                    #Get the contents of the message in the format that I'm expecting
                    if set(['username','ip','message','type','data']).issubset(set(package.keys())):
                        uname = package['username']
                        ip = package['ip']
                        mtype = package['type']
                        message = package['message']
                        data = package['data']
                        print mtype,message
                        if ip not in self.clients:
                            self.clients[ip] = uname
                        if ip not in self.Checkout:
                            self.Checkout[ip] = []
### reconnection
                        if 'reconnecting' in mtype.lower():
                            sendDict['type'] = 'inventory'
                            self.sock.send_pyobj(sendDict)
### inventory
                        elif 'inventory' in mtype.lower():
                            print 'taking inv?'
                            if message:
                                event,run,filename,group,dset = message.split(':')
                                print 'made it here'
                                if event and run and filename:
                                    openby = self.checkCheckout(event,run,filename,group,dset)
                                    print openby
                                    if not openby:
                                        self.Checkout[ip] = ['{}:::{}:::{}:::{}:::{}'.format(event,run,filename,group,dset)]
                                        sendDict['type'] = 'warning'
                                        sendDict['message'] = 'Inventory was taken'
                                        self.sock.send_pyobj(sendDict)
                                    else:
                                        sendDict['type'] = 'warning'
                                        sendDict['message'] = 'The file is already open by {}'.format(openby)
                                        self.sock.send_pyobj(sendDict)
                                else:
                                    sendDict['type'] = 'Error'
                                    sendDict['message'] = 'You apparently have a file open but the data sent to server is wrong'
                                    self.sock.send_pyobj(sendDict)
                            else:
                                sendDict['type'] = 'Warning'
                                sendDict['message'] = 'You do not have a file open'
                                self.sock.send_pyobj(sendDict)
                            print 'send the inventory msg'
### requestfilefromrun
                        elif 'requestfilefromrun' in mtype.lower():
                            '''
                            This will open a file from the run directory and return a df to client

                            input pyobj:
                                {
                                'username': '*Client Username',
                                'ip': '*Client IP Address',
                                'type': 'requestfilefromrun',
                                'message': '*Event_Name:*Run_Number:*File_Name:*Group_Name:*Dset_Name',
                                'data':None
                                }
                            Note:
                                If you want to open a non-h5py file you dont have to give a group or dset
                                but these are handy placeholders for extra values if something else needs
                                to be opened that requires more than just a filename.  All these
                                things in the message must be separated by a ":" character so that they
                                can easily be split on.
                            '''
                            #init the parts that I need
                            event,run,filename,group,dset = '','','','',''
                            for i,part in enumerate(message.split(':')):
                                if i == 0:
                                    event = part
                                elif i == 1:
                                    run = part
                                elif i == 2:
                                    filename = part
                                elif i == 3:
                                    group = part
                                elif i == 4:
                                    dset = part
                            #TODO in python 3 basestring needs to be changed to str
                            if event and isinstance(event,basestring):
                                try:
                                    executionDir = self.dictionary[event]
                                    if os.path.isdir(executionDir):
                                        if run and isinstance(run,basestring):
                                            rundir = os.path.join(executionDir,run)
                                            if os.path.isdir(rundir):
                                                if filename and isinstance(filename,basestring):
                                                    #TODO add checkout here because at this point assuming you know what data to send to open a file
                                                    checkkey = '{}:::{}:::{}:::{}:::{}'.format(event,run,filename,group,dset)
                                                    isCheckedOut = False
                                                    for key in self.Checkout.keys():
                                                        if checkkey in self.Checkout[key]:
                                                            isCheckedOut = True
                                                            openby = self.clients[key]
                                                            break
                                                    if not isCheckedOut:
                                                        self.Checkout[ip] = [checkkey]
                                                        data = {}
                                                        if filename.lower().endswith('.h5') or filename.lower().endswith('.hdf5'):
                                                            pathtofile = os.path.join(rundir,filename)
                                                            with h5py.File(pathtofile,'r') as hf:
                                                                pathinh5 = '{}/{}'.format(group,dset)
                                                                if pathinh5 in hf:
                                                                    for key in hf[pathinh5].dtype.names:
                                                                        data[key] = hf[pathinh5][key][:]
                                                                    sendDict['data'] = pd.DataFrame(data)
                                                                    sendDict['type'] = 'Data'
                                                                    self.sock.send_pyobj(sendDict)
                                                        else:
                                                            print('{} format is not supported yet. but you can add it'.format(os.path.splitext(filename)[-1]))
                                                    else:
                                                        sendDict['type'] = 'Error'
                                                        sendDict['message'] = 'File is being viewed by {}'.format(openby)
                                                        self.sock.send_pyobj(sendDict)
                                                else:
                                                    sendDict['type'] = 'Error'
                                                    sendDict['message'] = 'No Filename sent to the server'
                                                    self.sock.send_pyobj(sendDict)
                                            else:
                                                sendDict['type'] = 'Error'
                                                sendDict['message'] = '{} is not run a directory in {}'.format(run,event)
                                                self.sock.send_pyobj(sendDict)
                                        else:
                                            sendDict['type'] = 'Error'
                                            sendDict['message'] = 'No run was sent to the server'
                                            self.sock.send_pyobj(sendDict)
                                    else:
                                        sendDict['type'] = 'Error'
                                        sendDict['message'] = '{} is not a directory'.format(executionDir)
                                        self.sock.send_pyobj(sendDict)
                                except:
                                    sendDict['type'] = 'Error'
                                    sendDict['message'] = '{} is not a valid event recorded in the xml'.format(event)
                                    self.sock.send_pyobj(sendDict)
                            else:
                                sendDict['type'] = 'Error'
                                sendDict['message'] = 'There was no event sent to the server'
                                self.sock.send_pyobj(sendDict)
### testing function
                        elif 'test' in mtype.lower():
                            data = pd.DataFrame(dict(this=['is','a','dataframe'],
                                                     that=['is','a','wonderful'],
                                                     thing=[1,2,3]))
                            sendDict['type'] = 'data'
                            sendDict['data'] = data
                            sendDict['message'] = 'The data was successfully retrieved'
                            self.sock.send_pyobj(sendDict)
### push
                        elif 'push' in mtype.lower():
                            sendDict['type'] = 'Warning'
                            sendDict['message'] = 'Push was successful!'
                            self.sock.send_pyobj(sendDict)
### disconnect client
                        elif 'disconnect' in mtype.lower():
                            sendDict['type'] = 'Disconnect'
                            self.sock.send_pyobj(sendDict)
                            del self.clients[ip]
                            del self.Checkout[ip]
### shutdown
                        elif 'shutdown' in mtype.lower():
                            self.threads.append(threading.Thread(target=self.shutDown,args=(message,)))
                            self.threads[-1].daemon = True
                            self.threads[-1].start()
                            sendDict['type'] = 'Shutdown'
                            self.sock.send_pyobj(sendDict)
### send status
                        elif 'status' in mtype.lower():
                            sendDict['type'] = 'Status'
                            sendDict['message'] = 'Ok'
                            self.sock.send_pyobj(sendDict)
### else idk
                        else:
                            sendDict['type'] = 'Warning'
                            sendDict['message'] = 'The server does not know what to do with the message sent'
                            self.sock.send_pyobj(sendDict)
                    else:
                        sendDict['type'] = 'Error'
                        sendDict['message'] = 'The Server has received an incorrect structure.'
                        self.sock.send_pyobj(sendDict)
                else:
                    sendDict['type'] = 'Error'
                    sendDict['message'] = 'The Server has received an incorrect structure.'
                    self.sock.send_pyobj(sendDict)
#            except:
#                pass


if __name__ == '__main__':
    #local testing
    GenericServer()
    #Carls Home Network Testing
#    GenericServer(bind='tcp://192.168.0.13:6000')









