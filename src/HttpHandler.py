GET = "GET"
POST = "POST"
HTTP = "HTTP"

class HttpHandler:

  def __init__(self):
    self.operands = {"*":"%2A", "+":"%2B", "(":"%28", ")":"%29", "/":"%2F"}
    self.htmlFiles = {"404":"./html/error404.html", "login":"./html/login.html", "400":"./html/error400.html", "result":"./html/result.html", "request":"./html/request.html"}
    self.httpCodes = {"200":"HTTP/1.0 200 OK\n\n", "400":"HTTP/1.1 400 Bad request\n\n", "400":"HTTP/1.1 404 Not Found\n\n"}


  def detectHttpType(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    print("tamanyo del split: ", len(splitMessage))
    if (len(splitMessage) <= 1 or HTTP not in splitMessage[1].strip()):
      result = "noHTTP"
    else:
      if (GET in splitMessage[0].strip()):
        result = GET
      elif (POST in splitMessage[0].strip()):
        result = POST
    return result

  def getHttpRequest(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    htmlFile = splitMessage[1][0:splitMessage[1].find("HTTP")]
    htmlFile = htmlFile.strip()
    if (htmlFile[-1] == "?"):
      htmlFile = htmlFile[0:-1]
    return htmlFile
