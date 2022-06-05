# UCR/ECCI/PI_redesOper Equipo 7 raspado.

# from Utilities import *

class MessageFormatter:
## Class in charge of converting a data set into a message with json format

    ## meaning: set quotes.
    # return the string with " " arround
    # example: str: hello --> returns: "hello"
    def __sQts(self, str): 
        return f"\"{str}\""
    
    ## Convert two variables to a string with json format (key, value)
    # Example: key: seq , value: 2 => "seq":2
    # Optional: with comma or without comma
    # @param key string representing the key in a json format
    # @param value string representing the value in a json format
    # @param var_comma if it receives a comma "," it prints it; this is for all pairs except the last one.
    # @return string result with json format
    def jsonFormat(self, key, value, var_comma = ""):
        return self.__sQts(key) + ":" + f"{value}" + var_comma + ""

    ## Creates the necessary format for the login, agreed by all groups.
    # Example: {"seq":1,"type":"login","fin":true,"username":"u","password":"p"}
    # {"seq":13,"type":"login","fin":true,"username":"user","password":"pass","validated":true, "canWrite":true}
    # @param seq tcp message sequence number
    # @param username string representing the username of client
    # @param password username string representing the password of client
    # FROM SERVER:
    # @param validated STRING Optional is "true" if the user is in the database, "false" in otherwise
    # @param canWrite STRING Optional is "true" if the user can write, "false" in otherwise
    # @return string result with json format
    def formatLogin(self, username, password, validated = None, canWrite = None):
        format = "{"
        format += self.jsonFormat("type",       self.__sQts("login"),       ",")
        format += self.jsonFormat("username",   self.__sQts(username),      ",")
        
        if (validated != None and canWrite != None):
            format += self.jsonFormat("password",   self.__sQts(password),  ",")
            format += self.jsonFormat("validated",  validated,              ",")
            format += self.jsonFormat("canWrite",   canWrite)
        else:
            format += self.jsonFormat("password",   self.__sQts(password))

        format += "}"

        return format

    ## Creates the necessary format for writing request, agreed by all groups.
    # Example: 
    # {"seq":225,"type":"request","fin":true,"request":"write","operation":"2+4+5+8+5+7"}
    # {"seq":228,"type":"request","fin":true,"request":"write","result":31,"operation":"2+4+5+8+5+7"}
    # @param seq tcp message sequence number
    # @param fin tcp flag that indicates if is the end of message
    # @param operation represents the mathematical operation entered by the user
    # FROM SERVER:
    # @param Optional result represents the mathematical result of the operation [from server]
    # @return string result with json format
    def formatRequestWrite(self, operation, result = None):
        format = "{"
        format += self.jsonFormat("type", self.__sQts("request"), ",")
        format += self.jsonFormat("request", self.__sQts("write"), ",")

        if (result != None):
            format += self.jsonFormat("result", result, ",")
        format += self.jsonFormat("operation", self.__sQts(operation))
        format += "}"

        return format

    ## Creates the necessary format for read request, agreed by all groups.
    # Example: 
    # {"seq":226,"type":"request","fin":true,"request":"read","index":2}
    # {"seq":229,"type":"request","fin":true,"request":"read","index":"2","error":false,"result":31,"operation":"2+4+5+8+5+7"}
    # @param seq tcp message sequence number
    # @param fin tcp flag that indicates if is the end of message
    # @param index represents the position of the mathematical operation in the database
    # 
    # FROM SERVER:
    # @param error STRING Optional error  is true only if the index of the requested operation is out of range in the database[from server]
    # @param Optional result represents the mathematical result of the operation [from server]
    # @return string result with json format
    def formatRequestRead(self, index, error = None, result = None):
        format = "{"
        format += self.jsonFormat("type", self.__sQts("request"), ",")
        format += self.jsonFormat("request", self.__sQts("read"), ",")

        if (error != None and result != None):
            format += self.jsonFormat("index", index, ",")
            format += self.jsonFormat("error", error, ",")  # must be a string "true/false"
            format += self.jsonFormat("result", result)
        else:
            format += self.jsonFormat("index", index)

        format += "}"

        return format

    ## Creates the necessary format for the disconnection, agreed by all groups.
    # Example: {"seq":8,"type":"disconnect"} 
    # @param seq tcp message sequence number
    # @return string result with json format
    def formatDisconnect(self):
        format = "{"
        format += self.jsonFormat("type", self.__sQts("disconnect"))
        format += "}"

        return format

    ## Creates the necessary format for the error, agreed by all groups.
    # Example: {"seq":2,"type":"error","message":"example"}
    # @param seq tcp message sequence number
    # @param message error description 
    # @return string result with json format
    def formatError(self, message):
        format = "{"
        format += self.jsonFormat("type", self.__sQts("error"), ",")
        format += self.jsonFormat("message", self.__sQts(message))
        format += "}"

        return format

####################################################################################

# test code. To run: python MessageFormatter.py
def main():
    msg_f = MessageFormatter()
    print("\n")
    print("Login\n" + msg_f.formatLogin("user","pass") + "\n")
    print("Resp-Login\n" + msg_f.formatLogin("user","pass","true","true") + "\n")

    print("Req-Write\n" + msg_f.formatRequestWrite("1+2") + "\n")
    print("Req-Write[result]\n" + msg_f.formatRequestWrite("1+2",3) + "\n")

    print("Req-Read[index]\n" + msg_f.formatRequestRead(1) + "\n")
    print("Req-Read all\n" + msg_f.formatRequestRead(-1) + "\n")
    print("Resp-Read \n" + msg_f.formatRequestRead(2,"false",3) + "\n")
    print("Disconnect \n" + msg_f.formatDisconnect() + "\n")
    print("Error \n" + msg_f.formatError("mensaje de error") + "\n")

if __name__ == "__main__":
  	main()

####################################################################################
