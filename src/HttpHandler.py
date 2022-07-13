GET = "GET"
POST = "POST"
HTTP = "HTTP"
PATH = "html/"
class HttpHandler:

  def __init__(self):
    self.operands = {"*":"%2A", "+":"%2B", "(":"%28", ")":"%29", "/":"%2F"}
    self.htmlFiles = {"notFound":"notFound.html", "login":"login.html", "badRequest":"badRequest.html", "result":"result.html", "request":"request.html"}
    self.httpCodes = {"ok":"HTTP/1.0 200 OK\n\n", "badRequest":"HTTP/1.1 400 Bad request\n\n", "notFound":"HTTP/1.1 404 Not Found\n\n"}


  def __detectHttpType(self, httpRequest: str) -> str:
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

  def __getHttpRequest(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    htmlFile = splitMessage[1][0:splitMessage[1].find("HTTP")]
    htmlFile = htmlFile.strip()
    if (not htmlFile):
      return "login"
    
    if (htmlFile[-1] == "?"):
      htmlFile = htmlFile[0:-1]
    return htmlFile

  def __postHttpRequest(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    action = splitMessage[1][0:splitMessage[1].find("HTTP")]
    action = action.strip()
    if (not action):
      return "error"
    
    if (action[-1] == "?"):
      action = action[0:-1]
    return action

  def handleHttpRequest(self, httpRequest : str) -> str:
    requestType = self.__detectHttpType(httpRequest)
    if (requestType == "noHttp"):
      return ("noHttp", "noHttp")
    
    if (requestType == "GET"):
      return (requestType, self.__getHttpRequest(httpRequest))

    if (requestType == "POST"):
      return (requestType, self.__postHttpRequest(httpRequest))



  def getHtmlFile(self, filename: str):
    try:
      file = open(PATH + filename)
      return file
    except:
      return None

  def generateResponse(self, code, responseType: str, message : str, title: str = None) -> str:
    response = ""
    if (responseType not in self.htmlFiles):
      response = self.httpCodes["notFound"]
      file = open(PATH + self.htmlFiles["notFound"])
      response += file.read()
      response = response.replace("!CustomTitle!", "Recurso no encontrado")
      response = response.replace("!CustomMessage!", f"No se econtro el siguiente recurso: {responseType}")
    else:
      response = self.httpCodes[code]
      file = self.getHtmlFile(self.htmlFiles[responseType])
      response += file.read()
      if (title != None):
        response = response.replace("!CustomTitle!", title)
      response = response.replace("!CustomMessage!", message)

    return response

