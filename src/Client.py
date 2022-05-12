# UCR/ECCI/PI_redesOper Equipo 7 raspado.

from Utilities import *
from Args_analizer import Args_analizer
# from SimulatorTcp import SimulatorTcp
# from DataValidator import DataValidator


## class Client
# class in charge of handling the interaction with the user
class Client:

	## Constructor
	# initializes the attributes
	def __init__(self):
		self.__argsAnalizer = Args_analizer()
		# self.__comm = SimulatorTcp()
		# self.__validator = DataValidator()
		self.__username = ""
		self.__password = ""

####################################################################################

	## method that calls the class that analyzes arguments to analyze if their format is valid or not
	def __analizeArgs(self):
		if (self.__argsAnalizer.analizeArgs() == True):
			self.__username , self.__password = self.__argsAnalizer.getData()
			print(f"The format of the arguments {TXT_GREEN}is valid{TXT_RESET}")
		else:
			print(f"The format of the arguments {TXT_RED}is invalid{TXT_RESET}")
			self.__argsAnalizer.printUsage()
			self.close()
			
####################################################################################
	
	## method that handles the flow of client interaction: 
	def run(self):
		printMsgTime(f"{TXT_GREEN}|======: START :======|{TXT_RESET}")

		self.__analizeArgs()  # if arguments are invalid invokes to close.
		# chequea que sea un usuario registrado
		if(self.login() == False): # invoca a tcp
			self.close() 
		
		# enter 'q' to exit
		while True:
			input = self.showInterface()
			if input == 'q' : self.close()
			if input == '-h' : self.__argsAnalizer.printHelp()
		

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

	##
	#
	def validateData(self):
		## El atributo de tipo DataValidator se encarga de esto ......Agregar.......
		print("")

####################################################################################

	##
	#
	def login(self):
		# Invokes messageFormatter to format the string (user+password) ..Agregar..
		# Invokes Simulator_Tcp to send a message ........Agregar.........
		print("")

####################################################################################

	##
	#
	def receiveMessage(self):
		# Invokes Simulator_Tcp to receive a message ........Agregar.........
		print("")

####################################################################################

	def close(self):
		# Invokes Simulator_Tcp to close the connection ........Agregar.........
		printMsgTime(f"{TXT_RED}|======: FINISH :======|{TXT_RESET}")
		exit(0)

####################################################################################

# end Client class
####################################################################################

# test code. To run: python Client.py
def main():

	client = Client()
	client.run()

if __name__ == "__main__":
  	main()
####################################################################################