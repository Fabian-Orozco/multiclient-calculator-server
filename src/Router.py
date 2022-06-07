import socket
import threading
import os
from Utilities import *
import json
from MessageFormatter import MessageFormatter
import queue
import sys
from time import sleep


class Router:
	def __init__(self, ip, port, id):
		self.__serverIP = ip
		self.__serverPort = port
		self.__routerID = id
		self.__SocketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__connectToServer()
	
	def __connectToServer(self):
		printMsgTime(f"{TXT_YELLOW}Connecting to server{TXT_RESET} ip: {self.__serverIP} | poert: {self.__serverPort}")
		# tries to connect with server
		while(True):
			try:
				self.__SocketServer.connect((self.__serverIP, self.__serverPort))
				break
			except KeyboardInterrupt:
				self.__shutDown()
			except:
				printErrors("Server not found. Retrying connection.")
				sleep(5)
		self.__sendMsg(self.__SocketServer, "{\"type\":\"router\",\"id\":\"A\"}")
	
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

	def __shutDown(self):
		printMsgTime(f'{TXT_RED}|======: Shutting down Router \"{self.__routerID}\":======|{TXT_RESET}')
		# shutdown the server closes the socket
		self.__SocketServer.close()
		exit(0)

	def run():
		printMsgTime("Router running")
