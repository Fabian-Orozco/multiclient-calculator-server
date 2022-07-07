from ctypes import addressof
from operator import truediv
import socket




def main():
  print("Hello world")
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(("127.0.0.1", 8080))

  sock.listen()
  newSock, address = sock.accept()
  file = open('./http/login.html')
  content = file.read()
  response = 'HTTP/1.0 200 OK\n\n' + content
  chunks = []
  if (newSock) :
    print(f"Connected to {address}")
    while (True):
      try:
        mss = newSock.recv(4096) # should receive request from client. (GET ....)
        print(f"received from: {address}: {mss}")
      except:
        pass
      if (not mss):
        break
      else:
        chunks.append(mss)
  
    newSock.send(response.encode("UTF-8"))
    print ("-----------------------------------------------------------------------------------")

    newSock.close()
  return 0

if __name__ == "__main__":
  main()