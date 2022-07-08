import socket

def main():
  print("Hello world")
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(("127.0.0.1", 8080))

  sock.listen()
  file = open('./html/request.html')
  content = file.read()
  okResponse = 'HTTP/1.0 200 OK\n\n'
  errorResponse = 'HTTP/1.1 404 Not Found\n\n'
  notParsedResponse =  'HTTP/1.1 400 Bad request\n\n'
  response = okResponse + content
  
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