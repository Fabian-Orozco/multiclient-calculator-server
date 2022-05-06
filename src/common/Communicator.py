# Daniel Escobar Giraldo C 02748

import socket
from datetime import datetime


class Communicator:

	## Constructor
	def __init__(self, socket):
		self.sock = socket           # Socket
		self.BUFFER = 128          # buffer of received messages in bytes

	## Printing method to test class
	# @param msg is the string to print
	def printmsg(self, msg):
		# Print message with current date and time
		# testing function
		current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		print(f'[{current_date_time}] {msg}')


	## Method to send messages to another
	# @param message receives message to send
	# @param destination direction to where that message will be sent
	def sendMessage(self, message, destination):
		# we send message in utf-8 encoding
		self.sock.sendto(message.encode('utf-8'), destination)

	## Method to recieve messages form anyone
	# @return the received message, ipAddress and port of the client
	def receiveMessage(self):
		try:
			# we receive a message with a 128 bytes buffer
			data, client_address = self.sock.recvfrom(self.BUFFER)
		except:
			self.printmsg('Error receiving message')

		return data.decode('utf-8'), client_address


## testing 
# need to remove later
def main():
	print('Hello world')
	ipAddress = '127.0.0.1'
	port = 8080
	socketA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socketA.bind((ipAddress, port))
	test = Communicator(socketA)
	test.printmsg(f'Binded to {ipAddress}:{port}')
	
	message, address = test.receiveMessage()
	print(f'received messages from {address}: {message}')

if (__name__ == '__main__'): 
	main()

