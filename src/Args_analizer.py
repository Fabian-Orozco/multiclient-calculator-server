# UCR/ECCI/PI_redesOper Equipo 7 raspado.

## class Args_analizer
# class in charge of validating the arguments

import sys
from xmlrpc.client import TRANSPORT_ERROR

class Args_analizer:
	# Constructor
	def __init__(self):
		self.__validArguments = {'-u', '-p'} # to compare with the right of the flag
		self.__arguments = sys.argv[1:] # all arguments except the name of script
		self.__qtyArgs = len(self.__arguments)
		self.__indexU = self.__indexP = -1
		self.__user = self.__password = ""

####################################################################################

	## Print argument help: required arguments and their meaning.
	def printUsage(self):
		print(f'''\
usage: {sys.argv[0]} -u username -p password

required arguments:
  -u              flag before username
  "username"      username that will enter the server
  -p              flag before password 
  "password"      user password''')
	
####################################################################################

	def toString(self):
		print(f'''\nARGS INFO:\narray({self.__qtyArgs}): {self.__arguments} \
		\nindexU: {self.__indexU} | user: {self.__user}\
		\nindexP: {self.__indexP} | password: {self.__password}''')

####################################################################################

	# receives a string and looks for it in the array of arguments
	# returns the content if found, otherwise returns -1.
	def findArg(self, arg):
		return self.__arguments.index(arg) if arg in self.__arguments else -1

####################################################################################

	def loadIndexes(self):
		if (self.__qtyArgs < 4): #  fewer arguments than required
			print("ERROR: number invalid of arguments (must be at least 4)")
			return False
		else: # find the index of -u and -p
			self.__indexU = self.findArg('-u') # not guaranteed to find it
			self.__indexP = self.findArg('-p') # not guaranteed to find it
		return True

####################################################################################

	## find value of user and pass
	def findValue(self, arg, index):
		# assume: indexP + 1 or indexU + 1
		# we assume that the data is one position to the right
		temp = index + 1

		# if index is not -1 and is less than the total number of arguments and is NOT a flag (-u, -p)
		if (index != -1) \
			and (temp < self.__qtyArgs) \
			and (self.__arguments[temp] not in self.__validArguments):
			return self.__arguments[temp]
		else:
			print(f"ERROR: {arg} not found")
		return False

####################################################################################

	# Method in charge of invoking to load indexes and validating the content of the user and the password as existing strings
	def __validateArgs(self):
		result = False # assume
		if (self.loadIndexes()): # -u -p
			self.__user = self.findValue("user", self.__indexU)  # find the string that represents user
			self.__password = self.findValue("pass", self.__indexP)  # find the string that represents pass
		if (self.__user) and (self.__password): # both are valid (are strings and not flags)
			result = True
		return result

####################################################################################

	## Method in charge of invoking validating the arguments. If they are valid, returns True; on the contrary, return False.
	def analizeArgs(self):
		return self.__validateArgs()

####################################################################################

	## returns the string of username and password
	def getData(self):
		return [self.__user, self.__password]

# end class Args_analizer
####################################################################################

def main():
	print("\nStart...\n=================\n")

	reader = Args_analizer()

	if (reader.analizeArgs() == True):
		print(reader.getData())
		print("Arguments format are valid...")
	else:
		reader.printUsage()
		print("\nTry again later... close")
		print("\n=================\nFinish")

if __name__ == "__main__":
  	main()
		
####################################################################################
