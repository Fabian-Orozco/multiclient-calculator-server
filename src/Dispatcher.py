from sklearn import neighbors
from Utilities import *
import random
from time import sleep

import TempPackager
from MessageFormatter import MessageFormatter
import csv

filename = "topologia.csv"

class Dispatcher:
	def __init__(self):
		self.__neighborsSockets = []
		self.__neighborsIDs = []
		self.__allNodesIDs = []
		self.__formatter = MessageFormatter()
		self.__loadAvailableNode()
	
	def __loadAvailableNode(self):
		with open(filename) as topology:
			file = csv.reader(topology)
			for row in file:  # each row of the file
				if (row[0] not in self.__allNodesIDs):
					self.__allNodesIDs.append(row[0])
				if (row[3] not in self.__allNodesIDs):
					self.__allNodesIDs.append(row[3])

	def updateRoutersAvailables(self, sock, ID):
		self.__neighborsIDs.append(ID)
		self.__neighborsSockets.append(sock)

	def dispatch(self, operations):
		list = self.operationsDivider(operations)
		router = random.randint(0,len(self.__neighborsIDs)-1)
		destination = random.randint(0,len(self.__allNodesIDs)-1)
		print("len de sockets: " , len(self.__neighborsSockets))
		print("__neighborsIDs: " , self.__neighborsIDs)
		print("allNodesIDs: " , self.__allNodesIDs)
		print("destination: " , destination)

		for operation in list:
			# source , destination, packet, order, operation
			msg = self.__formatter.operationToRouter(0, self.__allNodesIDs[destination], 0, 0, operation)
			while(True):
				try:
					print("intentando enviar")
					sleep(3)
					self.__neighborsSockets[router].send(msg.encode('UTF-8'))
					print("si envio")
					sleep(3)
					#printMsgTime(f"{TXT_GREEN}Dispatcher{TXT_RESET} will send {TXT_YELLOW} to router {destination} the next message: {operation}")
					router = (router + 1) % len(self.__neighborsIDs)
					break
				except:
					printErrors(f"{TXT_RED}Testing{TXT_RESET} could not send {TXT_YELLOW} to router {self.__neighborsIDs[router]}{TXT_RESET}")
					router = (router + 1) % len(self.__neighborsIDs)

		# dispatcher just sends tne consumed messages of the queue to another server for now
		# printMsgTime(f"{TXT_GREEN}Dispatcher{TXT_RESET} will send to router \"{self.__routerID}\" the next message: {message}")

	def shutDown(self):
		# printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Shutting down dispatcher")
		for router in self.__routersAvailables:
			router.close()
	
	# para este punto, ya hizo connect
	def __send(sock, operation, destination):
		try:
			sock.send(operation.encode('UTF-8'))
			printMsgTime(f"{TXT_GREEN}Dispatcher{TXT_RESET} will send {TXT_YELLOW} to router {destination} the next message: {operation}")
		except:
			sleep(10)
			print("nel")

	def operationsDivider(self, operation):
		return TempPackager.split(operation)

def main():

	operation = input("server recibe operacion: ")
	ds = Dispatcher()
	ds.operationsDivider(operation)


if __name__ == "__main__":
	main()