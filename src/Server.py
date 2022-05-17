from base64 import encode
from SimulatorTcp import SimulatorTcp
import socket
import threading
import os
from PipeManager import *
from Utilities import *
from Authenticator import Authenticator
import json
from MessageFormatter import MessageFormatter
import queue
import ctypes
from Dispatcher import Dispatcher
import sys

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
		self.__requestsQueue = queue.Queue()
		self.__dispatcher = Dispatcher('127.0.0.2', 7070)

	def shutDownServer(self):
		printMsgTime(f'{TXT_RED}|======: Shutting down server :======|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__welcomingSocket.close()

	def __waitForClient(self):
		# start of thread tha consumes from the requests queue
		consumerThread = threading.Thread(target = self.__consumeRequests)
		consumerThread.daemon = True
		consumerThread.start()

		newPort = self.__port
		# waits for client connection
		# creates a thread for each client
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
			# put stop condition in the queue to estop the consumer thread
			self.__requestsQueue.put("stop")
			self.shutDownServer()

	def __handleConnection(self, port, values, destination):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((self.__host, port))
		communicator = SimulatorTcp(sock, destination[0], destination[1])
		# setting values to continue communication
		communicator.setSeqAck(values)

		loginAccepted, user = self.__clientLogin(communicator)
		if(loginAccepted == False):
			if (user == "timeout"):
				printMsgTime(f"{TXT_RED}Login timedout{TXT_RESET}")
			printMsgTime(f"{TXT_RED}Connection finished{TXT_RESET}")
			communicator.close()
			return

		action = self.__handleRequest(communicator)
		if (action == "timeout"):
			printMsgTime(f"User \"{user}\" {TXT_RED} reached timeout{TXT_RESET}")

		printMsgTime(f"User \"{user}\" {TXT_RED}disconnected{TXT_RESET}")
		communicator.close()

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

	def __consumeRequests(self):
		request = ""
		while (True):
			# Get the next data to consume, or block while queue is empty
			request = self.__requestsQueue.get(block = True, timeout = None)

			# checking if the request is a stop condition
			if (request == "stop"):
				self.__sendPipe(request)
				break
			# send the message through the pipe
			self.__sendPipe(request)

	def __sendPipe(self, message):
		# Cargamos la libreria 
		sendMsg(message)
		return

	def __clientLogin(self, communicator):
		canWrite = False
		userAccepted = False
		communicator.setTimeout(20)
		message = communicator.receiveTcpMessage()
		if (message == "timeout"):
			return (False,"timeout")
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
		printMsgTime(f"{TXT_GREEN}|======: Server started :======|{TXT_RESET}")
		printMsgTime(f"{TXT_YELLOW}Binded to ip:{self.__host} | port:{self.__port}{TXT_RESET}")

		self.__waitForClient()

if(__name__ == '__main__'):
	# default
	host = '127.0.0.1'
	port = 8080

	if (len(sys.argv) == 2):  # script | host
		host = sys.argv[1]

	elif(len(sys.argv) == 3):  # script | host | port
		host = sys.argv[1]
		port = int(sys.argv[2])

	server = Server(host, port)
	dispatcher = Dispatcher('127.0.0.2', 7070)

	pid = createChild()
	if(pid ==  0):
		closeWriteEnd()
		dispatcher.dispatch()
	elif(pid == -1):
		printErrors("Fork failure")
	else:
		closeReadEnd()
		server.run()
		closeWriteEnd()
