# UCR/ECCI/PI_redesOper Equipo 7 raspado.

## class Args_analizer
# class in charge of validating the arguments

from Utilities import *

import sys

class Args_analizer:

	## Constructor
	# initialize attributes
	def __init__(self):
		self.__validArguments = {'-u', '-p'} # to compare with the right of the flag
		self.__arguments = sys.argv[1:] # all arguments except the name of script
		self.__qtyArgs = len(self.__arguments)
		self.__indexU = self.__indexP = -1
		self.__user = self.__password = ""

####################################################################################
	## Print argument help: required arguments and their meaning.
	def printUsage(self):
		separator = f"{TXT_BLUE} | {TXT_RESET}"
		print(f'''\
____________________________________________________
usage: {TXT_BLUE}{sys.argv[0]} -u username -p password{TXT_RESET}

required arguments:
  {TXT_BLUE}-u{TXT_RESET}            flag before username
  {TXT_BLUE}username{TXT_RESET}      username that will enter the server
  {TXT_BLUE}-p{TXT_RESET}      	flag before password 
  {TXT_BLUE}password{TXT_RESET}      user password''')
		self.printHelp()
	
####################################################################################

	## Print argument help: required arguments and their meaning.
	def printHelp(self):
		separator = f"{TXT_BLUE} | {TXT_RESET}"
		print(f'''\
____________________________________________________
use flags for standard input:
  {TXT_BLUE}-r [index]{TXT_RESET}    read the indicated operation by index
  {TXT_BLUE}-r all{TXT_RESET}        read all operations on the database
  {TXT_BLUE}-w [2+2]{TXT_RESET}      write (calculate and store) operation

basic math operations:
{separator} + {separator} - {separator} * {separator} sqrt(a) {separator} a^b {separator}
____________________________________________________''')

####################################################################################

	## Testing method
	def toString(self):
		print(f'''\nARGS INFO:\narray({self.__qtyArgs}): {self.__arguments} \
		\nindexU: {self.__indexU} | user: {self.__user}\
		\nindexP: {self.__indexP} | password: {self.__password}''')

####################################################################################

	## Receives a string and looks for it in the array of arguments
	# @return the content if found, otherwise returns -1.
	def __findArg(self, arg):
		return self.__arguments.index(arg) if arg in self.__arguments else -1

####################################################################################

	## Checks the number of arguments and invokes the search for -u and -p
	# @return True if the number of arguments is acceptable, False otherwise.
	def __loadIndexes(self):
		if (self.__qtyArgs < 4): #  fewer arguments than required
			return False
		else: # find the index of -u and -p
			self.__indexU = self.__findArg('-u') # not guaranteed to find it
			self.__indexP = self.__findArg('-p') # not guaranteed to find it
		return True

####################################################################################

	## find value of user or pass
	# @param arg name of the key: username or password.
	# @param index that represents the position of '-u' or '-p' in the list.
	# @return If it is valid, it returns the string; otherwise it returns false.
	def __findValue(self, arg, index):
		# assume: indexP + 1 or indexU + 1
		# we assume that the data is one position to the right
		temp = index + 1

		# if index is not -1 and is less than the total number of arguments and is NOT a flag (-u, -p)
		if (index != -1) \
			and (temp < self.__qtyArgs) \
			and (self.__arguments[temp] not in self.__validArguments):
			return self.__arguments[temp]
		else:
			print(f"{TXT_RED}ERROR: {TXT_BLUE}{arg}{TXT_RESET} not found")
		return False

####################################################################################

	## Method in charge of invoking to load indexes and validating the content of the user and the password as existing strings.
	# @return True if the username and password string are acceptable, False in othercase.
	def __validateArgs(self):
		result = False # assume
		if (self.__loadIndexes()): # -u -p
			self.__user = self.__findValue("user", self.__indexU)  # find the string that represents user
			self.__password = self.__findValue("pass", self.__indexP)  # find the string that represents pass
		if (self.__user) and (self.__password): # both are valid (are strings and not flags)
			result = True
		return result

####################################################################################

	## Method in charge of invoking validating the arguments. 
	# @return If they are valid, returns True; on the contrary, return False.
	def analizeArgs(self):
		return self.__validateArgs()

####################################################################################

	## @return the string of username and password
	def getData(self):
		return [self.__user, self.__password]

# end class Args_analizer
####################################################################################

# test code. To run: python Args_analizer.py [args]

def main():
	print(f"\n{TXT_GREEN}Start...\n================={TXT_RESET}\n")

	args_analizer = Args_analizer()

	if (args_analizer.analizeArgs() == True):
		print(args_analizer.getData())
		print("Arguments format are valid...")
	else:
		args_analizer.printUsage()
		print("\nTry again later... close")
		print(f"\n{TXT_GREEN}=================\nFinish{TXT_RESET}")

if __name__ == "__main__":
  	main()
		
####################################################################################
