# Daniel Escobar Giraldo C 02748
import socket
from Cypher import Cypher
from Utilities import *


class Communicator:

	## Constructor
	def __init__(self, socket):
		self._sock = socket           # Socket
		self._BUFFER = 128          # buffer of received messages in bytes
		self.__cypher = Cypher()             # to encrypt ad decrypt messages


	## Method to send messages to another
	# @param message receives message to send
	# @param destination direction to where that message will be sent
	# destination parameter is an tuple with the next format: (ipAddress, port)
	def _sendMessage(self, message, destination):
		# we send message in utf-8 encoding
		# testing 
		printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Send message: "+ message + f" to {destination}")
		message = self.__cypher.encrypt(message)
		self._sock.sendto(message.encode('utf-8'), destination)

	## Method to recieve messages form anyone
	# @return the received message, ipAddress and port of the client
	def _receiveMessage(self):
		# we receive a message with a 128 bytes buffer
		data, client_address = self._sock.recvfrom(self._BUFFER)
		printMsgTime(f"{TXT_RED}Testing:{TXT_RESET} Received message: {data}" + f" from {client_address}")
		data = self.__cypher.decrypt(data.decode('utf-8'))
		# testing 
		return data, client_address
