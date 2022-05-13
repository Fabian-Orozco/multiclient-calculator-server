from SimulatorTcp import SimulatorTcp
import socket
from Utilities import *
from MessageFormatter import MessageFormatter

if(__name__ == '__main__'):
    #====================================== client to server testing
    format = MessageFormatter()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.2'
    port = 8080
    addresInfo = [ip, port]
    communication = SimulatorTcp(serverSocket, ip, port)
    if (communication.connect()):
        message = format.formatLogin("xd", "passbasic")

        communication.sendTcpMessage(message)

        #message = "\"type\":\"logout\""

        message = communication.receiveTcpMessage()
        printMsgTime(f"Received the login confirmation: {message}")
