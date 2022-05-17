import ctypes

libPipe = ctypes.CDLL('./libPipe.so')

def creteChild():
    libPipe.createChild.restype = ctypes.c_int
    pid = libPipe.createChild()
    return pid

def closeWriteEnd():
    libPipe.closeWriteEnd.restype = ctypes.c_char_p
    libPipe.closeWriteEnd()

def closeReadEnd():
    libPipe.closeReadEnd.restype = ctypes.c_char_p
    libPipe.closeReadEnd()

def receiveMsg():
    libPipe.receiveMsg.restype = ctypes.c_char_p
    message = libPipe.receiveMsg()
    return message
    
def sendMsg(msg):
    libPipe.sendMsg.argtypes = (ctypes.c_char_p,)
    libPipe.sendMsg(msg.encode(encoding='UTF-8'))