# UCR/ECCI/PI_redesOper Equipo 7 raspado.

from Utilities import *
from Args_analizer import Args_analizer
from SimulatorTcp import SimulatorTcp
# from DataValidator import DataValidator
from MessageFormatter import MessageFormatter
import json
import socket
	

## class Client
# class in charge of handling the interaction with the user
class Client:

	## Constructor
	# initializes the attributes
	def __init__(self, port, host):
		self.__argsAnalizer = Args_analizer()
		self.__comm = SimulatorTcp(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), port, host)
		# self.__validator = DataValidator()
		self.__msgFormatter = MessageFormatter()
		self.__username = ""
		self.__password = ""
		self.__canWrite = False
	
####################################################################################

	## method that calls the class that analyzes arguments to analyze if their format is valid or not
	def __analizeArgs(self):
		if (self.__argsAnalizer.analizeArgs() == True):
			self.__username , self.__password = self.__argsAnalizer.getData()
			print(f"The format of the arguments {TXT_GREEN}is valid{TXT_RESET}")
		else:
			self.__argsAnalizer.printUsage()
			self.__close(f"The format of the arguments {TXT_RED}is invalid{TXT_RESET}")
			
####################################################################################
	
	## method that handles the flow of client interaction: 
	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: START :======|{TXT_RESET}")  # header

		self.__analizeArgs()  # if arguments are invalid invokes to __close.

		# handshake and login
		self.__connect()  # Invokes to tcp. If invalid, close program
		self.login()  # Invokes to  tcp. If invalid, close program
		
		while True:
			input = self.showInterface()
			
			if (input == 'q') :
				break;
			elif (input == '-h') : 
				self.__argsAnalizer.printHelp()
			else:
				# self.__validateData(input)
				formatedMessage = self.__generateAction(input)
				if (formatedMessage != None): 
					print("testing_Mensaje formado para enviar:\n" + formatedMessage + "\n")
					self.__sendMessage(formatedMessage)
					# serverResponse = self.__receiveMessage(formatedMessage)
					# self.__verifyServerResponse()
				else:
					printErrors(f"Invalid input. Try again...")
		self.__disconnect()
		self.__close(f"Program {TXT_BLUE}finished{TXT_RESET} with 'q'")  # enter 'q' to exit
####################################################################################

	## 
	# 
	def __verifyServerResponse(self, serverResponse):
		# posibles llegadas: write/read with result , error [etapa 3], 
		# {"seq”:228,"type":"request","fin":true,"request":"write","result":31,"operation":"2+4+5+8+5+7"}   6
		# error solo si el indice está fuera del rango
		# {"seq”:229,"type":"request","fin":true,"request":"read","index":"2",”error”:false,”result”:31,”operation”:"1+1+1+1+1+1+1+1+1+1"}

		json_response = json.loads(serverResponse)
		request = json_response["request"]
		if (request == "read"):
			print("")
		elif(request == "write"):
			print("")
		

####################################################################################

	## prints the base message to the user
	# @return the value entered by the user
	def showInterface(self):
		try:
			return input(f"{TXT_BLUE}>{TXT_RESET} Enter the action to perform: ")
		except KeyboardInterrupt as err:  # SIGINT (ctrl+c)
			self.__disconnect()
			self.__close(f'Program finished by {TXT_RED}signal SIGINT{TXT_RESET}')

		except EOFError as err:  # EOF (ctrl+d)
			self.__disconnect()
			self.__close(f'Program finished by {TXT_RED}signal EOF{TXT_RESET}')
		return 'q'

####################################################################################

	##
	#
	def __validateData(self, userInput):
		## El atributo de tipo DataValidator se encarga de esto ......Agregar.......
		print("")
####################################################################################

	##
	#
	def __generateAction(self, userInput):
		userInput = userInput.strip()  	#remove blank space around
		content = (userInput[userInput.find(" "):]).strip() # action [content]

		if (userInput == "-r"):  # read [] => all
				# Tcp se encarga de dividir. Se asumen "fin" como true
				return self.__msgFormatter.formatRequestRead("true", -1) 	# -r
		
		elif ("-r" in userInput):  		# read action
			if (" " in userInput):		# read + index
				# Tcp se encarga de dividir. Se asumen "fin" como true
				return self.__msgFormatter.formatRequestRead("true", int(content))

		elif("-w" in userInput):
			if (" " in userInput):
				return self.__msgFormatter.formatRequestWrite("true",content)
		
		return None

####################################################################################

	##
	#
	def __connect(self):
		if(self.__comm.connect() == False):
			self.__close(f"{TXT_RED}Disconnected from server{TXT_RESET}")

	def __disconnect(self):
		disconnectMessage = self.__msgFormatter.formatDisconnect()
		self.__comm.sendTcpMessage(disconnectMessage)
		self.__close(f"{TXT_RED}Disconnected from server{TXT_RESET}")
	
####################################################################################

	##
	#
	def login(self):
		# Invokes messageFormatter to format the string (user+password) ..Agregar..
		message = self.__msgFormatter.formatLogin(self.__username, self.__password)
		printMsgTime(f"{TXT_YELLOW}Logging in as{TXT_RESET}: {self.__username}")
		self.__sendMessage(message)
		
		response = self.__receiveMessage()
		json_response = json.loads(response)

		validated = json_response['validated']

		if (validated == False):
			self.__close(f"Program finished: {TXT_RED}user is invalid{TXT_RESET}")
		
		printMsgTime(f"{TXT_GREEN}User validated.{TXT_RESET} Welcome {self.__username}\n")
		self.__canWrite = json_response['canWrite']
		return True
		

####################################################################################

	##
	#
	def __sendMessage(self, message):
		# Invokes Simulator_Tcp to send a message
		if (self.__comm.sendTcpMessage(message) == False):
			printErrors(f"{TXT_RED}Server did not respond.{TXT_RESET}")
			self.__close(f"{TXT_RED}Disconnected from server{TXT_RESET}")

####################################################################################

	##
	#
	def __receiveMessage(self):
		# Invokes Simulator_Tcp to receive a message ........Agregar.........
		message = self.__comm.receiveTcpMessage()
		return message

####################################################################################

	def __close(self, msg = ""):
		# Invokes Simulator_Tcp to __close the connection ........Agregar.........
		if (msg): printMsgTime(f"{msg}")
		printMsgTime(f"{TXT_RED}|======: FINISH :======|{TXT_RESET}")
		exit(0)

####################################################################################

# end Client class
####################################################################################

# test code. To run: python Client.py
def main():

	client = Client('127.0.0.2', 8080)
	client.run()

if __name__ == "__main__":
  	main()
####################################################################################