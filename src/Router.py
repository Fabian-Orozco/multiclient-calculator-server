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
		self.__routerID = id
		# self.__ownIp = socket.gethostbyname(socket.gethostname())

		# connection to server info
		self.__serverIP = serverIp # maybe this will deleted
		try:
			self.__serverPort = int(serverPort) # maybe this will deleted
		except:
			self.__serverPort = serverPort
		# self.__socketServer = self.SocketStruct(self.__ownIp, None, serverIp, serverPort, "server")
		
		self.__socketServer = self.SocketStruct(serverIp, None, serverIp, serverPort, "server")
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

	def __loadAvailableNode(self):
		with open(self.__topologyFile) as topology:
			file = csv.reader(topology)
			for row in file:  # each row of the file
				if (row[0] != self.__routerID and row[0] not in self.__availableNodes):
					self.__availableNodes.append(row[0])
				if (row[3] != self.__routerID and row[3] not in self.__availableNodes):
					self.__availableNodes.append(row[3])

	def __connectToServer(self):
		# router connects to server only if it received the ip and port from the console arguments
		self.__socketServer.connect()
		if (self.__serverIP != '-' or self.__serverPort != '-'):
			self.__socketServer.sendMsg("{\"type\":\"router\",\"id\":\""+ self.__routerID + "\"}")

	def __runConnectionToServer(self, sockStruct):
		printMsgTime(f"Conection with {sockStruct.neighbordId} {TXT_GREEN}established{TXT_RESET}")
		while(True):
			try:
				self.__receiveOperations(sockStruct, sockStruct)
				
				stopCondition = self.__processMessages(sockStruct)
				if (stopCondition == "threadStop"):
					return
			except KeyboardInterrupt:
				self.__shutDown()

	def __createSockets(self, fileName):
		with open(fileName) as neighbords:
			file = csv.reader(neighbords)
			for row in file:  # each row of the file
				if (row[0] == self.__routerID):
					newSocket = self.SocketStruct(self.__serverIP, row[1], row[3], row[4], row[2], int(row[5]))
					self.__connections[row[2]] = newSocket

	def __createthreads(self):
		connectionsList = self.__connections.values()
		try:
			for connection in connectionsList:
				if (connection.neighbordId != "server"):
						thread = threading.Thread(target = self.__runConnection, args = (connection,))
						self.threadsArray.append(thread)
						# deamon thread so it destoys itself when it has finished working
						thread.daemon = True

						# thread starts to work
						thread.start()
		except KeyboardInterrupt or OSError or EOFError:
			pass


	def __runConnection(self, sockStruct):
		printMsgTime(f"Conection with {sockStruct.neighbordId} {TXT_GREEN}established{TXT_RESET}")
		while(True):
			sockStruct.bind()
			sockStruct.listen()
			newSock = sockStruct.accept()

			if (newSock != None):
				newSockStruct = self.SocketStruct()
				newSockStruct.sock = newSock
				newSockStruct.neighbordId = sockStruct.neighbordId
				self.__receiveOperations(newSockStruct, sockStruct)
				newSockStruct.close()

			stopCondition = self.__processMessages(sockStruct)
			if (stopCondition == "threadStop"):
				return

			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockStruct.sock.setblocking(0)
			sockStruct.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			if (sockStruct.outQueue.empty() == False and sockStruct.connect()):
				self.__resendMessages(sockStruct)

			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockStruct.sock.setblocking(0)
			sockStruct.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def __receiveOperations(self, receiver, sockStruct):
		while(True):
			operation = receiver.recvMsg()
			if (operation == "timeout"):
				return
			sockStruct.inQueue.put(operation)

	def __processMessages(self, sockStruct):
		while (not sockStruct.inQueue.empty()):
			message = sockStruct.inQueue.get(block=False)
			if (message == "threadStop"):
				return "threadStop"
			operations = self.__splitMessage(message)
			for oper in operations:
				try:
					jsonMessage = json.loads(oper)
					if (jsonMessage["type"] == "operation"):

						if (jsonMessage["destination"] == self.__routerID):
							printMsgTime(f"Conexion con router {sockStruct.neighbordId} {TXT_RED}procesa{TXT_RESET}: {oper}")

						elif (jsonMessage["destination"] in self.__routingTable["destiny"]):
							# IMPORTANT: We need to check the table to know which connection can reach the destiny
							tableIndex = self.__routingTable["destiny"].index(jsonMessage["destination"])
							if (self.__routingTable["neighbord"][tableIndex] != "-"):
								self.__connections[self.__routingTable["neighbord"][tableIndex]].outQueue.put(oper)
							else:
								# if we can't get to the destiny, the message ius assugned randomly to a connection
								randomConnect = random.randint(1, len(self.__connections))
								self.__connections[randomConnect].outQueue.put(oper)


					elif ((jsonMessage["type"] == "vector")):
						if(self.__updateTable(oper)):
							self.__broadcastTable()
				except:
					printMsgTime(f"Connection with router {sockStruct.neighbordId} received an {TXT_RED}unknown message{TXT_RESET}: {oper}")



	def __splitMessage(self, message):
		message =  message[1:len(message)-1]
		split = message.split("}{")
		counter = 0
		for counter in range(0,len(split)):
			split[counter] = "{" + split[counter] + "}"
		return split

	def __resendMessages(self, sockStruct):
		while(sockStruct.outQueue.empty() != True):
			sockStruct.sendMsg(sockStruct.outQueue.get())

	def __createTable(self):
		self.__routingTable["neighbord"] = ["-"] * len(self.__availableNodes)
		self.__routingTable["weights"] = [-1] * len(self.__availableNodes)
		connectionsList = self.__connections.values()
		for conn in connectionsList:
			if (conn.neighbordId != "server"):
				x=0
				tableRowIndex = self.__routingTable["destiny"].index(conn.neighbordId)
				self.__routingTable["neighbord"][tableRowIndex] = conn.neighbordId
				self.__routingTable["weights"][tableRowIndex] = conn.weight

	def __updateTable(self, vector):
		table = json.loads(vector)
		isUpdated = False
		for connInfo in table["conn"]:
			if (connInfo["target"] != self.__routerID):
				tableRowIndex = self.__routingTable["destiny"].index(connInfo["target"])
				if (self.__routingTable["weights"][tableRowIndex] == -1):
					self.__routingTable["neighbord"][tableRowIndex] = table["node"]
					self.__routingTable["weights"][tableRowIndex] = connInfo["weight"]
					isUpdated = True
				elif(connInfo["weight"] != -1 and connInfo["weight"] < self.__routingTable["weights"][tableRowIndex]):
					isUpdated = True
		return isUpdated


	def __broadcastTable(self):
		strTable = self.__formatter.vectorFormat(self.__routingTable, self.__routerID)
		connectionsList = self.__connections.values()
		for conn in connectionsList:
			if (conn.neighbordId != "server"):
				conn.outQueue.put(strTable)

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

	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: Router {self.__routerID} started :======|{TXT_RESET}")
		self.__loadAvailableNode()
		self.__createSockets(self.__connectionsFile)
		self.__createTable()
		self.__broadcastTable()
		self.__createthreads()
		self.__connectToServer()
		self.__runConnectionToServer(self.__connections["server"])


	class SocketStruct:
		def __init__(self, routerIp="-", routerPort="-", otherIp="-", otherPort="-", nId = "-", connectionWeight = 0 ):
			# this actual router info
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

			# connection info
			self.weight = connectionWeight
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setblocking(False) # None blocking socket
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			# messages queues
			self.inQueue = queue.Queue()
			self.outQueue = queue.Queue()

		def bind(self):
			self.sock.bind((self.thisRouterIp, self.thisRouterPort))

		def listen(self):
			self.sock.listen()

		def accept(self):
			tries = 0
			while(tries < 10):
				try:
					sock, address = self.sock.accept()
					return sock
				except:
					sleep(random.uniform(0,0.5))
					tries += 1
			return None

		def sendMsg(self, message):
			printMsgTime(f"{TXT_RED}Sent:{TXT_RESET} {message} {TXT_YELLOW}to router {self.neighbordId}{TXT_RESET}")
			self.sock.send(message.encode('UTF-8'))

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

		def connect(self):
			if (self.neighbordId.lower() == "server"):
				self.__connectToServer()
				return True
			else:
				return self.__connectToRouter()

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

		def close(self):
			self.sock.close()


def main():
	print(socket.gethostbyname(socket.gethostname()))
	test =Router("127.0.0.1", "8080", "B")
	test.run()

if (__name__ == '__main__'):
	main()