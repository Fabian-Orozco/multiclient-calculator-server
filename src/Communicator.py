# Daniel Escobar Giraldo C 02748
import socket
from datetime import datetime


class Communicator:

	## Constructor
	def __init__(self, socket):
		self._sock = socket           # Socket
		self.__BUFFER = 128          # buffer of received messages in bytes

	## Method to send messages to another
	# @param message receives message to send
	# @param destination direction to where that message will be sent
	# destination parameter is an tuple with the next format: (ipAddress, port)
	def sendMessage(self, message, destination):
		# we send message in utf-8 encoding
		self._sock.sendto(message.encode('utf-8'), destination)

	## Method to recieve messages form anyone
	# @return the received message, ipAddress and port of the client
	def receiveMessage(self):
		# we receive a message with a 128 bytes buffer
		data, client_address = self._sock.recvfrom(self.__BUFFER)
		return data.decode('utf-8'), client_address
