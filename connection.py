# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import os
import socket
from constants import *
from base64 import b64encode
import glob

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.sock = socket

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        conn = self.sock
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break 
            data = data.split("\r\n")
            data = list(map(lambda x: x.split(" "), data))[:-1]
            
            print(data)
            
            for command in data:
                if command[0] == "get_file_listing":
                    response = self.get_file_listing()
                elif command[0] == "get_metadata":
                    response = self.get_metadata(command[1])
                elif command[0] == "get_slice":
                    response = self.get_slice(command[1], int(command[2]), int(command[3]))
                elif command[0] == "quit":
                    conn.close()
                    return
                conn.send(response.encode())


            # data = self.get_metadata("lorem5.txt")
             
        conn.close()
    
    def get_file_listing(self):
    
        path = os.getcwd() + '/' + DEFAULT_DIR
        
        files = "0 OK" + EOL
        for f in glob.glob(path + "**/*.*"):
            files = files + os.path.basename(f) + EOL
        files = files + EOL
        
        return files
        
    def get_metadata(self, filename):
        path = os.getcwd() + '/' + DEFAULT_DIR + '/'

        size = str("0 OK\r\n" + str(os.path.getsize(path + filename)) + EOL)

        return size
        

    def get_slice(self, filename, offset, size):
        path = os.getcwd() + '/' + DEFAULT_DIR + '/' + filename
        file = open(path, 'r').read()[offset:offset+size]
        response = "0 OK\r\n" + (b64encode(file.encode('utf-8'))).decode('utf-8') + EOL 
        return response
