import common.Communicator
import socket

socketA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ipAddress = '127.0.0.1'
port = 8080
test = common.Communicator.Communicator(socketA)
test.sendMessage("hola", (ipAddress, port))