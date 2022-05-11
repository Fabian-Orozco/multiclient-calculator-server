from SimulatorTcp import SimulatorTcp
import socket


if(__name__ == '__main__'):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.1'
    port = 8080
    addresInfo = [ip, port]
    communication = SimulatorTcp(serverSocket, ip, port)
    communication.connect()
    message = "\"type\":\"login\""
    communication.sendTcpMessage(message)
    message = communication.receiveTcpMessage()


