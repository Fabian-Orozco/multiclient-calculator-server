# UCR/ECCI/PI_redesOper Equipo 7 raspado.

## class Client
# class in charge of validating the arguments
from src.client.Args_analizer import Args_analizer


class Client:

	## Constructor
	# initializes the attributes
	def __init__(self):
		# self.__comm = SimulatorTcp()
		self.__username = ""
		self.__password = ""
		# self.__validator = DataValidator()
		self.__argsAnalizer = Args_analizer()
	
	def analizeArgs():
		
# end Client class

# test code. To run: python Client.py
def main():
	print(f"\n===start===")

	Client = Client()
	
	# enter 'q' to exit
	while True:
		username = input(f"\n> username: ")
		if username == 'q' : break
		password = input(f"> password: ")
		if password == 'q' : break
		print(f"{username} is {Client.checkLog(username, password)}")
		print(f"{username} can write: {Client.userCanWrite()}")

	print(f"\n===end===\n")

if __name__ == "__main__":
  	main()
