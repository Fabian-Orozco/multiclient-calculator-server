from MMU import MMU
from DiskManager import DiskManager
class Calculator:
    def __init__(self):
        self.saver = DiskManager()
        self.mmu = MMU()
        self.count = 0 
    
    def store(self, packet, operation, order):
        self.saver.addOperation(packet, operation, order)
        
    def calculate(self,packet, operation, order):
        # Procesa el inicio y final de la operación.
        # Si tiene símbolos antes<prefijo> o después<posfijo>, los quita antes de procesar y los pone luego de procesar.
        symbols = ["+","*","-","/","^"]
        prefijo = ""
        posifjo = ""
        if (operation[0] in symbols):
            prefijo = operation[0]
            operation = operation[1::]
            # print ("modificado 1: " + operation)
        if (operation[len(operation)-1] in symbols):
            posifjo += operation[len(operation)-1]
            operation = operation[0:len(operation)-1:]
            # print ("modificado 2: " + operation)

        # Guarda la operación
        self.saver.addOperation(packet, operation, order)
        # Calcula la operación
        self.mmu.updatePagedDisk(self.saver.getElement(self.count)["operation"], self.count)
        # Recibe el resultado
        operation = self.mmu.getOperation(self.count)
        # Aumenta dirección virtual (índice de disco)
        self.count += 1

        if (operation == None):
            return None
        return prefijo + str(operation) + posifjo

if __name__ == "__main__":
    calc = Calculator()
    print(calc.calculate(1670,"-7+2-",0))
