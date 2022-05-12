# Daniel Escobar Giraldo C02748
# basado en el turotial de Shashank Singh: https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-UDP-Server-with-Multiple-Clients.php

import socket
import os

class UDPClient:

    def __init__(self, host, port):
        self.host = host    # Host address
        self.port = port    # Host port
        self.sock = None    # Socket

    def printmsg(self, owner, msg):
        print(f'{owner} | {msg}')
        self.print_divider()

    def print_divider(self):
        term_size = os.get_terminal_size()
        print('\u2500' * term_size.columns, end='')

    def configure_client(self):
        self.print_divider()
        # create UDP socket with IPv4 addressing
        print('Client | Creating UDP/IPv4 socket ...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.printmsg('Client', f'Socket created and binded to {self.host}:{self.port}')

    def interact_with_server(self):
        # Send request to a UDP Server and receive reply from it.
        try:
            name = "not empty"
            while(name):
                # send data to server
                print("Input message to send (send empty message to close client): ")
                name = str(input())

                if (name):
                    # we proceed only if there is a message to send
                    self.sock.sendto(name.encode('utf-8'), (self.host, self.port))
                    print('\nClient | message sent')

                    # receive data from server

                    # the reply is simply a message form ther server indicating the messaged he received
                    resp, server_address = self.sock.recvfrom(1024)
                    resp = resp.decode('utf-8')
                    self.printmsg('Server', f'The server received message \"{resp}\" from {server_address}')
        except:
            self.print_divider()

    def close_client(self):
        self.close_client()
        self.printmsg('Client' ,'Socket closed')
        # we close the socket before closing client
        self.sock.close()

def main():
    # Create a UDP Client, send message to a UDP Server and receive reply.

    udp_client = UDPClient('127.0.0.1', 8080)
    udp_client.configure_client()
    udp_client.interact_with_server()

if __name__ == '__main__':
    main()