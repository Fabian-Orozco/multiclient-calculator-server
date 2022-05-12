import json
import random
import socket
from time import sleep
import Communicator
from datetime import datetime
from Utilities import *

class SimulatorTcp(Communicator.Communicator):
	def __init__(self, socket, ipAddres, port):
		super().__init__(socket)             # construtor form parent class
		self.__seqValue = 0                  # sequence value
		self.__ack = 0                       # acknoledgement value
		self.__resendTimeout = 2             # timeout of 2 seconds before resending message
		self.__maxTries = 4                  # maximum of resends before disconnecting
		self.__destination = (ipAddres,port) # tuple with destination address and port

	## function waiting for some client to ask for connection
	def listen(self, newPort):
		self._sock.settimeout(None)
		#self.__seqValue = random.randint(1000,2000)
		##testing
		# we set seqValue to 
		self.__seqValue = 10

		# wait for connection request message
		# example of connection request mesage
		# {"type":"syn","seq":"0"}
		message, senderAddress = self._receiveMessage()
		printMsgTime(f"{TXT_YELLOW}Connecting to ip:{senderAddress[0]} | port:{senderAddress[1]}{TXT_RESET}")

		connectionRequest = json.loads(message)
		if (connectionRequest['type'] != "syn"):
			return False

		# we send ack message
		self.__ack = connectionRequest['seq']+1
		self.__destination = senderAddress

		self._sock.settimeout(self.__resendTimeout)
		sendTries = 0;
		while(sendTries < self.__maxTries):
			self.__sendAckMessage()

			try:
				# receive confirmation
				confirmation, senderAddress = self._receiveMessage()
				break
			except socket.timeout:
				## testing
				printErrors("Resending request.")
				sendTries += 1
		if (sendTries == self.__maxTries):
			printErrors("Could not establish connection.")
			return False

		if (self.__checkAck(confirmation, senderAddress)):
			confirmation = json.loads(confirmation)
			# IMPORTANT register ack
			self.__ack = confirmation['seq']+1

			# IMPORTANT increment seqValue
			self.__seqValue += 1
			# send ack message with new port to connect
			self.__sendNewPort(newPort)
			printMsgTime(f"{TXT_GREEN}Connection established to ip:{self.__destination[0]} | port:{self.__destination[1]} {TXT_RESET}")
			return True

	## function to ask for connection
	def connect(self):
		#self.__seqValue = random.randint(1000,2000)
		
		##testing
		# we set seqValue to 
		self.__seqValue = 0

		## Example of connection request mesage
		# {"type":"syn","seq":"0"}
		'''
		Asi seria con la clase de format
		# format = MessageFormatter
		# connecRequest = format.formatSyn(self.__seqValue)  
		'''
		self._sock.settimeout(self.__resendTimeout)
		connectRequest = "{\"type\":\"syn\",\"seq\":" + f"{self.__seqValue}" + "}"
		sendTries = 0;
		printMsgTime(f"{TXT_YELLOW}Connecting to ip:{self.__destination[0]} | port:{self.__destination[1]}{TXT_RESET}")
		while(sendTries < self.__maxTries):
			self._sendMessage(connectRequest, self.__destination)

			try:
				# confirmation message format: {“type”:”ack”,“ack”:1,”seq”:10}
				# waits for confirmation message
				confirmation, senderAddress = self._receiveMessage()
				break
			except socket.timeout:
				## testing
				printErrors("Resending request.")
				sendTries += 1
		if (sendTries == self.__maxTries):
			printErrors("Could not establish connection.")
			return False

		if (self.__checkAck(confirmation, senderAddress)):
			confirmation = json.loads(confirmation)
			# IMPORTANT register ack
			self.__ack = confirmation['seq']+1

			if (self.__accept()):
				printMsgTime(f"{TXT_GREEN}Connection established to ip:{self.__destination[0]} | port:{self.__destination[1]}{TXT_RESET}")
				return True

		return False
	
	def __sendNewPort(self, newPort):
		ackMesage = "{\"type\":\"ack\",\"ack\":" + f"{self.__ack},\"seq\":" + f"{self.__seqValue},\"port\":" + f"{newPort}" + "}"

		## testing
		self._sendMessage(ackMesage, self.__destination)

	def __accept(self):
		sendTries = 0;
		# IMPORTANT increment seqValue
		self.__seqValue += 1
		while(sendTries < self.__maxTries):
			## we send ack message
			self.__sendAckMessage()

			try:
				## now we wait for the message with the new port
				# confirmation message format with new port: {“type”:”ack”,“ack”:”2”,”seq”:”11”,"port":4040}
				confirmation, senderAddress = self._receiveMessage()
				break
			except socket.timeout:
				## testing
				printErrors("Resending request.")
				sendTries += 1

		if (sendTries == self.__maxTries):
			printErrors("Could not establish connection.")
			return False

		if (self.__checkAck(confirmation, senderAddress)):
			confirmation = json.loads(confirmation)
			self.__destination = list(self.__destination)
			self.__destination[1] = confirmation['port']
			self.__destination = tuple(self.__destination)

			# IMPORTANT register ack
			self.__ack = confirmation['seq']+1
			return True
		return False

	## function to check the received ack
	# @param confirmation is the messaged received
	# @param senderAddress is the addres from where the message was received
	def __checkAck(self, confirmation, senderAddress):
		# confirmation message format: {“type”:”ack”,“ack”:”x+1”,”seq”:”y”}
		# to check if the message comes from the server
		if (senderAddress != self.__destination):
			return False

		confirmation = json.loads(confirmation)
		if (confirmation['type'] != "ack"):
			return False

		# we confirm the ack value coming from ther server
		if (confirmation['ack'] == self.__seqValue+1):
			return True

	def __sendAckMessage(self):
		'''
		Asi seria con la clase de format
		# format = MessageFormatter
		# acceptRequest = format.formatAck(self.__seqValue, self.__ack)
		'''
		ackMesage = "{\"type\":\"ack\",\"ack\":" + f"{self.__ack},\"seq\":" + f"{self.__seqValue}" + "}" 
		self._sendMessage(ackMesage, self.__destination)

	def sendTcpMessage(self, message):
		self._sock.settimeout(self.__resendTimeout)

		self.__seqValue += 1
		message = "{\"seq\":" + f"{self.__seqValue}," + message + "}"

		# IMPORTANT increment seqValue

		sendTries = 0;
		while(sendTries < self.__maxTries):
			self._sendMessage(message, self.__destination)

			try:
				response, otherAddress = self._receiveMessage()
				if (response and self.__checkAck(response, otherAddress)):
					response = json.loads(response)
					# IMPORTANT register ack
					self.__ack = response['seq']+1
					return True
				else:
					return False
			except socket.timeout:
				printErrors("Resending request.")
				sendTries += 1

		if (sendTries == self.__maxTries):
			printErrors("Closing connection.")
			return False

	def receiveTcpMessage(self):
		# receive message
		message, otherAddress = self._receiveMessage()

		# load data to generate ack
		information = json.loads(message)

		# checks if there is a sequence number
		if ('seq' in information):
			# send ack message to other part
			self.__ack = information['seq']+1
			self.__seqValue += 1
			self.__sendAckMessage()
			return message
		return "null"

	def getSeqAck(self):
		return (self.__seqValue, self.__ack)

	def setSeqAck(self, values):
		self.__seqValue = values[0]
		self.__ack = values[1]

	def setSocket(self, socket):
		self._sock = socket

	def getDestination(self):
		return self.__destination
	
	def setDestination(self, newDestination):
		self.__destination = newDestination