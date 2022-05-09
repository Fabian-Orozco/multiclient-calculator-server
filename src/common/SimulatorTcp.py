from calendar import c
import json
from operator import truediv
import random
import socket
import Communicator

class SimulatorTcp(Communicator.Communicator):

	def __init__(self, socket, ipAddres, port):
		super().__init__(socket)      # construtor form parent class
		self._seqValue = 0                  # sequence value
		self._ack = 0                       # acknoledgement value
		self._messagePackage = None         # string to accumulate message
		# sefl.timer =                      # timer for connections
		self._destination = (ipAddres,port) # tuple with destination addres and port

	## function waiting for some client to ask for connection
	def listen(self, connectRequest):
		print("nose")

	## function to ask for connection
	def connect(self):
		self._seqValue = random.randint(1000,2000)

		'''
		Asi seria con la clase de format
		# format = MessageFormatter
		# connecRequest = format.formatSyn(self._seqValue)  
		'''
		connectRequest = "{\"type\":\"syn\",\"seq\":"
		connectRequest += f"\"{self._seqValue}\""
		connectRequest += "}"
		print(connectRequest) # testing
		
		self.sendMessage(connectRequest, self._destination)
		if (self._waitConfirmation()):
			self.accept()
			return True
		else:
			return False
	
	def _waitConfirmation(self):
		# confirmation message format: {“type”:”ack”, “ack”:”x+1”,”seq”:”y”}

		confirmation, senderAddress = self.receiveMessage()

		# Testing
		# confirmation = "{\"type\":\"ack\", \"ack\":\"x+1\",\"seq\":\"y\"}"

		# to check if the messages comes form the server
		if (senderAddress != self._destination):
			return False
		confirmation = json.loads(confirmation)

		# we confirm the ack value coming from ther server
		if (confirmation['ack'] == self._seqValue+1):
			# IMPORTANT register ack

			# IMPORTANT register seqValue

			return True
	
	def accept(self):
		'''
		Asi seria con la clase de format
		# format = MessageFormatter
		# acceptRequest = format.formatAck(self._seqValue, self._ack)
		'''
		ackMesage = "{\"type\":\"ack\",\"seq\":"
		ackMesage += f"\"{self._seqValue}\""
		ackMesage += ",\"seq\":"
		ackMesage += f"\"{self._ack}\""
		ackMesage += "}" 
		print(ackMesage) # testing
		# self.sendMessage()



def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tcp = SimulatorTcp(sock, '127.0.0.1', 8080)
	tcp.accept()

if(__name__ == '__main__'):
	main()



