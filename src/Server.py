from SimulatorTcp import SimulatorTcp
import socket
import threading
import os

class Server:
	def __init__(self, host, port):
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.__host = host            # server port
		self.__port = port            # server ip
		self.__maxTimeOut = 300       # max timout of client inactivity in seconds



	def shutDownServer():
		self.printmsg('Shutting down server')
		# shutdown the server so we close the socket
		self.sock.close()

	def waitrForClient(self):
	# waits for client connection
	try:



	finally:



if(__name__ == '__main__'):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.1'
    port = 8080
    addresInfo = [ip, port]
    serverSocket.bind((ip, port))
    communication = SimulatorTcp(serverSocket, ip, port)
    communication.printmsg(f"Binded socket to {addresInfo}")

    if (communication.listen(8081)):
        newSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        newIp = '127.0.0.1'
        newport = 8081
        newAddresInfo = (newIp, newport)
        newSocket.bind((newIp, newport))
        communication.setSocket(newSocket)
        message = communication.receiveTcpMessage()
        communication.sendTcpMessage("\"type\":\"Hola como esta\"")

