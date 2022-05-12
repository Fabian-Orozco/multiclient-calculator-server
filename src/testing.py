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
