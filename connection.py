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
        self.get_file_listing()
        conn = self.sock
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break 
            # data = str(data).upper()
            data = self.get_file_listing()
            conn.send(data.encode())
             
        conn.close()
    
    def get_file_listing(self):
    
        path = os.getcwd() + '/' + DEFAULT_DIR
        
        files = "0 OK\r\n"
        for f in glob.glob(path + "**/*.*", recursive=False):
            files = files + (os.path.basename(f) + '\r\n')
        files = files + "\r\n"
        
        return files
        
    def get_metadata(self, filename):
        path = os.getcwd() + '/' + DEFAULT_DIR + '/'
        size = os.path.getsize(path + filename)
        return size
        

    def get_slice(self, filename, offset_size):
        pass