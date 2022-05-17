import ctypes
from SimulatorTcp import SimulatorTcp
from Utilities import *
import queue
import socket


class Dispatcher:
	def __init__(self, host, port):
		# destination of the calculation server
		self.__host = host            # server port
		self.__port = port            # server ip

		# creation of TCP to dispatch operations to next layer
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.__communicator = SimulatorTcp(self.__sock, self.__host, self.__port)

	def dispatch(self):
		libPipe = ctypes.CDLL('./libPipe.so')
		libPipe.receiveMsg.restype = ctypes.c_char_p
		try:
			while(True):
				message = libPipe.receiveMsg()
				if(message == b"stop"):
					print("Cerrando proceso B")
					exit(0)
				printMsgTime(f"{TXT_GREEN}Process B{TXT_RESET} will dispatch the next message: {message.decode('utf-8')}")
		except KeyboardInterrupt:
			exit(0)
			
		# dispatcher just sends tne consumed messages of the queue to another server for now
		# self.__communicator.sendTcpMessage(message)
