import socket
import threading
import os
from urllib import response
from Utilities import *
from Authenticator import Authenticator
import json
from MessageFormatter import MessageFormatter
import queue
import sys
from time import sleep
from Router import Router
from HttpHandler import HttpHandler


NOHTTP = "noHTTP"
POST = "POST"
GET = "GET"
BAD_REQUEST = "badRequest"
NOT_FOUND = "notFound"
OK_CODE = "ok"
LOGIN_ACTION = "login"
REQUEST = "request"
NO_WRITE_ACCESS_1 = "<input type=\"radio\" name=\"operationType\" id=\"option-1\" value=\"write\" required>"
NO_WRITE_ACCESS_2 = "<label for=\"option-1\">Escritura</label><br>"

class Server:
	def __init__(self, host, port):
		#=========================================================================================#
		# server attributes
		self.__serverHost = host                # server port
		self.__serverPort = port                # server ip
		self.__formatter = MessageFormatter()   # class to create messages with format
		self.__maxTimeOut = 300                                                              # max timeout of client inactivity in seconds
		self.__welcomingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # server welcoming socket
		self.__welcomingSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.__welcomingSocket.bind((self.__serverHost, self.__serverPort))
		self.__requestsQueue = queue.Queue()                                                 # server requests queue
		self.__authenticator = Authenticator()                                               # server creates a authenticator to checks client credentials
		self.httpHandler = HttpHandler()
		# self.__dispatcher = Dispatcher() 				# dispatcher that sends operations to routers
		#=========================================================================================#

		# threads list to be able to join them before closing
		self.__threadsArray = []

	# @brief closes server
	# @details sends stop condition to threads and joins them
	def shutDownServer(self):
		printMsgTime(f'{TXT_RED}|======: Shutting down server :======|{TXT_RESET}')
		routersCount = len(self.__threadsArray)

		# sending stop condition to each thread to the queue
		while routersCount > 0:
			self.__requestsQueue.put("stop")
			routersCount -= 1
		
		# join of each thread
		for thread in self.__threadsArray:
			thread.join()

		# shutdown the server closes the socket
		self.__welcomingSocket.close()
		exit(0)

	# @brief Server waits for any connection (router or client)
	def __waitForConnection(self):
		# waits for any connection
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
					thread = threading.Thread(target = self.__detectConnectionType, args = (newSocket, address))
					self.__threadsArray.append(thread)

					# deamon thread so it destoys itself when it has finished working
					thread.daemon = True

					# thread starts to work
					thread.start()
				except KeyboardInterrupt or OSError or EOFError:
					break
		finally:
			# put stop condition in the queue to estop the consumers threads
			self.shutDownServer()

	# @brief Detects the connection type 
	# @details method to determine if the threads has to run as a client manager or server manager
	# @param sock new socket where the connection is moved to after handshake
	# @param address ip and port form the client/router
	def __detectConnectionType(self, sock, address):
		connectionType = self.__recvMsg(sock, 20)
		if (connectionType == "timeout"):
			return

		(httpConnection, httpAction) = self.httpHandler.handleHttpRequest(connectionType)

		if (httpConnection == NOHTTP):
			# manages client connections through terminal
			jsonMessage = json.loads(connectionType)
			if (jsonMessage["type"] ==  "login"):
				# thread runs as a manager for client connections
				self.__handleClientConnection(sock, address, connectionType)
			else:
				return
		else:
			# manages client through http
			self.handleHttpConnection(httpConnection, httpAction, sock, connectionType)

		# elif (jsonMessage["type"] ==  "router"):
		# 	# thread runs as a manager for routers connections
		# 	self.handleRouterConnection(sock, address, connectionType)

	def handleHttpConnection(self, httpConnection : str, httpAction : str, client : socket.socket, httpRequest : str):
		printMsgTime(f"{TXT_YELLOW}Es HTTP la conexion{TXT_RESET}")
		response = ""
		if (httpConnection == "GET"):
			# http request method GET
			# for the request html and login html
			response = self.httpHandler.generateResponse(OK_CODE, httpAction, "")
		elif (httpConnection == "POST"):
			# http request method POST
			# to process login credentials and operations
			response = self.handleHttpPost(httpAction, httpRequest)
			# response = self.httpHandler.generateResponse(OK_CODE, BAD_REQUEST, "")
		else:
			# http request method not supported
			response = self.httpHandler.generateResponse(BAD_REQUEST, BAD_REQUEST, f"Este Servidor no soporta pedidos de tipo: {httpConnection}", "Tipo de pedido http no soportado")

		client.sendall(response.encode("UTF-8"))

	def handleHttpPost(self, httpAction : str, httpRequest : str) -> str:
		response = ""
		printMsgTime(f"{TXT_CYAN} Evaluando que post hacer {TXT_RESET}")
		if (httpAction == LOGIN_ACTION):
				response = self.httpLogin(httpRequest)
		return response

	def httpLogin(self, httpRequest : str) -> str:
		response = ""
		printMsgTime(f"{TXT_CYAN} Es login credenciales {TXT_RESET}")
		credentials = self.httpHandler.getContent(httpRequest)
		credentials = self.httpHandler.parseText(credentials)
		(user, password) = self.httpHandler.getCredentials(credentials)
		printMsgTime(f"{TXT_CYAN}credenciales: {TXT_RESET}{credentials}")
		print(user, "  ",  password)
		
		userAccepted = self.__authenticator.checkLog(user, password)
		print(userAccepted)
		
		if (userAccepted):
			response = self.httpHandler.generateResponse(OK_CODE, REQUEST, "", f"Bienvenido {user}")
			# checks if user can write
			if (self.__authenticator.userCanWrite() == False):
				response = response.replace(NO_WRITE_ACCESS_1, "")
				response = response.replace(NO_WRITE_ACCESS_2, "")
				print(response)
		else:
			response = self.httpHandler.generateResponse(OK_CODE, LOGIN_ACTION, "Usuairo o contrase&ntildea incorrecta")

		return response



	def calcularResultados(self, operacion : str) -> str:
		# call math class
		printMsgTime(f"{TXT_CYAN} Calculando {TXT_RESET}")


	# # @brief Method to handle a router connection 
	# # @details works as a consumer thread that consumes requests from the server queue and calls the dispatcher
	# # @param sock socket used to communicate with the router
	# # @param address ip and port form the client/router
	# # @param message is the first message received form the router
	# def handleRouterConnection(self, sock, address, message):
	# 	routerInfo = json.loads(message)
	# 	routerID = routerInfo["id"]
	# 	printMsgTime(f"{TXT_GREEN}Connection established.{TXT_RESET} Router {routerID} | ip:{address[0]} | port:{address[1]}")
	# 	self.__dispatcher.updateRoutersAvailables(sock, routerID)

	# @brief Method to handle a client connection 
	# @details receives operation requests form the cliente and push them into the requests queue of the server \
	#  Also it does the authentication of the client.
	# @param connection socket used to communicate with the client
	# @param address ip and port form the client/router
	# @param loginMessage is the first message received form the client with its credentials
	def __handleClientConnection(self, connection, address, loginMessage):
		# connection established with client
		printMsgTime(f"{TXT_GREEN}Connection established.{TXT_RESET} Client | ip:{address[0]} | port:{address[1]}")

		# authentication process
		loginAccepted, user = self.__clientLogin(connection, loginMessage)

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

	# @brief Waits for requests until desconnection message
	# @param communicator socket used to communicate with the client
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
			# self.__requestsQueue.put(messageReceived)

			# receives request message from client with a 5 minutes timeout
			messageReceived = self.__recvMsg(communicator, self.__maxTimeOut)

			# if timeout reached we return and close connection
			if (messageReceived == "timeout"):
				return messageReceived
			
			# loads message into json object
			jsonMessage = json.loads(messageReceived)

		# if while is finished, it means we have to clesthe connection
		return "disconnect"

	# @brief Method to check the client credentials
	# @param communicator socket used to communicate with the client
	# @param message is the first message received form the client with its credentials
	def __clientLogin(self, communicator, message):
		# control variables
		canWrite = False
		userAccepted = False

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

	# @brief Method to receive a message through tcp
	# @details checks if the timeout is reached. 
	# @param sock socket used to communicate
	# @param timeout maximum seconds that can be waiting the socket for a message
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

	# @brief Method to send a message through tcp
	# @param sock socket used to communicate
	# @param message message to be sent
	def __sendMsg(self, sock, message):
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} sent: {message}")
		sock.send(message.encode('UTF-8'))

	# # @brief Method to consume from the requests queue
	# # @param dispatcher object that divides the requests a sends them to the router network
	# def __consumeRequests(self):
	# 	request = ""
	# 	while (True):
	# 		# Get the next data to consume, or block while queue is empty
	# 		request = self.__requestsQueue.get(block = True, timeout = None)

	# 		if (request  == "stop"):
	# 			break

	# 		# carga json para ver el tipo de request
	# 		type = json.loads(request)
	# 		if type["request"] != "read":
	# 			# dispatcher will be called in this section
	# 			self.__dispatcher.dispatch(request)
	# 		else: # TODO ETAPA 4
	# 			printMsgTime(f"The {TXT_RED}read request{TXT_RESET} is not dispatched. {TXT_CYAN}Under construction.{TXT_RESET}")
			
	# 	self.__dispatcher.shutDown()

	# @brief method to run the server
	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: Server started :======|{TXT_RESET}")
		printMsgTime(f"{TXT_YELLOW}Binded to ip: {self.__serverHost} | port: {self.__serverPort}{TXT_RESET}")
		# self.__consume()
		self.__waitForConnection()

	# # @brief consumes from the request queue to dispatch to the routers
	# def __consume(self):
	# 	# creates thread to dispatch requests
	# 	thread = threading.Thread(target = self.__consumeRequests)
	# 	self.__threadsArray.append(thread)

	# 	# deamon thread so it destroys itself when it has finished working
	# 	thread.daemon = True

	# 	# thread starts to work
	# 	thread.start()


if(__name__ == '__main__'):
	# default values
	runmode = "server"
	serverHost = '127.0.0.1'
	serverPort = 8080
	routerID = "-"
	if (len(sys.argv) >= 2):  # script | mode
		runmode = sys.argv[1].lower()

	if(len(sys.argv) >= 3):  # script | mode | host
		serverHost = sys.argv[2]

	if(len(sys.argv) >= 4):  # script | mode | host | port
		try:
			serverPort = int(sys.argv[3])
		except:
			serverPort = '-'

	if(len(sys.argv) >= 5):  # script | mode | host | port | id
		routerID = sys.argv[4]

	print(f"runmode: {runmode}; serverHost: {serverHost}, serverPort: {serverPort}, routerID: {routerID}")

	# decides if it runs as a server or a router
	if (runmode == "server"):
		server = Server(serverHost, serverPort)
		server.run()
	elif (runmode == "router"):
		if (routerID == "-"): 
			printErrors("The router id was not specified")
			exit(0)
		node = Router(serverHost, serverPort, routerID)
		node.run()
