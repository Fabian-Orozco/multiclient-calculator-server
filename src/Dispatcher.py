import ctypes
from Utilities import *
import queue
import socket


class Dispatcher:
	def __init__(self, sock, router):
		self.__routerConnection = sock
		self.__routerID = router

	def dispatch(self, message):
		# dispatcher just sends tne consumed messages of the queue to another server for now
		printMsgTime(f"{TXT_GREEN}Dispatcher{TXT_RESET} will send to router \"{self.__routerID}\" the next message: {message}")

	def shutDown(self):
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Shutting down dispatcher connected to router \"{self.__routerID}\"")
		self.__routerConnection.close()