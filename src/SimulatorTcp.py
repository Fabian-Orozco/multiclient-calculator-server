import json
import random
import socket

import Communicator
from datetime import datetime
from MessageFormatter import MessageFormatter
from Utilities import *

class SimulatorTcp(Communicator.Communicator):
	def __init__(self, socket, ipAddres, port):
		super().__init__(socket)             # construtor form parent class
		self.__seqValue = 0                  # sequence value
		self.__ack = 0                       # acknoledgement value
		self.__resendTimeout = 2             # timeout of 2 seconds before resending message
		self.__maxTries = 4                  # maximum of resends before disconnecting
		self.__destination = (ipAddres,port) # tuple with destination address and port
		self.__formatter = MessageFormatter()

	## function waiting for some client to ask for connection
	# @remark, this does the handshake form the receiver part
	# @param newPort is the new port to which the client will be connected
	# return false if the handshake fails
	def listen(self, newPort):
		self._sock.settimeout(None)
		self.__seqValue = random.randint(100,999)

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
			ackMesageAndPort = self.__formatter.formatAck(self.__seqValue, self.__ack, newPort)
			self._sendMessage(ackMesageAndPort, self.__destination)
			printMsgTime(f"{TXT_GREEN}Connection established{TXT_RESET} to ip:{self.__destination[0]} | port:{self.__destination[1]}")
			return True

	## function to ask for connection
	# @remark, this does the handshake form the sender part
	# return false if the handshake fails
	def connect(self):
		self.__seqValue = random.randint(100,999)

		## Example of connection request mesage
		# {"type":"syn","seq":"0"}
		self._sock.settimeout(self.__resendTimeout)

		connectRequest = self.__formatter.formatSyn(self.__seqValue)

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
				printMsgTime(f"{TXT_GREEN}Connection established{TXT_RESET} to ip:{self.__destination[0]} | port:{self.__destination[1]}")
				return True

		return False		

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
		ackMesage = self.__formatter.formatAck(self.__seqValue, self.__ack)

		self._sendMessage(ackMesage, self.__destination)


	##Method to send a message with json format
	# @param the message to be sent. Needs to be alreay formatted
	# return true if the message was succesfully sent and the ack was correctly checked. Otherwise returns false
	def sendTcpMessage(self, message):
		# checks if message can be send directly
		# max message length is 128 (buffer size)
		if (len(message) >= self._BUFFER):
			print(f"hay que dividir: {message}")
			# message is too long, we divide
			messagesQueue = self.__divideMessage(message)
			i = 0
			# iuterates through queue and sends every message
			for i in messagesQueue:
				if (self.__sendTcp(i) == False ):
					return False
			return True
		else:
			print(f"No hay que dividir: {message}")
			# message is not too long, so we send it
			return self.__sendTcp(message)


	## Method to divide a message in multiple messages
	# @param the message to divide
	# @return queue of messages to send (this are calculated form the original message)
	def __divideMessage(self, message):
		jsonMessage = "{" + message
		messageData = json.loads(jsonMessage)
		# loads the opreation
		operation = messageData["operation"]

		# adds 2 to count the " at the beginning and the end
		operationSize = len(operation)+2

		# extracts metadata of message
		# metadata is all the data used by tcp, not the actual message
		metaData = message[0:message.find("\"operation\":")+13]
		
		# metadata also contains tne next string at the beginning {"seq":1258,
		# so we add the length of this string to have ea more accurate calculation
		metaDataSize = len(metaData) + 12
		
		# the minimum of divisions is 2
		messageQuantity = 2

		# determines quantity of messages to create
		while (True):
			if (((operationSize / messageQuantity) + metaDataSize) < self._BUFFER ):
				break
			else:
				messageQuantity = messageQuantity + 1

		# queue to store the multiple messages
		messagesToSend = []
		tempMessage = ""

		# size of every message
		partitionSize = int(operationSize / messageQuantity)
		start = 0
		end = partitionSize

		# loop top generate all the messages
		i = 0
		newMetaData = str(metaData)
		newMetaData = newMetaData.replace("\"fin\":true", "\"fin\":false")
		while (i < (messageQuantity - 1)):
			tempMessage = operation[start:end]
			tempMessage = newMetaData + tempMessage + "\"}"
			messagesToSend.append(tempMessage)
			i = i + 1
			if (i != (messageQuantity - 1)):
				start = end
				end += partitionSize
		tempMessage = operation[end:]
		tempMessage = metaData + tempMessage + "\"}"
		messagesToSend.append(tempMessage)

		# return the messages queue
		return messagesToSend

	## Send a TCP message
	# @remark method already waits for the ack and checks it
	# @param the message to send
	# @return true if the message was succesfully sent and the ack was correctly checked.
	def __sendTcp(self, message):
		self._sock.settimeout(self.__resendTimeout)

		self.__seqValue += 1
		message = "{" + self.__formatter.jsonFormat("seq", self.__seqValue, ",") + message

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

	## Methoid to receive a TCP message
	# remark the method detects if messages are complete or not. If not it returns the general message
	# @remark method sends the ack
	# @return tthe received message
	def receiveTcpMessage(self):
		message = self.__receiveTcp()
		if (message == "timeout"):
			return message

		jsonMessage = json.loads(message)

		if ("fin" in jsonMessage and jsonMessage["fin"] == False):
			message = self.__joinMessages(message)
	
		return message


	## Methoid to receive a TCP message
	# remark the method receives messages in json format
	# @remark method sends the ack
	# @return tthe received message
	def __joinMessages(self, firstMessage):
		self._sock.settimeout(None)
		completeMessage = str(firstMessage)[0:len(firstMessage)-2]

		tempMessage = ""
		while(True):
			tempMessage = self.__receiveTcp()
			tempMessage = json.loads(tempMessage)
			completeMessage += tempMessage["operation"]
			if (tempMessage["fin"] == True):
				break

		completeMessage = completeMessage.replace("\"fin\":false", "\"fin\":true")
		completeMessage += "\"}"
		return completeMessage

	def __receiveTcp(self):
		try:
			# receive message
			message, otherAddress = self._receiveMessage()
		except socket.timeout:
			return "timeout"
		self.__destination = otherAddress
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

	def close(self):
		self._sock.close()

	def setTimeout(self, timeout):
		self._sock.settimeout(timeout)
