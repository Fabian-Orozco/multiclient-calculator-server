from concurrent.futures import process
from fileinput import filename
from hmac import new
from multiprocessing import connection
import socket
import threading
import os
from turtle import Turtle
from warnings import catch_warnings

from numpy import rint
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
		self.__queuesMaxSize = 10
		self.__ownIp = socket.gethostbyname(socket.gethostname())

		# connection to server info
		self.__serverIP = serverIp # maybe this will deleted
		try:
			self.__serverPort = int(serverPort) # maybe this will deleted
		except:
			self.__serverPort = serverPort
		self.__socketServer = self.SocketStruct(self.__ownIp, None, serverIp, serverPort, "server")

		# Info to connect to other routers
		self.__connections = dict({"server":self.__socketServer})
		self.__connectionsFile = "neighbors.csv"
	
		# routing table info
		self.__routingTable = {}
		self.__tableUpdatesQueue = queue.Queue()

		# thread management
		self.threadsArray = []
	
	def __connectToServer(self):
		# router connects to server only if it received the ip and port from the console arguments
		self.__socketServer.connect()
		if (self.__serverIP != '-' or self.__serverPort != '-'):
			self.__socketServer.sendMsg("{\"type\":\"router\",\"id\":\""+ self.__routerID + "\"}")

	def __createSockets(self, fileName):
		with open(fileName) as topology:
			file = csv.reader(topology)
			for row in file:  # each row of the file
				if (row[0] == self.__routerID):
					newSocket = self.SocketStruct(self.__ownIp, row[1], row[3], row[4], row[2], row[5])
					self.__connections[row[2]] = newSocket


	def tableUpdater(self):
		x=0

	def __createthreads(self):
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Creating threads")
		connectionsList = self.__connections.values()
		for connection in connectionsList:
			thread = threading.Thread(target = self.__runConnection, args = (connection,))
			self.threadsArray.append(thread)
			# deamon thread so it destoys itself when it has finished working
			thread.daemon = True

			# thread starts to work
			thread.start()

	def __runConnection(self, sockStruct):
		x = 0
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Thread handles conection with {sockStruct.neighbordId}")
		while(True):
			sockStruct.bind()
			sockStruct.listen()
			newSock = sockStruct.accept()
			if (newSock != None):
				newSockStruct = self.SocketStruct()
				newSockStruct.sock = newSock
				self.__receivesOperations(sockStruct)
				newSockStruct.close()

			self.__processMessages(sockStruct)

			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			if (sockStruct.outQueue.empty() == False and sockStruct.connect()):
				self.__resendMessages(sockStruct)

			sockStruct.close()
			sockStruct.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def __receivesOperations(self, receiver, sockStruct):
		while(True):
			operation = receiver.recvMsg()
			if (operation == "timeout"):
				return
			sockStruct.inQueue.append(operation)

	def __processMessages(self, sockStruct):
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} connection with router {sockStruct.neighbordId} is processing messages")
		while (not sockStruct.inQueue.empty()):
			message = sockStruct.inQueue.pop(block=False)
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
				self.__tableUpdatesQueue.append(message)

			else:
				printMsgTime(f"{TXT_RED}Testing{TXT_RESET} connection with router {sockStruct.neighbordId} received an unknown message: {message}")
		return

	def __resendMessages(self, sockStruct):
		x = 0

	def __shutDown(self):
		printMsgTime(f'{TXT_RED}|======: Shutting down Router \"{self.__routerID}\":======|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__socketServer.close()
		exit(0)

	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: Router {self.__routerID} started :======|{TXT_RESET}")
		self.__connectToServer()

		self.__createSockets(self.__connectionsFile)
		self.__createthreads()

	class SocketStruct:
		def __init__(self, routerIp="-", routerPort="-", otherIp="-", otherPort="-", nId = "-", connectionWeight = 0 ):
			# this actual router info
			self.neighbordId = nId
			self.thisRouterIp = routerIp
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

			# messages queues
			self.inQueue = queue.Queue()
			self.outQueue = queue.Queue()

			printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Created socket to router {self.neighbordId}, ip:{self.neighbordIp} | port:{self.neighbordPort}.")


		def bind(self):
			self.sock.bind((self.thisPort,self.thisRouterIp))

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
			# maximum timeout is 5 minutes
			self.sock.settimeout(0)
			message = ""
			try:
				message = self.sock.recv(4096)
				printMsgTime(f"{TXT_RED}Testing{TXT_RESET} received: {message}")
				return message.decode('UTF-8')
			except socket.timeout:
				# timout reached
				return "timeout"

		def connect(self):
			if (self.neighbordId == "Server"):
				self.__connectToServer()
				return True
			else:
				return self.__connectToRouter()

		def __connectToRouter(self):
			try:
				self.sock.connect((self.neighbordIp, self.neighbordPort))
				return True
			except socket.error:
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
						sleep(5)
				printMsgTime(f"{TXT_GREEN}Connection established to {self.neighbordId}.{TXT_RESET} ip:{self.neighbordIp} | port:{self.neighbordPort}")

		def close(self):
			self.sock.close()


def main():
	print(socket.gethostbyname(socket.gethostname()))
	test =Router("-", "-", "J")
	test.run()

if (__name__ == '__main__'):
	main()