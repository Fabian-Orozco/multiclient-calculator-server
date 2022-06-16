from Utilities import *
from Operation import Package

class Packager:
    __VALID_SYMBOLS = {"(", ")","+", "-", "*", "/", "s", "^"}
    __ENDLINE = "x"      # Va al inicio de la pila, y en medio de cada operacion o numero enviado a los nodos

    ## retorna el tope de la pila sin sacarlo
    #
    #  @param pila la pila de la cual se quiere saber el tope
    #  @return el tope de la pila, si el tope es una funcion sqrt, solo retorna "s" para el manejo de la precedencia
    def __inspect(self, pila):
        if len(pila) >= 0:
            aux = pila.pop()
            pila.append(aux)
        if(aux[0] == "s"):
            return "s"
        else:
            return aux

    ## si el signo es un "-" se necesita saber si funciona como operador o como signo, si es como signo se debe mantener junto al numero
    #  Por ejemplo: si hay un "-5-5" se tiene que dividir como "-5 - 5"
    #
    #  @param index indice donde se encuentra el "-"
    #  @param string el string con la operacion
    #  @return si el "-" es un signo lo devuelve junto con el numero, si no solo devuelve el "-"
    def __checkMinus(self, index, string):

        # Operador: 5-5, ()-5, ()-()
        # Signo: -5, (-5), -()

        answer = string[index]

        # -5
        if ((index - 1) < 0):
            index += 1
            while string[index].isnumeric():
            #while string[index] in self.NUMBERS:        # recorre el string hasta que se termine el numero
                answer = answer + string[index]
                index += 1
            index -= 1
        # (-5)
        elif ((index - 1) >= 0):
            if (string[index - 1] == "("):
                index += 1
                while string[index].isnumeric():
                #while string[index] in self.NUMBERS:    # recorre el string hasta que se termine el numero
                    answer = answer + string[index]
                    index += 1
                index -= 1
        tupla = [answer, index]                         # Tupla que contiene el resultado y el indice donde debe seguir recorriendo la cadena

        return tupla
    
    ## funcion para insertar un espacio entre las partes de la operacion, entre los operandos y los operadores
    #  esto se realiza para poder identificar los numeros de los operadores a la hora de llamar al metodo que lo combierte a sufijo
    #
    #  @param string operacion a la que se le debe agregar espacios
    #  @return operacion con los espacios asignados
    def __insertSpaces(self, string):
        list = []
        index = 0
        while index < len(string):
            current = string[index]
            if(current.isnumeric()):                # Es un numero
                for j in range(index+1,len(string)):
                    if(string[j].isnumeric()):
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
                data = self.__checkMinus(index,string)
                current = data[0]
                index = data[1]
            list.append(current)
            index = index + 1

        return ' '.join(list)

    ## transforma la operacion infija entrante en una sufija
    #
    #  @param operation la operacion infija a transformar, los operandos y los numeros estan separados por espacios
    #  @return un string con la operacion sufija separada por espacios 
    def __infix_to_suffix(self, operation):
        precedence = {}         # Diccionario que asigna un valor de prioridad a un operador "s" es para la funcion sqrt
        precedence["^"] = 3
        precedence["*"] = 3
        precedence["/"] = 3
        precedence["+"] = 2
        precedence["-"] = 2
        precedence["("] = 1
        operatorStack = []      # Pila donde almacenamos los operadores
        suffixOperation = []    # Lista donde vamos almacenando la operacion sufija
        inputSpaced = self.__insertSpaces(operation)        # Inserta espacios entre caracteres
        print(f"Operacion: {operation}")   

        entries = inputSpaced.split() # Lista con las entradas de la operacion (operacion dividida)
        for entry in entries:
            if (((entry in self.__VALID_SYMBOLS) == False)):     # La entrada es un numero
                suffixOperation.append(entry)
            elif entry == "(":                                               # La entrada es un "(", lo agregamos al stack
                operatorStack.append(entry)
            elif entry == ")":                                                  # La entrada es un ")"
                tope = operatorStack.pop()
                while tope != "(":                      # Mientras lo que saquemos del operator stack no sea un "(" seguimos sacando
                    suffixOperation.append(tope)        # Lo agregamos a la respuesta
                    tope = operatorStack.pop()
            else:                                       # Es un operador
                while(len(operatorStack) != 0) and \
                    (precedence[self.__inspect(operatorStack)] >= precedence[entry]):  # Extraemos los operadores con igual o mayor precedencia, luego ingresamos el operador
                        suffixOperation.append(operatorStack.pop())
                operatorStack.append(entry)

        while len(operatorStack) != 0:                  # Enviamos los operadores faltantes en la pila
            suffixOperation.append(operatorStack.pop())

        return " ".join(suffixOperation)

    ## devuelve si la operacion es operable o si solo es un numero
    #  
    #  @param operation la operacion a evaluar
    #  @return True si el string es operable, False si no
    def __isOperable(self, operation):
        if ((operation[0] == "(") or operation.isnumeric()):
            return True
        else:
            return False

    ## divide la operacion entrante entre varias operaciones pequenas
    #  para realizarlo utiliza una pila que se encarga de, mediante varias reglas, dividir las operaciones aunque tengan dependencia
    #  
    #  @param suffix operacion de tipo sufija la cual sera la que se dividira
    #  @return lista de string con las operaciones pequenas
    def __split(self, operation):
        
        suffixOperation = self.__infix_to_suffix(operation)   # convierte la operacion a sufija con espacios

        operation = suffixOperation.split()                 # creo lista con las partes de la operacion
        length = len(operation)

        stack = []                # Pila para poder dividir la operacion
        stack.append(self.__ENDLINE)

        index = 0
        while index < length:       # recorro la operacion
            data = operation[index]
            if data.isnumeric() or data[0] == "s":  # si es numero o sqrt lo agrego a la pila
                stack.append(data)
            else:
                top = stack.pop()

                if top.isnumeric() or top[0] == "s":    # el tope es un numero
                    top2 = stack.pop()
                    if top2.isnumeric() or top2[0] == "s":  # el segundo tope es un numero
                        data = "(" + top2 + data + top + ")"
                        stack.append(data)
                        stack.append(self.__ENDLINE)
                    else:                                   # el segundo tope es un __ENDLINE
                        stack.append(top2)
                        data = data + top
                        stack.append(data)
                        stack.append(self.__ENDLINE)
                else:                                   # el tope es un __ENDLINE
                    stack.append(top)
                    iStack = len(stack) - 1

                    while ((self.__isOperable(stack[iStack]) == False) and (stack[iStack].isnumeric() == False)): # recorro hasta encontrar donde va el operador
                        iStack -= 1
                    
                    aux = stack[iStack]
                    stack.remove(aux)
                    data = data + aux
                    stack.insert(iStack,data)
            index += 1

        return stack


    def __package(self, listing, id):
        packages = []

        index = 0
        part = 0

        while index < len(listing):
            if listing[index] != "x":
                package = Package(listing[index], id, part)
                packages.append(package)
                part += 1
            index += 1

        return packages

    def run(self, operation, id):
        listing = self.__split(operation)
        print(f"Lista: {listing}")
        packages = self.__package(listing, id)

        return packages

## Funcion para correr el programa
def main():
    packager = Packager()

    while True:
        operation = input(" > ingrese la operación: ")
        if operation == "q": break

        packages = packager.run(operation, 1)

        for package in packages:
            print(package.operation)

## Para ejecutar python3 Packager.py
#  luego ingrese la operacion
if __name__ == "__main__":
    main()
