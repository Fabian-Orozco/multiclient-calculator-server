from http import server
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
		self.__ownIp = socket.gethostbyname(socket.gethostname())

		# connection to server info
		self.__serverIP = serverIp # maybe this will deleted
		try:
			self.__serverPort = int(serverPort) # maybe this will deleted
		except:
			self.__serverPort = serverPort
		# self.__socketServer = self.SocketStruct(self.__ownIp, None, serverIp, serverPort, "server")
		
		self.__socketServer = self.SocketStruct("127.0.0.1", None, serverIp, serverPort, "server") # TESTING

		# Info to connect to other routers
		self.__connections = dict({"server":self.__socketServer})
		self.__connectionsFile = "neighbors.csv"
		self.__availableNodes = []
		self.__topologyFile = "topologia.csv"

		# routing table info
		self.__routingTable = {}

		# thread management
		self.threadsArray = []

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
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Thread handles conection with {sockStruct.neighbordId}")
		while(True):
			try:
				self.__receiveOperations(sockStruct, sockStruct)
				
				stopCondition = self.__processMessages(sockStruct)
				if (stopCondition == "threadStop"):
					return
				if (sockStruct.outQueue.empty() == False):
					self.__resendMessages(sockStruct)
			except KeyboardInterrupt:
				self.__shutDown()

	def __createSockets(self, fileName):
		with open(fileName) as neighbords:
			file = csv.reader(neighbords)
			for row in file:  # each row of the file
				if (row[0] == self.__routerID):
					newSocket = self.SocketStruct(self.__ownIp, row[1], row[3], row[4], row[2], row[5])
					self.__connections[row[2]] = newSocket

	def __createthreads(self):

		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Creating threads")
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
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Thread handles conection with {sockStruct.neighbordId}")
		while(True):
			sockStruct.bind()
			sockStruct.listen()
			newSock = sockStruct.accept()
			if (newSock != None):
				newSockStruct = self.SocketStruct()
				newSockStruct.sock = newSock
				self.__receiveOperations(sockStruct)
				newSockStruct.close()

			stopCondition = self.__processMessages(sockStruct)
			if (stopCondition == "threadStop"):
				return

			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			if (sockStruct.outQueue.empty() == False and sockStruct.connect()):
				self.__resendMessages(sockStruct)

			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def __receiveOperations(self, receiver, sockStruct):
		while(True):
			operation = receiver.recvMsg()
			if (operation == "timeout"):
				return
			sockStruct.inQueue.put(operation)

	def __processMessages(self, sockStruct):
		# printMsgTime(f"{TXT_RED}Testing{TXT_RESET} connection with router {sockStruct.neighbordId} is processing messages")
		while (not sockStruct.inQueue.empty()):
			message = sockStruct.inQueue.get(block=False)

			if (message == "threadStop"):
				return "threadStop"

			printMsgTime(f"{TXT_RED}Testing{TXT_RESET} connection with router {sockStruct.neighbordId} is processing: {message}")
			jsonMessage = json.loads(message)

			if (jsonMessage["type"] == "operation"):

				if (jsonMessage["destination"] == self.__routerID):
					printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Parte de oper conexion con router {sockStruct.neighbordId} mensaje: {message}")

				else:
					if (jsonMessage["destination"] in self.__connections):
						# IMPORTANT: We need to check the table to know which connection can reach the destiny
						# right now this doens't check the table
						self.__connections[jsonMessage["destination"]].outQueue.append(message)

			elif ((jsonMessage["type"] == "vector")):
				self.__updateTable(jsonMessage)

			else:
				printMsgTime(f"{TXT_RED}Testing{TXT_RESET} connection with router {sockStruct.neighbordId} received an unknown message: {message}")
		

	def __resendMessages(self, sockStruct):
		x = 0

	def __updateTable(self, newTable):
		x = 0

	def __broadcastTable(self):
		x = 0

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
		print(self.__availableNodes)
		self.__createSockets(self.__connectionsFile)
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
			self.sock.setblocking(0) # None blocking socket

			# messages queues
			self.inQueue = queue.Queue()
			self.outQueue = queue.Queue()

			printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Created socket to router {self.neighbordId}, ip:{self.neighbordIp} | port:{self.neighbordPort}.")


		def bind(self):
			self.sock.bind((self.thisRouterIp, self.thisRouterPort))

		def listen(self):
			self.sock.listen()

		def accept(self):
			try:
				sock, address = self.sock.accept()
				return sock
			except:
				return None

		def sendMsg(self, message):
			printMsgTime(f"{TXT_RED}Testing{TXT_RESET} sent: {message}")
			self.sock.send(message.encode('UTF-8'))

		def recvMsg(self):
			message = ""
			try:
				message = self.sock.recv(4096)
				printMsgTime(f"{TXT_RED}Testing{TXT_RESET} received: {message}")
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
			try:
				self.sock.connect((self.neighbordIp, self.neighbordPort))
				return True
			except socket.error or socket.timeout:
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
	test =Router("127.0.0.1", "8081", "J")
	test.run()

if (__name__ == '__main__'):
	main()