# Daniel Escobar Giraldo C02748
# basado en el turotial de Shashank Singh: https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-UDP-Server-with-Multiple-Clients.php

from pydoc import cli
import socket
import threading
import os
from typing import final

class multiServer:
    def __init__(self, host, port):
        self.host = host    # Host address
        self.port = port    # Host port
        self.sock = None    # Socket
        self.socket_lock = threading.Lock() # to manage the threads

    def printmsg(self, msg):
        print(f'Server | {msg}')
        self.print_divider()

    def print_divider(self):
        term_size = os.get_terminal_size()
        print('\u2500' * term_size.columns, end='')

    def configure_server(self):
        self.print_divider()

        # create UDP socket with IPv4 addressing
        print('Server | Server started')

        # bind server to the address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.printmsg(f'Binded to {self.host}:{self.port}')

    def shutdown_server(self):
        self.printmsg('Shutting down server')
        # shutdown the server so we close the socket
        self.sock.close()

    def handle_request(self, data, client_address):
        # handle request
        # the received message is printed and we send the same message as response to client
        mesageReceived = data.decode('utf-8')

        print(f'Server | Message received from {client_address}: {mesageReceived}')

        # send response to the client
        with self.socket_lock:
            self.sock.sendto(mesageReceived.encode('utf-8'), client_address)
        self.printmsg('Received message sent to client')

    def wait_for_client(self):
        # Wait for clients and handle their requests
        try:
            while True: # keep alive

                try:
                    # receive request from client
                    data, client_address = self.sock.recvfrom(1024)
                    if(data): # if a message was received
                        #we create a thread to manage the connection
                        thread = threading.Thread(target = self.handle_request,
                            args = (data, client_address))
                        thread.daemon = True
                        thread.start()
                except OSError as err:
                    self.printmsg(err)
                except KeyboardInterrupt:
                    self.shutdown_server()
        finally:
            self.shutdown_server()

def main():
    # Create and start the UDP Server
    udp_server_multi_client = multiServer('127.0.0.1', 8080)
    udp_server_multi_client.configure_server()
    udp_server_multi_client.wait_for_client()

if __name__ == '__main__':
    main()