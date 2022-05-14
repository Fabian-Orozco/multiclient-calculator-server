import ctypes

# Cargamos la libreria 
libPipe = ctypes.CDLL('./src/server/libPipe.so')

# Definimos los tipos de los argumentos de la función factorial
libPipe.sendMsg.argtypes = (ctypes.c_char_p,)

# Definimos el tipo del retorno de la función factorial
libPipe.sendMsg.restype = ctypes.c_char_p

libPipe.sendMsg.argtypes = (ctypes.c_char_p,)




def send():
    msg = b"casa"

    msg = libPipe.sendMsg(msg)
    
    if(msg != b"papa"):
        print(msg)
        
        
        
    else:
        print("SOy el papi")
        exit(0)

    



send()