from Utilities import *

class Packager:
    VALID_SYMBOLS = {"(", ")","+", "-", "*", "/", "s", "^"}
    NUMBERS = {"1","2","3","4","5","6","7","8","9","0"}

    ## retorna el tope de la pila sin sacarlo
    #  @param pila la pila de la cual se quiere saber el tope
    #  @return el tope de la pila, si el tope es una funcion sqrt, solo retorna "s" para el manejo de la precedencia
    def inspect(self, pila):
        if len(pila) >= 0:
            aux = pila.pop()
            pila.append(aux)
        if(aux[0] == "s"):
            return "s"
        else:
            return aux

    ## transforma la operacion infija entrante en una sufija
    #  @param operation la operacion infija a transformar, los operandos y los numeros estan separados por espacios
    #  @return un string con la operacion sufija separada por espacios 
    def infix_to_suffix(self, operation):
        precedence = {}         # Diccionario que asigna un valor de prioridad a un operador "s" es para la funcion sqrt
        precedence["s"] = 4
        precedence["^"] = 3
        precedence["*"] = 3
        precedence["/"] = 3
        precedence["+"] = 2
        precedence["-"] = 2
        precedence["("] = 1
        operatorStack = []      # Pila donde almacenamos los operadores
        suffixOperation = []    # Lista donde vamos almacenando la operacion sufija
        entries = operation.split() # Lista con las entradas de la operacion (operacion dividida)
        for entry in entries:
            if (((entry in self.VALID_SYMBOLS) == False) and (entry[0] != "s")):     # La entrada es un numero
                suffixOperation.append(entry)
            elif entry == "(":                                                  # La entrada es un "(", lo agregamos al stack
                operatorStack.append(entry)
            elif entry == ")":                                                  # La entrada es un ")"
                tope = operatorStack.pop()
                while tope != "(":                      # Mientras lo que saquemos del operator stack no sea un "(" seguimos sacando
                    suffixOperation.append(tope)        # Lo agregamos a la respuesta
                    tope = operatorStack.pop()
            else:                                       # Es un operador
                if(entry[0] == "s"):
                    while(len(operatorStack) != 0) and (precedence[self.inspect(operatorStack)] >= precedence[entry[0]]): 
                        suffixOperation.append(operatorStack.pop())
                    operatorStack.append(entry)
                else:
                    while(len(operatorStack) != 0) and (precedence[self.inspect(operatorStack)] >= precedence[entry]):  # Extraemos los operadores con igual o mayor precedencia, luego ingresamos el operador
                        suffixOperation.append(operatorStack.pop())
                    operatorStack.append(entry)

        while len(operatorStack) != 0:                  # Enviamos los operadores faltantes en la pila
            suffixOperation.append(operatorStack.pop())
        
        return " ".join(suffixOperation)

    ## si el signo es un "-" se necesita saber si funciona como operador o como signo, si es como signo se debe mantener junto al numero
    #  Por ejemplo: si hay un "-5-5" se tiene que dividir como "-5 - 5"
    #
    #  @param index indice donde se encuentra el "-"
    #  @param string el string con la operacion
    #  @return si el "-" es un signo lo devuelve junto con el numero, si no solo devuelve el "-"
    def checkMinus(self, index, string):

        # Operador: 5-5, ()-5, ()-()
        # Signo: -5, (-5), -()

        answer = string[index]

        # -5
        if ((index - 1) < 0):
            index += 1
            while string[index] in self.NUMBERS:        # recorre el string hasta que se termine el numero
                answer = answer + string[index]
                index += 1
            index -= 1
        # (-5)
        elif ((index - 1) >= 0):
            if (string[index - 1] == "("):
                index += 1
                while string[index] in self.NUMBERS:    # recorre el string hasta que se termine el numero
                    answer = answer + string[index]
                    index += 1
                index -= 1
        tupla = [answer, index]                         # Tupla que contiene el resultado y el indice donde debe seguir recorriendo la cadena

        return tupla
    
    ## funcion para insertar un espacio entre las partes de la operacion, entre los operandos y los operadores
    #  esto se realiza para poder identificar los numeros de los operadores a la hora de llamar al metodo que lo combierte a sufijo
    #  @param string operacion a la que se le debe agregar espacios
    #  @return operacion con los espacios asignados
    def insertSpaces(self, string):
        list = []
        index = 0
        while index < len(string):
            current = string[index]
            if(current in self.NUMBERS):                # Es un numero
                for j in range(index+1,len(string)):
                    if(string[j] in self.NUMBERS):
                        current += string[j]
                        index = index + 1
                    else:
                        break
            elif current == "s":                        # Es la funcion sqrt
                index = index + 1
                while string[index] != ")":
                    current += string[index]
                    index = index + 1
                current+= string[index]
            elif current == "-":                        # Es un "-"
                data = self.checkMinus(index,string)
                current = data[0]
                index = data[1]
            list.append(current)
            index = index + 1

        return ' '.join(list)

## Funcion para correr el programa
def main():
    packager = Packager()

    while True:
        entry = input(" > ingrese la operación: ")
        if entry == "q": break
        inputSpaced = packager.insertSpaces(entry)        # Inserta espacios entre caracteres
        print(f"Antes: {entry}\nDespues:{inputSpaced}")   

        suffix = packager.infix_to_suffix(inputSpaced)        # Devuelve operacion sufija

        print(f"Operacion sufija: {suffix}")

## Para ejecutar python3 Packager.py
#  luego ingrese la operacion
if __name__ == "__main__":
    main()
