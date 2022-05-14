from email import message
from SimulatorTcp import SimulatorTcp
import socket
import threading
import os
from Utilities import *
from Authenticator import Authenticator
import json
from MessageFormatter import MessageFormatter
import queue

class Server:
	def __init__(self, host, port):
		self.__host = host            # server port
		self.__port = port            # server ip
		self.__maxTimeOut = 300       # max timout of client inactivity in seconds
		self.__welcomingSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.__welcomingSocket.bind((self.__host, self.__port))
		self.tcpCommunication = SimulatorTcp(self.__welcomingSocket, self.__host, self.__port)
		self.__authenticator = Authenticator()
		self.__formatter = MessageFormatter()
		self.__requestsQueue = queue.LifoQueue()

	def shutDownServer(self):
		printMsgTime(f'{TXT_RED}|====Shutting down server====|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__welcomingSocket.close()

	def __waitForClient(self):
		newPort = self.__port
		# waits for client connection
		try:
			while (True):
				try:
					newPort += 1
					if (self.tcpCommunication.listen(newPort)):
						# creates thread to manage the connection
						thread = threading.Thread(target = self.__handleConnection,
							args = (newPort, self.tcpCommunication.getSeqAck(), \
							self.tcpCommunication.getDestination()))
						thread.daemon = True
						thread.start()
				except KeyboardInterrupt or OSError or EOFError:
					break
		finally:
			printMsgTime(f"{TXT_RED}Testing:{TXT_RESET}{TXT_YELLOW}Server queue contains the next messages:{TXT_RESET}")
			while not self.__requestsQueue.empty():
				print(self.__requestsQueue.get())
			self.shutDownServer()

	def __handleConnection(self, port, values, destination):
		printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Handling request in thread: {threading.get_ident()}")

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self.__host, port))
		communicator = SimulatorTcp(sock, destination[0], destination[1])
		# setting values to continue communication
		communicator.setSeqAck(values)

		loginAccepted, user = self.__clientLogin(communicator)
		if(loginAccepted == False):
			communicator.close()
			return
		action = self.__handleRequest(communicator)
		if (action == "timeout"):
			printMsgTime(f"User \"{user}\" {TXT_RED}timedout thread: {threading.get_ident()}{TXT_RESET}")
		
		printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Closing thread: {threading.get_ident()}")

		printMsgTime(f"User \"{user}\" {TXT_RED}disconnected{TXT_RESET}")



	def __handleRequest(self, communicator):
		communicator.setTimeout(self.__maxTimeOut)
		messageReceived = communicator.receiveTcpMessage()
		if (messageReceived == "timeout"):
			return messageReceived
		jsonMessage = json.loads(messageReceived)


		while(jsonMessage["type"] != "disconnect"):
			self.__requestsQueue.put(messageReceived)
			communicator.setTimeout(self.__maxTimeOut)
			messageReceived = communicator.receiveTcpMessage()
			if (messageReceived == "timeout"):
				return messageReceived
			jsonMessage = json.loads(messageReceived)
		return "disconnect"


	def __clientLogin(self, communicator):
		canWrite = False
		userAccepted = False
		message = communicator.receiveTcpMessage()
		loginInfo = json.loads(message)
		userAccepted = self.__authenticator.checkLog(loginInfo['username'], loginInfo['password'])
		if (userAccepted):
			canWrite = self.__authenticator.userCanWrite()

		message = self.__formatter.formatLogin(loginInfo['username'], loginInfo['password'],  str(userAccepted).lower(), str(canWrite).lower())
		user = loginInfo['username']
		communicator.sendTcpMessage(message)
		if (userAccepted):
			printMsgTime(f"User \"{loginInfo['username']}\" {TXT_GREEN}accepted{TXT_RESET}")
			return (True, user)
		else:
			printMsgTime(f"User \"{loginInfo['username']}\" {TXT_RED}not accepted{TXT_RESET}")
			return (False, user)

	def run(self):
		printMsgTime(f"{TXT_GREEN}|====Server started====|{TXT_RESET}")
		printMsgTime(f"{TXT_YELLOW}Binded to ip:{self.__host} | port:{self.__port}{TXT_RESET}")

		self.__waitForClient()

if(__name__ == '__main__'):
	server = Server('127.0.0.2', 8080)
	server.run()