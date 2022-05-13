# UCR/ECCI/PI_redesOper Equipo 7 raspado.

import json

route = "./json/users.json"

## class Authenticator
# class in charge of validating the entered username and password; in addition to verifying the permissions that it has, comparing through the file of valid users.
class Authenticator:

	## Constructor
	# initializes the attribute that contains the data in json file
	def __init__(self):
		with open(route) as file:
			self.__usersJson = json.load(file)  # list of the data in json file
		self.__actualUser = None  # user that will be verified

	## Compares the values given by parameter with the values of the json object
	# @param username represents the key of the json object
	# @param password represents the key of the json object
	# return boolean True if the user is in the json object, otherwise returns False
	def checkLog(self, username, password):
		for user in self.__usersJson['users']:
			if user["username"] == username and user["password"] == password:
				self.__actualUser = user
				return True
			else:
				self.__actualUser = None
		return False
	
	## Check if a user has write permissions
	# return boolean true if the user has write permissions, otherwise returns False
	def userCanWrite(self):
		try:
			return self.__actualUser["canWrite"]
		except:
			return False

# end Authenticator class

# test code. To run: python Authenticator.py
def main():
	print(f"\n===start===")

	authenticator = Authenticator()
	
	# enter 'q' to exit
	while True:
		username = input(f"\n> username: ")
		if username == 'q' : break
		password = input(f"> password: ")
		if password == 'q' : break
		print(f"{username} is {authenticator.checkLog(username, password)}")
		print(f"{username} can write: {authenticator.userCanWrite()}")

	print(f"\n===end===\n")

if __name__ == "__main__":
  	main()
