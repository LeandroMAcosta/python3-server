# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
from os import listdir
from os.path import isfile, join, getsize


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.s = socket
        self.d = './' + directory
        self.buffer = ''
        self.active = True  # Nos dice si el cliente termino la conexión.

    def _build_message(self, code, data=None):
        """
        Estos mensajes estan construidos por el codigo de respuesta,
        seguida de un espacio, seguido de un mensaje de error y
        datos del server si es que los hay.
        """

        message = str(code) + ' ' + error_messages[code] + EOL
        if data is not None:
            message += str(data)
            message += EOL  # Completa el mensaje con un fin de línea.
        return message

    def send(self, message):
        # Envia el mensaje al cliente.
        # FALTA: Hacerlo bien.
        self.s.send(message.encode('ascii'))

    def get_file_listing(self):
        files = [f for f in listdir(self.d) if isfile(join(self.d, f))]
        message = self._build_message(CODE_OK, EOL.join(files) + EOL)
        self.send(message)

    def get_slice(self, filename, offset, size):
        try:
            offset, size = int(offset), int(size)
        except ValueError:
            raise

        path = join(self.d, filename)

        data = open(path, 'r').read()[offset:offset+size]
        data = b64encode(data.encode('ascii'))

        message = self._build_message(CODE_OK, data)
        self.send(message)

    def get_metadata(self, filename):
        try:
            size = getsize(join(self.d, filename))
            message = self._build_message(CODE_OK, str(size))
        except Exception:
            message = self._build_message(FILE_NOT_FOUND)
        self.send(message)

    def quit(self):
        message = self._build_message(CODE_OK)
        self.send(message)
        self.active = False
        self.s.close()

    def parser_command(self, command, args=None):
        # Llama al metodo correspondiente al comando solicitado

        print("Request: " + command)

        try:
            if command in ['quit', 'get_file_listing'] and args:
                raise TypeError
            elif command == 'get_file_listing':
                self.get_file_listing()
            elif command == 'get_metadata':
                self.get_metadata(*args)
            elif command == 'get_slice':
                self.get_slice(*args)
            elif command == 'quit':
                self.quit()
            else:
                message = self._build_message(INVALID_COMMAND)
                self.send(message)
        except (TypeError, ValueError):
            message = self._build_message(INVALID_ARGUMENTS)
            self.send(message)

    def _normalize_command(self, command):
        '''
        Ejemplo:
        Input 'command arg arg\r\n'
        Output [command, [arg, arg]]

        Donde el primer elemento de la lista es el comando y el resto son
        los argumentos si es que los hay.

        Si no puede normalizar, devolver 100 y desconectar el cliente.
        '''
        if command == "" or '\n' in command:
            message = self._build_message(BAD_EOL)
            self.send(message)
        else:
            try:
                command, args = command.strip().split(' ', 1) 
                return [command, args.split(' ')]
            except ValueError:
                return command.strip().split()

    def _read_buffer(self):
        while EOL not in self.buffer and self.active:
            self.buffer = self.s.recv(4096).decode("ascii")
            if len(self.buffer) == 0:
                self.active = False
        if EOL in self.buffer:
            response, self.buffer = self.buffer.split(EOL, 1)
            return response
        else:
            return ""

    def handle(self):
        # Atiende eventos de la conexión hasta que termina.
        while self.active:
            # Normaliza, descodifica mensajes.
            command = self._normalize_command(self._read_buffer())
            if command is not None:
                self.parser_command(*command)
