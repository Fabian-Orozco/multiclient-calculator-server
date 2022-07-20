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
    # operands as the appear in the http message
    self.operands = {"%2A":"*", "%2B":"+", "%28":"(", "%29":")", "%2F":"/", "%5E":"**"}

    # nammes of the files availables in our server
    self.htmlFiles = {"notFound":"notFound.html", "login":"login.html", "badRequest":"badRequest.html", "result":"result.html", "request":"request.html", "operationReadOnly":"readOnly.html"}

    # http error codes
    self.httpCodes = {"ok":"HTTP/1.0 200 OK\n\n", "badRequest":"HTTP/1.1 400 Bad request\n\n", "notFound":"HTTP/1.1 404 Not Found\n\n", "notLogin":"HTTP/1.1 401 Unauthorizedn\n\n"}


  # @brief method to detects if POST or GET or no http
  # @param httpRequest message received from the client
  # return string with the type of connection 
  def __detectHttpType(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    if (splitMessage != None and len(splitMessage) <= 1  or HTTP not in splitMessage[1].strip()):
      result = NOHTTP
    else:
      result = splitMessage[0].strip()
    return result

  # @brief method that detects the action requested in a GET htt message
  # @param httpRequest message received from the client
  # return action requested by the client
  def __getHttpRequest(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    htmlFile = splitMessage[1][0:splitMessage[1].find("HTTP")]
    htmlFile = htmlFile.strip()
    if (not htmlFile):
      # if empty action we send the home page / login page
      return "login"
    
    if (htmlFile[-1] == "?"):
      htmlFile = htmlFile[0:-1]
    return htmlFile

  # @brief method that detects the action requested in a POST htt message
  # @param httpRequest message received from the client
  # return action requested by the client
  def __postHttpRequest(self, httpRequest: str) -> str:
    splitMessage = httpRequest.split("/")
    action = splitMessage[1][0:splitMessage[1].find("HTTP")]
    action = action.strip()
    if (not action):
      # if empty action we return a error string
      return "error"
    
    if (action[-1] == "?"):
      action = action[0:-1]
    return action

  # @brief method that detects if it is a POST or GET and return the action
  # @param httpRequest message received from the client
  # return tuple with the type of message and the action to perform
  def handleHttpRequest(self, httpRequest : str) -> str:
    requestType = self.__detectHttpType(httpRequest)
    if (requestType == NOHTTP):
      # if no http message was detected we return an NOHTTP string
      return (NOHTTP, NOHTTP)

    # else we detect if it is post or get and return the action to perform

    if (requestType == "GET"):
      getRequest = self.__getHttpRequest(httpRequest)
      self.addTolog(httpRequest, getRequest)
      return (requestType, getRequest)

    if (requestType == "POST"):
      postRequest = self.__postHttpRequest(httpRequest)
      self.addTolog(httpRequest, postRequest)
      return (requestType, postRequest)


  # @brief method to open html files
  # @return the file or None if it doesn't exist
  def getHtmlFile(self, filename: str):
    try:
      file = open(PATH + filename)
      return file
    except:
      return None

  # @brief mehtod to genrate general html response messages
  # @param http error code
  # @param responseType indicates if it is a 400, 404 or 200 message type
  # @param message message to put in the html
  # @param title to put in the html file
  def generateResponse(self, code, responseType: str, message : str, title: str = None) -> str:
    response = ""
    if (responseType not in self.htmlFiles):
      # if we don't have the requested html
      response = self.httpCodes["notFound"]
      file = open(PATH + self.htmlFiles["notFound"])
      response += file.read()

      # replaces the message and title with error messages
      response = response.replace("!CustomTitle!", "Recurso no encontrado")
      response = response.replace("!CustomMessage!", f"No se econtro el siguiente recurso: {responseType}")
    else:

      response = self.httpCodes[code]
      # we load the indicated html file
      file = self.getHtmlFile(self.htmlFiles[responseType])
      response += file.read()

      # replaces the message and title section with the received strings
      if (title != None):
        response = response.replace("!CustomTitle!", title)
      response = response.replace("!CustomMessage!", message)

    return response

  # @brief extracts content of a http message
  # @param httpRequest message received from the client
  # @return string with the content
  def getContent(self, httpRequest : str) -> str:
    return self.parseText(httpRequest[httpRequest.rfind("\n"):])

  # @brief method to translate a http encoded text to normal text
  # @param text string to parse
  # @return the parsed text
  def parseText(self, text : str) -> str:
    checkOperands = list(self.operands.keys())
    for httpOperand in checkOperands:
      text = text.replace(httpOperand, self.operands[httpOperand])
    return text

  # @brief extracts a tuple from the cotent of the http message
  # @param content content with to http variables 
  # @return tuple woth two strings
  def getContentTuple(self, content : str) -> str:
    user = content[content.find("=")+1:content.find("&")]
    user = user.strip(" \n\t")
    password = content[content.rfind("=")+1:]
    password = password.strip(" \n\t")

    return (user, password)

  # @brief adds to a log file a http request
  # @param httpMessage message received from the client
  # @param contentType action to perfomr in the server (login, operation, etc)
  def addTolog(self, httpMessage : str, contentType : str):
    # generates string with date content, content length, content type and host
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

  # @brief extracts length of the content of a http message
  # @param httpRequest message received from the client
  # @return string with the length
  def __getLength(self, httpMessage : str) -> str:
    length = httpMessage[httpMessage.find("Content-Length:")+15: ]
    if (length):
      length = length[:length.find("\r\n")]
      if (not length):
        length = "0"
    length = length.strip()
    return length

  # @brief extracts the host of a http message
  # @param httpRequest message received from the client
  # @return string with the host who sent the http message
  def __getHost(self, httpMessage : str) -> str:
    host = httpMessage[httpMessage.find("Host:")+5: ]
    if (host):
      host = host[:host.find("\r\n")]
      host = host.strip()
    return host