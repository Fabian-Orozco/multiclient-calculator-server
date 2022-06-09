from fileinput import filename
from multiprocessing import connection
import socket
import threading
import os

from numpy import rint
from Utilities import *
import json
from MessageFormatter import MessageFormatter
import queue
import sys
from time import sleep
import csv



class Router:
	def __init__(self, ip, port, id):
		self.__serverIP = ip # maybe this will deleted
		self.__serverPort = port # maybe this will deleted
		self.__routerID = id
		self.__queuesMaxSize = 10
		self.__socketServer = self.SocketStruct(ip, port, self.__queuesMaxSize, "Server")
		self.__ownIp = socket.gethostbyname(socket.gethostname())

		self.__connectionsFile = "neighbors.csv"
		self.connections = [self.__socketServer]
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
				print(row)
				if (row[0] == self.__routerID):
					self.__loadOwnSocket(row[1])
					self.__loadNeighbordSocket(row[3], row[4], row[2], row[5])

	def __loadOwnSocket(self, port):
		newConnecton = self.SocketStruct(self.__ownIp, port, self.__queuesMaxSize)
		self.connections.append(newConnecton)
		printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Binded socket to ip:{self.__ownIp} | port:{port}.")


	def __loadNeighbordSocket(self, ip, port, id, weight):
		newConnecton = self.SocketStruct(ip, port, self.__queuesMaxSize, id, weight)
		self.connections.append(newConnecton)
		printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Created socket to router {id}, ip:{ip} | port:{port}.")


	def __createthreads(self):
		printMsgTime("Creating threads")

		for connection in self.connections:
			thread = threading.Thread(target = self.__runConnection, args = (connection))
			self.threadsArray.append(thread)

	def __establishConnection(self, sock):
		if (sock.neighbordId != '-'):
			sock.connect()
			printMsgTime(f"{TXT_GREEN}Connection established.{TXT_RESET} Router {sock.neighbordId} | ip:{sock.neighbordIp]} | port:{sock.neighbordPort}")

		else:
			sock.listen()
			sock.accept()
		
		printMsgTime(f"{TXT_GREEN}Connection established.{TXT_RESET} Router {sock.neighbordId} | ip:{sock.neighbordIp]} | port:{sock.neighbordPort}")



	def __runConnection(self, sock):
		

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
		def __init__(self, otherIp, otherPort, maxSize, nId = "-", connectionWeight = 0 ):
			self.neighbordId = nId
			self.neighbordIp = otherIp
			self.neighbordPort = otherPort
			self.weight = connectionWeight
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.inQueue = queue.Queue(maxSize)
			self.outQueue = queue.Queue(maxSize)

		def bind(self, ip, port):
			self.sock.bind((ip,port))

		def listen(self):
			self.sock.listen()

		def accept(self):
			newSocket, address = self.sock.accept()
			self.sock.close()
			self.sock = newSocket

		def sendMsg(self, message):
			printMsgTime(f"{TXT_RED}Testing{TXT_RESET} sent: {message}")
			self.sock.send(message.encode('UTF-8'))

		def recvMsg(self, timeout):
			# maximum timeout is 5 minutes
			self.sock.settimeout(timeout)
			message = ""
			try:
				message = self.sock.recv(4096)
				printMsgTime(f"{TXT_RED}Testing{TXT_RESET} received: {message}")
				return message.decode('UTF-8')
			except socket.timeout:
				# timout reached
				return "timeout"

		def connect(self):
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