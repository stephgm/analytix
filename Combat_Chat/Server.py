# -*- coding: utf-8 -*-
"""
Created on Wed Aug 1 17:54:42 2019

@author: Jordan
"""

# Python program to implement server side of chat room. 
import socket 
import select 
import threading
from collections import OrderedDict
  
SERVER_DICT = OrderedDict(Local=('127.0.0.1',1234),OtherLocal=('127.0.0.1',1222))
HEADER_LENGTH = 10

#List for the threads
threads = []

class ChatServer(object):
    def __init__(self,server,parent=None):
        super(ChatServer,self).__init__()
        self.parent = parent
        self.server = server
        
        self.thread = []
        self.running = True
        
        self.startServer()
        self.run()
    def startServer(self):
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        #This allows you to reconnect even if address was in use.  very useful
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        
        self.server_socket.bind(SERVER_DICT[self.server])
        
        self.server_socket.listen(100)
        
        self.sockets_list = [self.server_socket]
        
        self.clients = {}
    
    
    def receive_message(self,client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return {}
            message_length = int(message_header.decode("utf-8").strip())
            return {'header':message_header,'data':str(client_socket.recv(message_length))}
        
        except:
            print 'in the except'
            return {}
        
    def run(self):
        while self.running:
            #sockets to read, write, or error on
            read_sockets,_,exception_sockets = select.select(self.sockets_list,[],self.sockets_list)
            
            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    #someone just connected
                    client_socket,client_address = self.server_socket.accept()
                    
                    user = self.receive_message(client_socket)
                    
                    if user:
                        self.sockets_list.append(client_socket)
                        
                        self.clients[client_socket] = user
                        
                        print('Accepted new connection from {}:{} username:{}'.format(client_address[0],client_address[1],user['data'].decode('utf-8')))
                        userlist = []
                        for cs in self.clients:
                            userlist.append(self.clients[cs]['data'])
                        for client in self.clients:
                            nmessage = 'CLIENTLIST--{}'.format(userlist).encode('utf-8')
                            nmessageheader = '{:<10}'.format(len(nmessage))
                            client.send(user['header'] + user['data'] + nmessageheader + nmessage)
                    
                else:
                    user = self.clients[notified_socket]
                    message = self.receive_message(notified_socket)
                    if not message and message != 'GetUserList':
                        print('Closed connection from {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        userlist = []
                        for cs in self.clients:
                            userlist.append(self.clients[cs]['data'])
                        for client_socket in self.clients:
                            nmessage = 'CLIENTLIST--{}'.format(userlist).encode('utf-8')
                            nmessageheader = '{:<10}'.format(len(nmessage))
                            client_socket.send(user['header'] + user['data'] + nmessageheader + nmessage)
                        continue
                    elif message and message != 'GetUserList':
                        print('Received message from {}:{}'.format(user['data'].decode('utf-8'),message['data'].decode('utf-8')))
                        
                        for client_socket in self.clients:
                            if client_socket != notified_socket:
                                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    elif message and message == 'GetUserList':
                        userlist = []
                        for cs in self.clients:
                            userlist.append(self.clients[cs]['data'])
                        nmessage = 'CLIENTLIST--{}'.format(userlist).encode('utf-8')
                        nmessageheader = '{:<10}'.format(len(nmessage))
                        notified_socket.send(user['header'] + user['data'] + nmessageheader + nmessage)
            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]
                userlist = []
                for cs in self.clients:
                    userlist.append(self.clients[cs]['data'])
                for client_socket in self.clients:
                    nmessage = 'CLIENTLIST--{}'.format(userlist).encode('utf-8')
                    nmessageheader = '{:<10}'.format(len(nmessage))
                    client_socket.send(user['header'] + user['data'] + nmessageheader + nmessage)
                    

def main(server):
    #This function exists so that the client can spawn a server if for some reason it is down.
    threads.append(threading.Thread(target=ChatServer,args=(server,)))
    threads[-1].start()

if __name__ == '__main__':
    for key in SERVER_DICT:
        main(key)
        
       
    