from datetime import datetime
from Utilities import *

GET = "GET"
POST = "POST"
HTTP = "HTTP"
PATH = "html/"
NOHTTP = "noHTTP"
LOG_FILE = "bitacora/ServerLog.log"

class HttpHandler:

  def __init__(self):
    self.operands = {"%2A":"*", "%2B":"+", "%28":"(", "%29":")", "%2F":"/", "%5E":"**"}
    self.htmlFiles = {"notFound":"notFound.html", "login":"login.html", "badRequest":"badRequest.html", "result":"result.html", "request":"request.html", "operationReadOnly":"readOnly.html"}
    self.httpCodes = {"ok":"HTTP/1.0 200 OK\n\n", "badRequest":"HTTP/1.1 400 Bad request\n\n", "notFound":"HTTP/1.1 404 Not Found\n\n"}


  def __detectHttpType(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    if (splitMessage != None and len(splitMessage) <= 1  or HTTP not in splitMessage[1].strip()):
      result = NOHTTP
    else:
      result = splitMessage[0].strip()
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
    if (requestType == NOHTTP):
      return (NOHTTP, NOHTTP)
    if (requestType == "GET"):
      getRequest = self.__getHttpRequest(httpRequest)
      self.addTolog(httpRequest, getRequest)
      return (requestType, getRequest)

    if (requestType == "POST"):
      postRequest = self.__postHttpRequest(httpRequest)
      self.addTolog(httpRequest, postRequest)
      return (requestType, postRequest)



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

  def getContent(self, httpRequest : str) -> str:
    return self.parseText(httpRequest[httpRequest.rfind("\n"):])

  def parseText(self, text : str) -> str:
    checkOperands = list(self.operands.keys())
    for httpOperand in checkOperands:
      text = text.replace(httpOperand, self.operands[httpOperand])
    return text

  def getContentTuple(self, content : str) -> str:
    user = content[content.find("=")+1:content.find("&")]
    user = user.strip(" \n\t")
    password = content[content.rfind("=")+1:]
    password = password.strip(" \n\t")

    return (user, password)

  def addTolog(self, httpMessage : str, contentType : str):
    result = "Content type: " + self.__detectHttpType(httpMessage) + " " + contentType + ", "
    result += "Content length: " + self.__getLength(httpMessage) + ", "
    time = datetime.now().strftime('%x - %X') + ", "
    result += "Date: " + time + ", "
    result += "Host: " + self.__getHost(httpMessage) + ", "
    result += "Content: " + self.getContent(httpMessage).strip(" \n")

    try:
      file = open(LOG_FILE, "a")
      printMsgTime(f"{TXT_GREEN}Added to log:{TXT_RESET} {result}")
      result += "\n\n"
      file.write(result)
    except:
      printErrors(f"Could not open log file '{LOG_FILE}'")

  def __getLength(self, httpMessage : str) -> str:
    length = httpMessage[httpMessage.find("Content-Length:")+15: ]
    if (length):
      length = length[:length.find("\r\n")]
      if (not length):
        length = "0"
    length = length.strip()
    return length


  def __getHost(self, httpMessage : str) -> str:
    host = httpMessage[httpMessage.find("Host:")+5: ]
    if (host):
      host = host[:host.find("\r\n")]
      host = host.strip()
    return host