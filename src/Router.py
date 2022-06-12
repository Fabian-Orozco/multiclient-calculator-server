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
		self.__serverIP = ip
		self.__serverPort = port
		self.__routerID = id
		self.__queuesMaxSize = 10
		self.__socketServer = self.SocketStruct(ip, port, self.__queuesMaxSize, "Server")
		self.__ownIp = socket.gethostbyname(socket.gethostname())
	
	def __connectToServer(self):
		# router connects to server only if it received the ip and port from the console arguments
		if (self.__socketServer.connect() == False):
			self.__shutDown()
		self.__socketServer.sendMsg("{\"type\":\"router\",\"id\":\""+ self.__routerID + "\"}")

	def __createSockets(self, fileName):
		x = 0


	def __loadOwnSocket(self, port):
		x = 0

	def __loadNeighbordsSocket():
		x = 0

	def __shutDown(self):
		printMsgTime(f'{TXT_RED}|======: Shutting down Router \"{self.__routerID}\":======|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__socketServer.sock.close()
		exit(0)

	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: Router {self.__routerID} started :======|{TXT_RESET}")
		self.__connectToServer()

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
def main():
	print(socket.gethostbyname(socket.gethostname()))

if (__name__ == '__main__'):
	main()