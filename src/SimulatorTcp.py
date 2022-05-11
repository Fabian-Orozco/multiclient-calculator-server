import json
import random
import socket
from time import sleep
import Communicator
from datetime import datetime
from colors import *


class SimulatorTcp(Communicator.Communicator):
	def __init__(self, socket, ipAddres, port):
		super().__init__(socket)      # construtor form parent class
		self.__seqValue = 0                  # sequence value
		self.__ack = 0                       # acknoledgement value
		self.__messagePackage = None         # string to accumulate message
		self.__resendTimeout = 2             # timeout of 2 seconds before resending message
		self.__destination = (ipAddres,port) # tuple with destination addres and port

	## function waiting for some client to ask for connection
	def listen(self, newPort):
		# self.__seqValue = random.randint(1000,2000)
		##testing
		# we set seqValue to 
		self.__seqValue = 10

		# wait for connection request message
		# example of connection request mesage
		# {"type":"syn","seq":"0"}
		message, senderAddress = self.receiveMessage()
		connectionRequest = json.loads(message)
		if (connectionRequest['type'] != "syn"):
			return False

		self.printmsg(f"Connection request received from {senderAddress}")

		# we send ack message
		self.__ack = connectionRequest['seq']+1
		self.__destination = senderAddress
		self.__sendAckMessage()

		# receive confirmation
		confirmation, senderAddress = self.receiveMessage()
		if (self.__checkAck(confirmation, senderAddress)):
			# send ack message with new port to connect
			self.__sendNewPort(newPort)
			return True

	## function to ask for connection
	def connect(self):
		# self.__seqValue = random.randint(1000,2000)
		
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
		connectRequest = "{\"type\":\"syn\",\"seq\":"
		connectRequest += f"{self.__seqValue}"
		connectRequest += "}"

		## testing
		self.printmsg(f"Connection request sent message {connectRequest} to {self.__destination}")
		self.sendMessage(connectRequest, self.__destination)

		# confirmation message format: {“type”:”ack”,“ack”:1,”seq”:10}
		# we wait for confirmation
		confirmation, senderAddress = self.receiveMessage()
		if (self.__checkAck(confirmation, senderAddress)):
			self.__accept()
			self.printmsg(f"Connected to new port {self.__destination}")
			return True

		return False
	
	def __sendNewPort(self, newPort):
		ackMesage = "{\"type\":\"ack\",\"ack\":"
		ackMesage += f"{self.__ack}"
		ackMesage += ",\"seq\":"
		ackMesage += f"{self.__seqValue}"
		ackMesage += ",\"port\":"
		ackMesage += f"{newPort}"
		ackMesage += "}"

		## testing 
		self.sendMessage(ackMesage, self.__destination)

	def __accept(self):
		## we sen ack message
		self.__sendAckMessage()

		## now we wait for the message with the new port
		# confirmation message format with new port: {“type”:”ack”,“ack”:”2”,”seq”:”11”,"port":4040}
		confirmation, senderAddress = self.receiveMessage()
		if (self.__checkAck(confirmation, senderAddress)):
			message = json.loads(confirmation)
			self.__destination = list(self.__destination)
			self.__destination[1] = message['port']
			self.__destination = tuple(self.__destination)

			## testing
			self.printmsg(f"Connection accepted, moved to port: {self.__destination}")

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
			# IMPORTANT register ack
			self.__ack = confirmation['seq']+1

			# IMPORTANT register seqValue
			self.__seqValue += 1
			return True

	def __sendAckMessage(self):
		'''
		Asi seria con la clase de format
		# format = MessageFormatter
		# acceptRequest = format.formatAck(self.__seqValue, self.__ack)
		'''
		ackMesage = "{\"type\":\"ack\",\"ack\":"
		ackMesage += f"{self.__ack}"
		ackMesage += ",\"seq\":"
		ackMesage += f"{self.__seqValue}"
		ackMesage += "}" 

		self.sendMessage(ackMesage, self.__destination)

	def sendTcpMessage(self, message):
		self._sock.settimeout(self.__resendTimeout)

		message = "{\"seq\":" + f"{self.__seqValue}," + message + "}"
		## testing
		self.sendMessage(message, self.__destination)
		self.printmsg(f"Message generated: {message} sent to {self.__destination}")

		try:
			response, otherAddress = self.receiveMessage()
			self.__checkAck(response, otherAddress)

			return response
		except socket.timeout:
			self.printmsg(f"No confirmation from server received, sendig again")

	def receiveTcpMessage(self):
		# receive message
		message, otherAddress = self.receiveMessage()
		# testing
		self.printmsg(f"Received message {message} from {otherAddress}")
		# load data to generate ack
		information = json.loads(message)

		# sets the destination address to where the ack message should be sent
		self.__destination = otherAddress

		# checks if there is a sequence number
		if ('seq' in information):
			# send ack message to other part
			self.__ack = information['seq']+1
			self.__seqValue += 1
			self.__sendAckMessage()
			return message

	## Printing method to test class
	# @param msg is the string to print
	def printmsg(self, msg):
		# Imprime el día y la hora actuales + el mensaje enviado por parámetro
		time = datetime.now().strftime('%x - %X')
		print (f'{TXT_BLUE}[{time}]{TXT_RESET} {msg}')

	def setSocket(self, socket):
		self._sock = socket



def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tcp = SimulatorTcp(sock, '127.0.0.1', 8080)
	tcp.sendTcpMessage("jola")
if(__name__ == '__main__'):
	main()



