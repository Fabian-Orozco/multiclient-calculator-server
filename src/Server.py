import socket
import threading
import os
from Utilities import *
from Authenticator import Authenticator
import json
from MessageFormatter import MessageFormatter
import queue
from Dispatcher import Dispatcher
import sys
from time import sleep


class Server:
	def __init__(self, mode, host, port):
		self.__serverHost = host            # server port
		self.__serverPort = port            # server ip
		self.__maxTimeOut = 300       # max timeout of client inactivity in seconds
		self.__formatter = MessageFormatter()
		if (mode == "server"):
			self.__configServer()
		elif (mode == "router"):
			self.__configRouter(id)

	def __configRouter(self, id="-"):
		# id to identinify the router
		self.__routerId = id
		self.__routerConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# tries to connect with server
		while(True):
			try:
				self.__routerConnection.connect((self.__serverHost, self.__serverPort))
				break
			except KeyboardInterrupt:
				self.shutDownServer()
			except:
				printErrors("Server not found. Retrying connection.")
				sleep(5)
		self.__sendMsg(self.__routerConnection, "{\"type\":\"router\"}")

	def __configServer(self):
		# server creates the socket
		self.__welcomingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# server binds the socket
		self.__welcomingSocket.bind((self.__serverHost, self.__serverPort))

		self.__requestsQueue = queue.Queue()
		self.dispatcher = Dispatcher()
		self.__authenticator = Authenticator()

	def shutDownServer(self):
		printMsgTime(f'{TXT_RED}|======: Shutting down server :======|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__welcomingSocket.close()
		exit(0)

	def __waitForClient(self):
		# start of thread tha consumes from the requests queue
		consumerThread = threading.Thread(target = self.__consumeRequests)
		consumerThread.daemon = True
		consumerThread.start()

		# waits for client connection
		# creates a thread for each client
		try:
			while (True):
				try:
					# infinite timeout so it waits for clients all the time.
					self.__welcomingSocket.settimeout(None)

					# welcoming socket listening for new connections
					self.__welcomingSocket.listen()

					# server accepts the connection
					newSocket, address = self.__welcomingSocket.accept()
					printMsgTime(f"{TXT_YELLOW}Connecting to ip:{address[0]} | port:{address[1]}{TXT_RESET}")

					# creates thread to manage the connection
					# the thread receives the socket of the new connection
					thread = threading.Thread(target = self.__handleConnection, args = (newSocket, address))

					# deamon thread so it destoys itself when it has finished working
					thread.daemon = True

					# thread starts to work
					thread.start()
				except KeyboardInterrupt or OSError or EOFError:
					break
		finally:
			# put stop condition in the queue to estop the consumer thread
			self.__requestsQueue.put("stop")
			self.shutDownServer()

	def __handleConnection(self, connection, address):
		# connection established with client
		printMsgTime(f"{TXT_GREEN}Connection established{TXT_RESET} to ip:{address[0]} | port:{address[1]}")

		# authentication process
		loginAccepted, user = self.__clientLogin(connection)

		# if not accepted the user
		if(loginAccepted == False):
			# the we print error messages
			if (user == "timeout"):
				printMsgTime(f"{TXT_RED}Login timedout{TXT_RESET}")
			printMsgTime(f"{TXT_RED}Connection finished{TXT_RESET}")

			# closes connection
			connection.close()
			return

		# handle request returns a disconnect message when finished
		disconnetcMessage = self.__handleRequest(connection)

		# disconnect message can be a timeout message
		if (disconnetcMessage == "timeout"):
			printMsgTime(f"User \"{user}\" {TXT_RED} reached timeout{TXT_RESET}")

		# end of the connection
		printMsgTime(f"User \"{user}\" {TXT_RED}disconnected{TXT_RESET}")
		connection.close()

	def __handleRequest(self, communicator):
		# receives request message from client with a 5 minutes timeout
		messageReceived = self.__recvMsg(communicator, self.__maxTimeOut)
		
		# if timeout reached we return and close connection
		if (messageReceived == "timeout"):
			return "timeout"
		printMsgTime(f"{TXT_RED}Request{TXT_RESET} message received: {messageReceived}")

		# loads message into json object
		jsonMessage = json.loads(messageReceived)

		# keeps receiving if it doesn't receive en disconnection request
		while(jsonMessage["type"] != "disconnect"):
			# puts in queue the received message
			self.__requestsQueue.put(messageReceived)

			# receives request message from client with a 5 minutes timeout
			messageReceived = self.__recvMsg(communicator, self.__maxTimeOut)

			# if timeout reached we return and close connection
			if (messageReceived == "timeout"):
				return messageReceived
			
			# loads message into json object
			jsonMessage = json.loads(messageReceived)

		# if while is finished, it means we have to clesthe connection
		return "disconnect"

	def __clientLogin(self, communicator):
		# control variables
		canWrite = False
		userAccepted = False

		# receives login message from client with 20 seconds timeout
		message = self.__recvMsg(communicator, 20)

		if (message == "timeout"):
			# timeout reached, we return timeout message
			return (False,"timeout")

		# loads into json oject the message
		loginInfo = json.loads(message)

		# authenticator checks if the user and password is valid
		userAccepted = self.__authenticator.checkLog(loginInfo['username'], loginInfo['password'])
		
		# checks if user can write
		if (userAccepted):
			canWrite = self.__authenticator.userCanWrite()

		# create message of validation which will be sent to client
		message = self.__formatter.formatLogin(loginInfo['username'], loginInfo['password'],  str(userAccepted).lower(), str(canWrite).lower())

		# sends the validation message to client
		self.__sendMsg(communicator, message)

		if (userAccepted):
			printMsgTime(f"User \"{loginInfo['username']}\" {TXT_GREEN}accepted{TXT_RESET}")
			# return true because is a valid username. Also i returns the name of the user
			return (True, loginInfo['username'])
		else:
			printMsgTime(f"User \"{loginInfo['username']}\" {TXT_RED}not accepted{TXT_RESET}")
			# return false because is a valid username. Also i returns the name of the user
			return (False, loginInfo['username'])

	def __recvMsg(self, sock, timeout):
		# maximum timeout is 5 minutes
		sock.settimeout(timeout)
		message = ""
		try:
			message = sock.recv(4096)
			printMsgTime(f"{TXT_RED}Testing{TXT_RESET} received: {message}")
			return message.decode('UTF-8')
		except socket.timeout:
			# timout reached
			return "timeout"

	def __sendMsg(self, sock, message):
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} sent: {message}")
		sock.send(message.encode('UTF-8'))

	def __consumeRequests(self):
		request = ""
		while (True):
			# Get the next data to consume, or block while queue is empty
			request = self.__requestsQueue.get(block = True, timeout = None)

			# dispatcher will be called in this section
			printMsgTime("Dispatcher work zone")
			self.dispatcher.dispatch(request)

	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: Server started :======|{TXT_RESET}")
		printMsgTime(f"{TXT_YELLOW}Binded to ip: {self.__serverHost} | port: {self.__serverPort}{TXT_RESET}")

		self.__waitForClient()

if(__name__ == '__main__'):
	# default values
	runmode = "server"
	ServerHost = '127.0.0.1'
	ServerPort = 8080
	routerID = "-"
	if (len(sys.argv) >= 2):  # script | mode
		runmode = sys.argv[1].lower()

	if(len(sys.argv) >= 3):  # script | mode | host
		ServerHost = sys.argv[2]

	if(len(sys.argv) >= 4):  # script | mode | host | port
		ServerPort = int(sys.argv[3])


	server = Server(runmode, ServerHost, ServerPort)
	server.run()
