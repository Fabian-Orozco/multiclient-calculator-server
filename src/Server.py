from cgi import test
from time import sleep
from Communicator import Communicator
from SimulatorTcp import SimulatorTcp
import socket
import threading
import os
from Utilities import *


class Server:
	def __init__(self, host, port):
		self.__host = host            # server port
		self.__port = port            # server ip
		self.__maxTimeOut = 300       # max timout of client inactivity in seconds
		self.__welcomingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.__welcomingSocket.bind((self.__host, self.__port))
		self.tcpCommunication = SimulatorTcp(self.__welcomingSocket, self.__host, self.__port)


	def shutDownServer(self):
		printMsgTime(f'{TXT_RED}|====Shutting down server====|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__welcomingSocket.close()

	def waitForClient(self):
		newPort = self.__port
		# waits for client connection
		try:
			while (True):
				try:
					newPort += 1
					if (self.tcpCommunication.listen(newPort)):
						# creates thread to manage the connection
						thread = threading.Thread(target = self.handle_request,
							args = (newPort, self.tcpCommunication.getSeqAck(), \
							self.tcpCommunication.getDestination()))
						thread.daemon = True
						thread.start()
				except KeyboardInterrupt or OSError or EOFError:
					break
		finally:
			self.shutDownServer()

	def handle_request(self, port, values, destination):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self.__host, port))
		communicator = SimulatorTcp(sock, destination[0], destination[1])
		# setting values to continue communication
		communicator.setSeqAck(values)
		clientMessage = communicator.receiveTcpMessage()
		clientMessage = communicator.receiveTcpMessage()



	def run(self):
		printMsgTime(f"{TXT_GREEN}|====Server started====|{TXT_RESET}")
		printMsgTime(f"{TXT_YELLOW}Binded to ip:{self.__host} | port:{self.__port}{TXT_RESET}")

		self.waitForClient()

if(__name__ == '__main__'):
	server = Server('127.0.0.2', 8080)
	server.run()
	'''
	# tecp testing
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('127.0.0.1', 8080))
	test = SimulatorTcp(sock,'127.0.0.1',8080)
	test.listen(8080)
	message = "\"type\":\"Hola como esta\""
	test.receiveTcpMessage()
	message = "\"type\":\"lohout\""
	test.sendTcpMessage(message)
'''

