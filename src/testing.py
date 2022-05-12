from SimulatorTcp import SimulatorTcp
import socket
from Utilities import *


if(__name__ == '__main__'):
    #====================================== client to server testing

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.2'
    port = 8080
    addresInfo = [ip, port]
    communication = SimulatorTcp(serverSocket, ip, port)
    if (communication.connect()):
        message = "\"type\":\"login\""

        communication.sendTcpMessage(message)

        message = "\"type\":\"logout\""

        communication.sendTcpMessage(message)



    
'''
    #====================================== tctp testing
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.1'
    port = 4040
    addresInfo = [ip, port]
    communication = SimulatorTcp(serverSocket, ip, port)
    communication.connect()
    communication.receiveTcpMessage()
    message = "\"type\":\"Hola como esta\""
    communication.sendTcpMessage(message)


    # IMPORTANT register ack
    self.__ack = confirmation['seq']+1

    # IMPORTANT register seqValue
    self.__seqValue += 1
'''
