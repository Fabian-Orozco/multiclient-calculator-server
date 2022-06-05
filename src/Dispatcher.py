import ctypes
from PipeManager import *
from Utilities import *
import queue
import socket


class Dispatcher:
	def __init__(self, host, port):
		print("Constructor")

	def dispatch(self):
		try:
			while(True):
				message = receiveMsg()
				if(message == b"stop"):
					print("Cerrando proceso B")
					exit(0)
				printMsgTime(f"{TXT_GREEN}Process B{TXT_RESET} will dispatch the next message: {message.decode('utf-8')}")
		except KeyboardInterrupt:
			closeReadEnd()
			exit(0)
			
		# dispatcher just sends tne consumed messages of the queue to another server for now
		# self.__communicator.sendTcpMessage(message)