from SimulatorTcp import SimulatorTcp
import socket

if(__name__ == '__main__'):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = '127.0.0.1'
    port = 8080
    addresInfo = [ip, port]
    serverSocket.bind((ip, port))
    communication = SimulatorTcp(serverSocket, ip, port)
    communication.printmsg(f"Binded socket to {addresInfo}")

    if (communication.listen(8081)):
        newSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        newIp = '127.0.0.1'
        newport = 8081
        newAddresInfo = (newIp, newport)
        newSocket.bind((newIp, newport))
        communication.setSocket(newSocket)
        message = communication.receiveTcpMessage()
        communication.sendTcpMessage("\"type\":\"Hola como esta\"")

