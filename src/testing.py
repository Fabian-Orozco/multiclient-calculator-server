from SimulatorTcp import SimulatorTcp
import socket
from Utilities import *
from MessageFormatter import MessageFormatter

if(__name__ == '__main__'):
    #====================================== client to server testing
    format = MessageFormatter()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.2'
    port = 8080
    addresInfo = [ip, port]
    communication = SimulatorTcp(serverSocket, ip, port)
    if (communication.connect()):
        #message = format.formatRequestWrite("true", "2+3+4+8+5+4+5+4+5+6+7+7+7+8+4+8+7+9+8+4+2+485464654654+23121#+46546543+54541646546546546546546516316546385463854654563456341563456341653463546463463463545634358459846546346874968463846843685436546546354684654+654+68546+4+684684854638476387441466543543543654635435435435435435435435435435435435435435435435435435434354")
        #printMsgTime(f"{TXT_YELLOW}Sending message is {TXT_RESET}" + message)
        message = format.formatRequestWrite("true", "2+3+4+8+354")
        printMsgTime(f"{TXT_YELLOW}Sending message is {TXT_RESET}" + message)

        #communication.sendTcpMessage(message)