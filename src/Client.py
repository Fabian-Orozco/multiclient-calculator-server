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
			print(f"The format of the arguments {TXT_RED}is invalid{TXT_RESET}")
			self.__argsAnalizer.printUsage()
			self.__close()
			
####################################################################################
	
	## method that handles the flow of client interaction: 
	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: START :======|{TXT_RESET}")

		self.__analizeArgs()  # if arguments are invalid invokes to __close.
		# chequea que sea un usuario registrado

		self.__connect()  # invoca a tcp. Si no es válido, cierra el programa
		self.login()  # invoca a tcp. Si no es válido, cierra el programa

		# enter 'q' to exit
		while True:
			input = self.showInterface()
			if input == 'q' : self.__close()
			if input == '-h' : self.__argsAnalizer.printHelp()
			# self.__validateData(input)
			formatedMessage = self.__generateAction(input)
			# self.__msgFormatter.
			# self.__sendMessage(input)
		

####################################################################################

	## prints the base message to the user
	# @return the value entered by the user
	def showInterface(self):
		try:
			return input(f"{TXT_BLUE}>{TXT_RESET} Enter the action to perform: ")
		except KeyboardInterrupt as err:  # SIGINT (ctrl+c)
			print(f' \n{TXT_RED}Program finished by signal SIGINT{TXT_RESET}')

		except EOFError as err:  # EOF (ctrl+d)
			print(f' \n{TXT_RED}Program finished by signal EOF{TXT_RESET}')
		return 'q'
####################################################################################

	## prints the base message to the user
	# @return the value entered by the user
	def __checkInput(self, userInput):
		if ("-r" in userInput):
			return "read"
		elif ("-w" in userInput):
			return "write"
		else:
			return False

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
		action = self.__checkInput(userInput)
		userInput = userInput.strip()
		if (action == "read"):
			if (" " in userInput):
				userInput = (userInput[userInput.find(" "):]).strip()
				# Tcp se encarga de dividir. Se asumen "fin" como true
				return self.__msgFormatter.formatRequestRead("true", int(userInput))

			else: # solo está el "-r"
				# Tcp se encarga de dividir. Se asumen "fin" como true
				return self.__msgFormatter.formatRequestRead("true", -1)
				
		elif(action == "write"):
			print("WRITE")
		else:
			print("INVALID ACTION")



####################################################################################

	##
	#
	def __connect(self):
		if(self.__comm.connect() == False):
			self.__close()

####################################################################################

	##
	#
	def login(self):
		# Invokes messageFormatter to format the string (user+password) ..Agregar..
		message = self.__msgFormatter.formatLogin(self.__username, self.__password)
		self.__sendMessage(message)
		
		response = self.__receiveMessage()
		json_response = json.loads(response)

		validated = json_response['validated']

		if (validated == False):
			printErrors("User not validated")
			self.__close()
		
		printMsgTime(f"{TXT_GREEN}User validated.{TXT_RESET} Welcome {self.__username}\n")
		self.__canWrite = json_response['canWrite']
		return True
		

####################################################################################

	##
	#
	def __sendMessage(self, message):
		# Invokes Simulator_Tcp to send a message
		self.__comm.sendTcpMessage(message)

####################################################################################

	##
	#
	def __receiveMessage(self):
		# Invokes Simulator_Tcp to receive a message ........Agregar.........
		message = self.__comm.receiveTcpMessage()
		return message

####################################################################################

	def __close(self):
		# Invokes Simulator_Tcp to __close the connection ........Agregar.........
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