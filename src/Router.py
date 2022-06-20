import random
import socket
import threading
import os
from Utilities import *
import json
from MessageFormatter import MessageFormatter
import queue
import sys
from time import sleep
import csv



class Router:
	def __init__(self, serverIp, serverPort, id):
		# this router info
		self.__routerID = id # id that identifies the router

		# connection to server info
		self.__serverIP = serverIp # the server ip
		try:
			# converto to int the port value
			self.__serverPort = int(serverPort)
		except:
			self.__serverPort = serverPort

		self.__socketServer = self.SocketStruct(serverIp, None, serverIp, serverPort, "server") # the server and our router shares the same ip
		# Info to connect to other routers
		self.__connections = dict({"server":self.__socketServer})
		self.__connectionsFile = "neighbors.csv"
		self.__availableNodes = []
		self.__topologyFile = "topologia.csv"

		# routing table info
		self.__routingTable = {"neighbord":[], "destiny":self.__availableNodes, "weights":[]}

		# thread management
		self.threadsArray = []

		# message format
		self.__formatter = MessageFormatter()

	# @brief Loads the name of the availables nodes of the network
	# @details reads the topology file to load only the name of all the nodes
	def __loadAvailableNode(self):
		with open(self.__topologyFile) as topology:
			file = csv.reader(topology)
			for row in file:  # each row of the file
				if (row[0] != self.__routerID and row[0] not in self.__availableNodes):
					self.__availableNodes.append(row[0])
				if (row[3] != self.__routerID and row[3] not in self.__availableNodes):
					self.__availableNodes.append(row[3])


	# @brief Method to connect this router to our server.
	# @details after establishing the connection the router sends the name of the router
	def __connectToServer(self):
		# router connects to server only if it received the ip and port from the console arguments
		self.__socketServer.connect()
		if (self.__serverIP != '-' or self.__serverPort != '-'):
			self.__socketServer.sendMsg("{\"type\":\"router\",\"id\":\""+ self.__routerID + "\"}")

	# @brief Receives parts of operations from the server
	# @details the main thread uses this method to
	# @param sockStruct is an class that can send, receive from/to a router
	def __runConnectionToServer(self, sockStruct):
		printMsgTime(f"Conection with {sockStruct.neighbordId} {TXT_GREEN}established{TXT_RESET}")
		while(True):
			try:
				# receiving operations (parts)
				self.__receiveOperations(sockStruct, sockStruct)

				# porcessing operations includes resending or calculating
				stopCondition = self.__processMessages(sockStruct)
				if (stopCondition == "threadStop"):
					return
			except KeyboardInterrupt:
				# keyboard interrupt to close the server
				self.__shutDown()

	# @brief method to create all the necessary sockets
	# @details reads the Neighbors.csv file to create the sockets. Sockets is an abstracion tha uses the TCP sockets
	# @param filename is the name of the file to be read
	def __createSockets(self, fileName):
		with open(fileName) as neighbords:
			file = csv.reader(neighbords)
			for row in file:  # each row of the file
				if (row[0] == self.__routerID):
					# Neighbors.csv file is a csv, so we access it like an array
					newSocket = self.SocketStruct(self.__serverIP, row[1], row[3], row[4], row[2], int(row[5]))
					self.__connections[row[2]] = newSocket

	# @brief Method to create a thread for connection
	def __createthreads(self):
		connectionsList = self.__connections.values()
		try:
			# connection is a custom socket created in the class SocketStruct
			for connection in connectionsList:
				# the connection with our server is managed by the main thread. Thre is no need to create a thread for this connection
				if (connection.neighbordId != "server"):
						# target of each thread is the __runConnection method
						thread = threading.Thread(target = self.__runConnection, args = (connection,))
						self.threadsArray.append(thread)
						# deamon thread so it destoys itself when it has finished working
						thread.daemon = True

						# thread starts to work
						thread.start()
		except KeyboardInterrupt or OSError or EOFError:
			pass

	# @brief Each thread does the same job of recieving and resending messages
	# @details the general steps to do are: Bind/listen, receive messages, processing messages, resending messages
	# @param sockStruct is an class that can send, receive from/to a router
	def __runConnection(self, sockStruct):
		printMsgTime(f"Conection with {sockStruct.neighbordId} {TXT_GREEN}established{TXT_RESET}")
		while(True):

			sockStruct.bind()
			sockStruct.listen()
			# tries to connect to some router
			newSock = sockStruct.accept()

			# if the connection was succesfull
			if (newSock != None):
				# we create a new SocketStruct to receive the messages
				newSockStruct = self.SocketStruct()
				newSockStruct.sock = newSock
				newSockStruct.neighbordId = sockStruct.neighbordId

				# receives operations through the new socket 
				self.__receiveOperations(newSockStruct, sockStruct)

				# the new socket can be destroyed, it won't be used anymore
				newSockStruct.close()

			# process mesages includes calculating and putting if the corresponding queue to resend if necessary
			stopCondition = self.__processMessages(sockStruct)

			# condition to kill the threads
			if (stopCondition == "threadStop"):
				return

			# resetting the socket so it can connect to resend
			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockStruct.sock.setblocking(0)
			sockStruct.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			if (sockStruct.outQueue.empty() == False and sockStruct.connect()):
				# resend messages form the output queue until it's empty
				self.__resendMessages(sockStruct)

			# resetting the socket so if can accept a new connection
			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockStruct.sock.setblocking(0)
			sockStruct.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# @brief Receives operartions and put them in the in queue
	# @param receiver temporal socketStruct used to receive messages 
	# @param sockStruct porigfinal socket used to manage the connection. This includes the input queue and output queue
	def __receiveOperations(self, receiver, sockStruct):
		while(True):
			# receives messages
			operation = receiver.recvMsg()
			# if the message is timeout, it means the router didn't receive anything it stops receiving
			if (operation == "timeout"):
				# "timeout" is not a messge received by another router. It's a message created by the method recvMsg() in the class SocketStruct
				return
			# puts the message to the input queue
			sockStruct.inQueue.put(operation)

	# @brief Process the messages in the input queue
	# @deatails includes the process of resending and calculating
	# @param sockStruct porigfinal socket used to manage the connection. This includes the input queue and output queue
	def __processMessages(self, sockStruct):
		# process messages until the input queue is empty
		while (not sockStruct.inQueue.empty()):
			message = sockStruct.inQueue.get(block=False)
			
			# stop condition used when the router is closed
			if (message == "threadStop"):
				return "threadStop"
			
			# splt messages is used when the received message includes mre than one operation in json format
			# this happens when the transmitter sends several messages in a short period of time so the receiver receives all the messages in the same buffer
			operations = self.__splitMessage(message)

			# cycle to process al the received messages if theres is more than one
			for oper in operations:
				try:
					jsonMessage = json.loads(oper)

					# checking if the message is a operation
					if (jsonMessage["type"] == "operation"):

						# checks if the message is for this router
						if (jsonMessage["destination"] == self.__routerID):
							printMsgTime(f"Conexion con router {sockStruct.neighbordId} {TXT_RED}procesa{TXT_RESET}: {oper}")

							# if not the message is put in the output queue of the thread that manages the connection with the destiny of the message 
						elif (jsonMessage["destination"] in self.__routingTable["destiny"]):
							# IMPORTANT: We need to check the table to know which connection can reach the destiny
							tableIndex = self.__routingTable["destiny"].index(jsonMessage["destination"])

							if (self.__routingTable["neighbord"][tableIndex] != "-"):
								# if the destiny is in our table we put it in the respective output queue
								self.__connections[self.__routingTable["neighbord"][tableIndex]].outQueue.put(oper)
							else:
								# if we can't get to the destiny, the message is put randomly in a output queue
								# the next router will be responsible of resending to the correct destiny
								randomConnect = random.randint(1, len(self.__connections))
								self.__connections[randomConnect].outQueue.put(oper)

						# checking if the message is a vector
					elif ((jsonMessage["type"] == "vector")):
						# in this case we updated the routing table
						if(self.__updateTable(oper)):
							# after updating the table we send the new table to every neighbor router
							# the router sends its table only if it was updated
							self.__broadcastTable()
				except:
					printMsgTime(f"Connection with router {sockStruct.neighbordId} received an {TXT_RED}unknown message{TXT_RESET}: {oper}")

	# @brief Split a meesage with multiple json messages
	# @param message that may contain multiple json messages
	# @return list with the split result
	def __splitMessage(self, message):
		message =  message[1:len(message)-1]
		
		# the }{ indicates that there is another json message
		split = message.split("}{")
		counter = 0
		for counter in range(0,len(split)):
			split[counter] = "{" + split[counter] + "}"
		# when there aren't more than one json message it returns a list with one message
		return split

	# @brief Resends all the messages of the output queue
	def __resendMessages(self, sockStruct):
		while(sockStruct.outQueue.empty() != True):
			sockStruct.sendMsg(sockStruct.outQueue.get())

	# @brief Creates the routing table
	def __createTable(self):
		# fills the table with default values
		self.__routingTable["neighbord"] = ["-"] * len(self.__availableNodes)
		self.__routingTable["weights"] = [-1] * len(self.__availableNodes)
		connectionsList = self.__connections.values()
		# iterates through the sockets list
		for conn in connectionsList:
			# the socket connected to the server is excluded from the routing table
			if (conn.neighbordId != "server"):
				# index in the table
				tableRowIndex = self.__routingTable["destiny"].index(conn.neighbordId)
				
				# fills the table with the initial values
				self.__routingTable["neighbord"][tableRowIndex] = conn.neighbordId
				self.__routingTable["weights"][tableRowIndex] = conn.weight

	# @brief Compares the table with the new table to update our table
	# @param message that contains the vector snet by another router
	def __updateTable(self, vector):
		table = json.loads(vector)
		isUpdated = False
		for connInfo in table["conn"]:
			# we ignore the connection with this router
			# our table does not need to include a connection to the same router
			if (connInfo["target"] != self.__routerID):

				# index of the table of with the "target" 
				tableRowIndex = self.__routingTable["destiny"].index(connInfo["target"])
				neighborIndex =  self.__routingTable["destinyt"][table["node"]]

				# -1 means with can not reach that target
				if (self.__routingTable["weights"][tableRowIndex] == -1):
					# as we can not reach the target and the new table has this information, we save this new information
					self.__routingTable["neighbord"][tableRowIndex] = table["node"]
					self.__routingTable["weights"][tableRowIndex] = connInfo["weight"]
					isUpdated = True

					# if we can reach the target we check if the new information received is better than the one already saved in our table
				elif(connInfo["weight"] != -1 and self.__routingTable["weights"][neighborIndex] != -1 and connInfo["weight"] < self.__routingTable["weights"][tableRowIndex] + self.__routingTable["weights"][neighborIndex]):

					vecino = self.__routingTable["neighbord"][tableRowIndex]
					target = self.__routingTable["destiny"][tableRowIndex]
					peso = self.__routingTable["weights"][tableRowIndex]
					printMsgTime(f"{TXT_RED}Actualiza:{TXT_RESET} n: {vecino} target: {target} weight: {peso} ")

					# updates the table with the new information
					self.__routingTable["weights"][tableRowIndex] = connInfo["weight"]
					self.__routingTable["neighbord"][tableRowIndex] = table["node"]

					vecino = self.__routingTable["neighbord"][tableRowIndex]
					target = self.__routingTable["destiny"][tableRowIndex]
					peso = self.__routingTable["weights"][tableRowIndex]
					printMsgTime(f"{TXT_RED}Reemplaza con:{TXT_RESET} n: {vecino} target: {target} weight: {peso} ")

					isUpdated = True

		# returns boolean indicating if the table was updated with new and better information or not
		return isUpdated

	# @brief Sends the routing table to each neighbor
	def __broadcastTable(self):
		strTable = self.__formatter.vectorFormat(self.__routingTable, self.__routerID)
		connectionsList = self.__connections.values()
		for conn in connectionsList:
			if (conn.neighbordId != "server"):
				conn.outQueue.put(strTable)

	# @brief Kills all the threads, closes the sockets and closes the router 
	def __shutDown(self):
		# shutdown the server closes the socket
		connectionsList = self.__connections.values()
		for conn in connectionsList:
			# print(conn.inQueue)
			# if (conn.neighbordId != "server"):
			conn.inQueue.put("threadStop")
			conn.close()

		printMsgTime(f'{TXT_RED}|======: Router \"{self.__routerID}\" shut down :======|{TXT_RESET}')
		exit(0)

	# @brief main method to start the router
	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: Router {self.__routerID} started :======|{TXT_RESET}")
		self.__loadAvailableNode()
		self.__createSockets(self.__connectionsFile)
		self.__createTable()
		self.__broadcastTable()
		self.__createthreads()
		self.__connectToServer()
		self.__runConnectionToServer(self.__connections["server"])

	# @class SocketStruct adds functionality to a basic socket
	# @deatils adds the input, putput queue, the id of the neighbor, the id of this router, the weight of the connection and the ports and ips information
	class SocketStruct:
		def __init__(self, routerIp="-", routerPort="-", otherIp="-", otherPort="-", nId = "-", connectionWeight = 0 ):
			# this router info like port, ip and id
			self.neighbordId = nId
			self.thisRouterIp = routerIp
			try:
				self.thisRouterPort = int(routerPort)
			except:
				self.thisRouterPort = routerPort

			# neighbord info
			self.neighbordIp = otherIp
			try:
				self.neighbordPort = int(otherPort)
			except:
				self.neighbordPort = otherPort

			# connection info like port, ip and id
			self.weight = connectionWeight
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setblocking(False) # None blocking socket
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			# messages queues. Output and input queue
			self.inQueue = queue.Queue()
			self.outQueue = queue.Queue()

		# @brief Binds the socket to this router ip and port
		def bind(self):
			self.sock.bind((self.thisRouterIp, self.thisRouterPort))

		# @brief The socket listens
		def listen(self):
			self.sock.listen()

		# @brief Accept a connection
		# @deatials tries to accept multiple times with a random sleeps between each try
		def accept(self):
			tries = 0
			while(tries < 10):
				try:
					sock, address = self.sock.accept()
					return sock
				except:
					# random sleep to avoid problems with other teams
					sleep(random.uniform(0,0.5))
					tries += 1
			return None

		# @brief sends messages
		# @param message to send
		def sendMsg(self, message):
			printMsgTime(f"{TXT_RED}Sent:{TXT_RESET} {message} {TXT_YELLOW}to router {self.neighbordId}{TXT_RESET}")
			self.sock.send(message.encode('UTF-8'))

		# @brief Receives a message
		# @details if nothing is received it returns the message "timeout"
		# @return the received message
		def recvMsg(self):
			message = ""
			try:
				message = self.sock.recv(4096)
				if (not message):
					return "timeout"
				printMsgTime(f"{TXT_RED}Received:{TXT_RESET} {message} {TXT_YELLOW}from router {self.neighbordId}{TXT_RESET}")
				return message.decode('UTF-8')
			except socket.error:
				return "timeout"

		# @brief Connects is an interface
		# @deatils the connect method changes between connection to server or connection to router
		def connect(self):
			if (self.neighbordId.lower() == "server"):
				self.__connectToServer()
				return True
			else:
				return self.__connectToRouter()

		# @brief Method to connecto to a router
		# @details tries to connect multiple times with random sleeps between tries
		def __connectToRouter(self):
			tries = 0
			while(tries < 10):
				try:
					self.sock.connect((self.neighbordIp, self.neighbordPort))
					return True
				except socket.error or socket.timeout:
					sleep(random.uniform(0,1))
					tries += 1
			return False

		# @brief Method to connecto to a sever
		# @details tries to connect multiple times with 1.5 seconds between tries. This connection is only with the server which is easier
		def __connectToServer(self):
			if (self.neighbordIp != "-" or self.neighbordPort != "-"):
				printMsgTime(f"{TXT_YELLOW}Connecting to {self.neighbordId}.{TXT_RESET} ip:{self.neighbordIp} | port:{self.neighbordPort}")
				# tries to connect with server
				while(True):
					try:
						self.sock.connect((self.neighbordIp, self.neighbordPort))
						break
					except socket.error:
						printErrors(f"{self.neighbordId} not found. Retrying connection.")
						sleep(1.5)
				printMsgTime(f"{TXT_GREEN}Connection established to {self.neighbordId}.{TXT_RESET} ip:{self.neighbordIp} | port:{self.neighbordPort}")

		# @brief Closes the socket
		def close(self):
			self.sock.close()

def main():
	print(socket.gethostbyname(socket.gethostname()))
	test =Router("127.0.0.1", "8080", "B")
	test.run()

if (__name__ == '__main__'):
	main()