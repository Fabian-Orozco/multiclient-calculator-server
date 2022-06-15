# UCR/ECCI/PI_redesOper Equipo 7 raspado.

from Utilities import *
import random
from time import sleep

import TempPackager
from MessageFormatter import MessageFormatter
import csv

filename = "topologia.csv"

# se encarga de enviar los partes de las operaciones a los routers de la topología
class Dispatcher:
	def __init__(self):
		self.__neighborsSockets = []			# conexiones del server
		self.__neighborsIDs = []				# IDs de las conexiones del server
		self.__allNodesIDs = []					# todos los IDs de la topologia
		self.__loadAvailableNode()				# llena IDs de la topologia
		self.__formatter = MessageFormatter()
	
	# llena el atributo con los IDs de la topologia
	def __loadAvailableNode(self):
		with open(filename) as topology:
			file = csv.reader(topology)
			for row in file:  # each row of the file
				# no repite letras
				if (row[0] not in self.__allNodesIDs):
					self.__allNodesIDs.append(row[0])
				if (row[3] not in self.__allNodesIDs):
					self.__allNodesIDs.append(row[3])

	# lo invoca el server cada que un router se conecta
	# agrega el socket y el ID del router
	def updateRoutersAvailables(self, sock, ID):
		self.__neighborsIDs.append(ID)
		self.__neighborsSockets.append(sock)

	# recibe la operacion, la divide y reparte entre routers
	def dispatch(self, operation):
		list = self.operationsDivider(operation)					# invoca a packager para dividir la operacion
		router = random.randint(0,len(self.__neighborsIDs)-1)  		# router to send (initially)
		destination = random.randint(0,len(self.__allNodesIDs)-1)  	# target router (to process)

		for operation in list:
			# params: source , destination, packet, order, operation
			msg = self.__formatter.operationToRouter(0, self.__allNodesIDs[destination], 0, 0, operation)
			while(True):
				try:
					# intenta hacer send a un router aleatorio, lo recibirá solo si está en receive.
					self.__neighborsSockets[router].send(msg.encode('UTF-8'))

					printMsgTime(f"{TXT_GREEN}Dispatcher{TXT_RESET} will send {TXT_YELLOW}to router {self.__neighborsIDs[router]}{TXT_RESET} | target: {TXT_YELLOW}{self.__allNodesIDs[destination]}{TXT_RESET} the operation: {operation}")
					break
				except:
					printErrors(f"{TXT_RED}Testing{TXT_RESET} could not send {TXT_YELLOW} to router {self.__neighborsIDs[router]}{TXT_RESET}")
				# aumenta contador: para intentar enviarlo a otro router en la otra iteracion
				router = (router + 1) % len(self.__neighborsIDs)
				destination = (destination + 1) % len(self.__allNodesIDs)
			# aumenta contador: para intentar enviarlo a otro router en la otra iteracion
			router = (router + 1) % len(self.__neighborsIDs)
			destination = (destination + 1) % len(self.__allNodesIDs)



	def shutDown(self):
		printMsgTime(f"{TXT_RED}Testing{TXT_RESET} Shutting down dispatcher")
		# cierra conexiones
		for socket in self.__neighborsSockets:
			socket.close()

	# invoca al packager para dividir la operacion
	# retorna una lista con las partes de la operacion a repartir
	def operationsDivider(self, operation):
		return TempPackager.split(operation)

def main():
	operation = input("Recibe operacion: ")
	ds = Dispatcher()
	ds.operationsDivider(operation)

if __name__ == "__main__":
	main()