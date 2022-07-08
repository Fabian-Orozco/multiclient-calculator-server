from audioop import add
from ctypes import addressof
from http import client
from operator import truediv
import socket




def main():
  print("Hello world")
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(("127.0.0.1", 8080))

  sock.listen()
  file = open('./http/login.html')
  content = file.read()
  response = 'HTTP/1.0 200 OK\n\n' + content
  
  while True:
    client, address = sock.accept()
    print(f"Connected to {address}")
    request = client.recv(1024).decode("UTF-8")
    print(f"Received form {address}: {request}")
  
    client.sendall(response.encode("UTF-8"))
    client.close()
  
  sock.close()

if __name__ == "__main__":
  main()