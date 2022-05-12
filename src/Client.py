# UCR/ECCI/PI_redesOper Equipo 7 raspado.

from colors import *
from Args_analizer import Args_analizer

from datetime import datetime

# import SimulatorTcp

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
		self.print_msg_time(f"{TXT_GREEN}|======: START :======|{TXT_RESET}")

		self.__analizeArgs()  # if arguments are invalid invokes to close.
		# chequea que sea un usuario registrado
		self.login()  # invoca a tcp
		
		# enter 'q' to exit
		while True:
			input = self.showInterface()
			if input == 'q' : self.close()
		

####################################################################################

	def showInterface(self):
		return input(f"{TXT_BLUE}>{TXT_RESET} Enter the action to perform: ")

####################################################################################

	def validateData(self):
		## El atributo de tipo DataValidator se encarga de esto
		print("")

####################################################################################

	def login(self):
		# Invokes messageFormatter to format the string (user+password)
		# Invokes Simulator_Tcp to send a message
		print("")

####################################################################################

	def receiveMessage(self):
		# Invoca a tcp para recibir un mensaje
		print("")

####################################################################################

	def close(self):
		# Invoca a tcp para cerrar la conexión
		self.print_msg_time(f"{TXT_RED}|======: FINISH :======|{TXT_RESET}")
		exit(0)

####################################################################################

	def print_msg_time(self, msg):
		''' Prints the current day and time + the message sent by parameter '''
		current_time = datetime.now().strftime('%x - %X')
		print (f'\n{TXT_BLUE}[{current_time}]{TXT_RESET} {msg}\n')

# end Client class
####################################################################################

# test code. To run: python Client.py
def main():

	client = Client()
	client.run()

if __name__ == "__main__":
  	main()
####################################################################################