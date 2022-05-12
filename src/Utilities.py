from datetime import datetime

#######################################################################

TXT_RESET = '\033[0m'
TXT_BLUE = '\033[34m'
TXT_RED = '\033[31m'
TXT_GREEN = '\033[32m'
TXT_YELLOW = '\033[33m'



#######################################################################

## Prints the current day and time + the message sent by parameter
# @param msg is the string to print
def printMsgTime(msg):
    time = datetime.now().strftime('%x - %X')
    print (f'{TXT_BLUE}[{time}]{TXT_RESET} {msg}')

def printErrors(msg):
    printMsgTime(f"{TXT_RED}ERROR: {TXT_RESET}{msg}")
