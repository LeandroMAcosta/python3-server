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
        self.s = socket            # Socket del cliente.
        self.d = './' + directory  # Directiorio actual.
        self.buffer = ''           # Cola de comandos. 
        self.active = True         # Nos dice si el cliente termino la conexión.
        self.data = ''             # Datos que se van a enviar al cliente.

    def send(self, message):
        # Envia el mensaje al cliente.
        # FALTA: Hacerlo bien.
        self.data = ''
        self.s.send(message.encode('ascii'))

    def _valid_filename(self, filename):
        return set(filename) <= VALID_CHARS and isfile(join(self.d, filename))

    def _build_message(self, status):
        """
        Estos mensajes estan construidos por el codigo de respuesta,
        seguida de un espacio, seguido de un mensaje de error y
        datos del server si es que los hay.
        """
        message = '%s %s %s' % (status, error_messages[status], EOL)
        if len(self.data) != 0:
            message += str(self.data)
            message += EOL  # Completa el mensaje con un fin de línea.
        return message

    def get_file_listing(self):
        try:
            files = [f for f in listdir(self.d) if isfile(join(self.d, f))]
            self.data = EOL.join(files) + EOL
            return CODE_OK
        except Exception:
            return FILE_NOT_FOUND

    def get_slice(self, filename, offset, size):
        try:
            offset, size = int(offset), int(size)
        except ValueError:
            '''
            Levantar esta excepcion significa que llegaron argumentos
            invalidos y parser_command tiene que manejalo.
            '''
            raise

        if not self._valid_filename(filename):
            return FILE_NOT_FOUND
        
        path = join(self.d, filename)
        file = open(path, 'rb')
        file.seek(offset)
        data = file.read(size)
        data = b64encode(data).decode('ascii')
        self.data = data
        return CODE_OK

    def get_metadata(self, filename):
        if not self._valid_filename(filename):
            return FILE_NOT_FOUND

        size = getsize(join(self.d, filename))
        self.data = str(size)
        return CODE_OK

    def quit(self):
        self.active = False
        return CODE_OK

    def _normalize_command(self, command):
        '''
        Ejemplo:
        Llamar a self._normalize_command('get_metadata home.txt') produce una
        una tupla de la forma: ('get_metadata', ['home.txt'])

        Donde el primer elemento de la lista es el comando y el resto son
        los argumentos si es que los hay.
        '''
        command = command.split(' ')
        return command[0], command[1:]

    def parser_command(self, command):
        '''
        Esta funcion llama al metodo correspondiente al comando solicitado.
        
        Ademas:
            1. Chequea que no haya un caracter \n fuera de un terminador de
               pedido.
            2. Normaliza el comando a una forma comoda para nosotros.
        '''
        if '\n' in command:
            return BAD_EOL

        # Normalizamos el comando.
        command, args = self._normalize_command(command)

        print("Request: " + command)

        try:
            if command == 'get_file_listing':
                return self.get_file_listing(*args)
            elif command == 'get_metadata':
                return self.get_metadata(*args)
            elif command == 'get_slice':
                return self.get_slice(*args)
            elif command == 'quit':
                return self.quit(*args)
            else:
                return INVALID_COMMAND
        except (TypeError, ValueError):
            return INVALID_ARGUMENTS

    def _read_buffer(self):
        while EOL not in self.buffer and self.active:
            try:
                data = self.s.recv(BUFSIZE)
            except ConnectionResetError:
                self.active = False
                break
            if len(data) == 0:
                self.active = False
            else:
                data = data.decode("ascii")
                self.buffer += data
        if EOL in self.buffer:
            response, self.buffer = self.buffer.split(EOL, 1)
            return response
        else:
            return ''
        
    def handle(self):
        # Atiende eventos de la conexión hasta que termina.
        while self.active:
            command = self._read_buffer()
            if len(command) != 0: 
                status = self.parser_command(command)
                # Desconectamos si ocurrio un error fatal.
                if fatal_status(status):
                    self.active = False
                # Construimos un mensaje.
                message = self._build_message(status)
                # Enviamos el mensaje al cliente.
                self.send(message)
