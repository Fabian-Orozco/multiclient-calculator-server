from posixpath import split
import socket

from HttpHandler import HttpHandler

def main():
  httpHand = HttpHandler()
  print("Server up")
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(("127.0.0.1", 8080))

  sock.listen()
  okResponse = 'HTTP/1.0 200 OK\n\n'
  errorResponse = 'HTTP/1.1 404 Not Found\n\n'
  notParsedResponse =  'HTTP/1.1 400 Bad request\n\n'
  content = ""
  while True:
    client, address = sock.accept()
    print(f"Connected to {address}")
    request = client.recv(1024).decode("UTF-8")
    print(f"Received form {address}:\n[ {request} ]")
    requestType = httpHand.detectHttpType(request)
    print(f"\nDetected type is:  {requestType}")
    if (requestType != "noHTTP"):
      print(f"\HTML request is:  {httpHand.getHttpRequest(request)}")

    if ("/login" in request):
      file = open('./html/result.html')
      content = file.read()
      response = okResponse + content
      file.close()
    else:
      file = open('./html/login.html')
      content = file.read()
      response = okResponse + content
      file.close()
    client.sendall(response.encode("UTF-8"))
    client.close()
  
  sock.close()

if __name__ == "__main__":
  main()