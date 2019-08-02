# -*- coding: utf-8 -*-
"""
Created on Wed Aug 1 17:54:43 2019

@author: Jordan
"""

# Python program to implement client side of chat room. 
import socket 
import errno
import sys
import os
import threading
import multiprocessing
import time
import numpy as np

import PyQt5.QtWidgets as Widgets
import PyQt5.QtGui as Gui
import PyQt5.uic as Qt5

import Server

LOGO_FILE = 'ChatIcon.png'

#HEADER_LENGTH = 10
#IP = '127.0.0.1'
#PORT = 1234

            
class ChatClient(object):
    def __init__(self,username,server,parent=None):
        super(ChatClient,self).__init__()
        self.parent = parent
        self.username = username
        self.server = server
        self.running = True
        self.setupSocket()
        
    def setupSocket(self):
        #Okay, so if the server is running already, then this will go off without a hitch
        try:
            self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.client_socket.connect(Server.SERVER_DICT[self.server])
            self.client_socket.setblocking(False)
            
            self.username_header = "{:10}".format(len(self.username)).encode('utf-8')
            
            self.client_socket.send(self.username_header+self.username)
        #If the server is not running, then we will just run the file in a new process
        #Or this was the idea, but I can't figure it out atm... just gonna print an alert.
        except:
#            x = multiprocessing.Process(target=Server.main,args=(self.server,))
#            x.start()
#            x.join()
#            time.sleep(5)
#            self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#            self.client_socket.connect(Server.SERVER_DICT[self.server])
#            self.client_socket.setblocking(False)
#            
#            self.username_header = "{:10}".format(len(self.username)).encode('utf-8')
#            
#            self.client_socket.send(self.username_header+self.username)
            self.parent.Alert('The Server for {} seems to be down'.format(self.server))
            self.parent.ServerCombo.setCurrentIndex(-1)
        
    def Send(self,message):
        if message:
            message = str(message)
            message = message.encode('utf-8')
            message_header = "{:<10}".format(len(message)).encode('utf-8')
            self.client_socket.send(message_header + message)
                
    def getMessage(self,TextWidget,run,ClientTreeWidget):
        while self.running:
            try:
                rusername_header = self.client_socket.recv(Server.HEADER_LENGTH)
                if not len(rusername_header):
                    print('connection closed by the server')
                    sys.exit(0)
                rusername_length = int(rusername_header.decode('utf_8').strip())
                rusername = self.client_socket.recv(rusername_length).decode('utf-8')
                message_header = self.client_socket.recv(Server.HEADER_LENGTH)
                message_length = int(message_header.decode('utf_8').strip())
                message = self.client_socket.recv(message_length)
                if not message.startswith('CLIENTLIST'):
                    TextWidget.insertPlainText('{:<10}:{}\n'.format(rusername,message))
                else:
                    ClientTreeWidget.clear()
                    print message.split('--')[-1]
                    clientdict = eval(message.split('--')[-1])
                    for client in clientdict:
                        item = Widgets.QTreeWidgetItem()
                        item.setText(0,str(client))
                        ClientTreeWidget.addTopLevelItem(item)
        
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error',str(e))
                    sys.exit(1)
                continue
            
            except Exception as e:
                print('General error',str(e))
                sys.exit(1)

class ChatGUI(Widgets.QMainWindow):
    def __init__(self,parent=None):
        super(ChatGUI,self).__init__(parent)
        Widgets.QMainWindow.__init__(self, parent)
        Qt5.loadUi('CombatChat.ui', self)
        
        self.threads = []
        self.Client = None
        self.run = True
        
        self.ServerCombo.addItems(Server.SERVER_DICT.keys())
        self.ServerCombo.setCurrentIndex(-1)
        self.UsernameLineEdit.setText(os.path.basename(os.path.expanduser('~')))
### Username set Here.  Remove Numpy random.. Its there for unique purposes
        self.username = self.UsernameLineEdit.text()+str(np.random.rand())
        
        self.setWindowTitle('Combat Chat')
        self.setWindowIcon(Gui.QIcon(LOGO_FILE))
        
        self.makeConnections()
        
    def makeConnections(self):
        self.ServerCombo.activated.connect(self.setupSocket)
        self.MessageLine.editingFinished.connect(self.sendMessage)
        self.SendButton.clicked.connect(self.sendMessage)
        self.actionTo_txt.triggered.connect(self.exportChat)
    
    def setupSocket(self):
        self.Alert('Connecting to {} as {}.'.format(self.ServerCombo.currentText(),self.username))
        self.Client = ChatClient(self.username,self.ServerCombo.currentText(),self)
        if self.ServerCombo.currentText():
            self.startThreads()
            self.Alert('Connected to {} as {}.'.format(self.ServerCombo.currentText(),self.username))
        else:
            self.Client = None
    
    def sendMessage(self):
        if self.Client:
            message = self.MessageLine.text()
            if message.strip():
                self.MessageLine.setText('')
                self.Client.Send(message)
                self.ChatText.moveCursor(Gui.QTextCursor.End)
                self.ChatText.insertPlainText('{:<10}:{}\n'.format(self.username,message))
                self.ChatText.moveCursor(Gui.QTextCursor.End)
    
    def startThreads(self):
        self.threads.append(threading.Thread(target=self.Client.getMessage,args=(self.ChatText,self.run,self.UserTree,)))
        self.threads[-1].start()
        
    def stopThreads(self):
        for thread in self.threads:
            self.Client.running = False
            thread.join()
        
    def closeEvent(self,event):
        self.stopThreads()
        
    def exportChat(self):
        if not os.path.isdir(os.path.join(os.path.expanduser('~'),'CombatChat_Logs')):
            os.mkdir(os.path.join(os.path.expanduser('~'),'CombatChat_Logs'))
        name = Widgets.QFileDialog.getSaveFileName(self, 'Save File',os.path.join(os.path.expanduser('~'),'CombatChat_Logs'),'Text File (*.txt)')[0]
        if name:
            f = open(name,'w')
            text = self.ChatText.toPlainText()
            f.write(text)
            f.close()
            self.Alert('Chat text successfully exported to {}.'.format(name))
    def Alert(self,msg):
        self.statusbar.showMessage(msg)
        
def main():
    app = Widgets.QApplication(sys.argv)
    frame = ChatGUI()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)
    
if __name__ == '__main__':
    main()