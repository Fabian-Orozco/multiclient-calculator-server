from itertools import count


KEY_TO_FRAME = 1
CELDAS_EN_RAM = 4
class MMU:
    
    def __init__(self):
        self._pageTable = []
        self._pagedDisk = []
        self._pagesInRam = []
        self._ram = bytearray(16)
    
    def getFrame(self, index):
        return index + KEY_TO_FRAME
    
    def getHash(frame):
        return frame % CELDAS_EN_RAM

    def updatePagedDisk(self, diskOperation, index):
        pageFrames = []
        for char in range(0, len(diskOperation), 4):
            pageFrames.append(diskOperation[char:char+4])
        page = {"index":index,"operation":diskOperation,"qtypags":len(pageFrames),"parts" : pageFrames}
        self._pagedDisk.append(page)
    
    def addPage(self, pageFrames):
        for pag in range(pageFrames["qtypags"]):
            page = [pageFrames["index"], False, pag, False, -1]
            self._pageTable.append(page)
    
    def saveRAM(self, operation, frame):
        operation = bytes(operation, encoding="utf-8")
        char = 0
        for byt in range(frame, frame+4):
            if(char > len(operation)-1):
                break
            self._ram[byt] = operation[char]
            char += 1
        print(self._ram)

    def updatePageTable(self, operationNumber):
        pageFrames = self._pagedDisk[operationNumber]
        self.addPage(pageFrames)


    def getOperation(self, operationNumber):
        operationPart = 0
        operation = ""
        count = 0
        while(True):
            page  = self._getPage(operationPart, operationNumber)
            #Si la operacion no esta pagina se actualiza la pageTable para añadir las paginas correspondientes
            if(page == -1 and count == 0):
                self.updatePageTable(operationNumber)
                page  = self._getPage(operationPart, operationNumber)
            #Ya se encontraron todos los datos de la operacion
            elif(page == -1):
                return operation
            if(self._pageTable[page][3] == False):
                #Agregar varas de paginacion
                self.runPagination(page)

            frame = self._translate(page)
            for i in range(frame, (frame+4)):
                operation += (chr(self._ram[i]))
            operationPart += 1
            count += 1


    def _translate(self, page):
        return self._pageTable[page][4] * 4

      
    def runPagination(self, page):
    #Paginacion por espacio de trabajo
        while(True):
            pagedOperation = self._pagedDisk[self._pageTable[page][0]]
            if(len(self._pagesInRam) < 4):
                self._pageTable[page][3] = True
                self._pageTable[page][4] = len(self._pagesInRam)
                self._pagesInRam.append(page)
                operationPart = pagedOperation["parts"][self._pageTable[page][2]]
                self.saveRAM(operationPart, self._pageTable[page][4]*4)
                #Siguiente pagina de esa operacion a poner en Ram
                page = self._getPage(self._pageTable[page][2]+1, self._pageTable[page][0]) 
                if(page == -1):
                    return
  
            for i in self._pagesInRam:
                if(self._pageTable[i][1] == True and self._pageTable[i][3] == True):
                    self._pageTable[i][3] = False
                    self._pageTable[page][3] = True
                    self._pageTable[page][4] = self._pageTable[i][4]
                    #Se debe cargar a Ram los datos
                    operationPart = pagedOperation["parts"][self._pageTable[page][2]]
                    self.saveRAM(operationPart, self._pageTable[page][4]*4)
                    page = self._getPage(self._pageTable[page][2]+1, self._pageTable[page][0])
                    if(page == -1):
                        return
            return

 
    def _getPage(self, operationPart, operationNUmber):
        for i in range(len(self._pageTable)):
            if(self._pageTable[i][0] == operationNUmber and self._pageTable[i][2] == operationPart):
                return i
        return -1

if(__name__ == '__main__'):
    mmu = MMU()
    mmu.updatePagedDisk( "4+2+4+3+1+3+5+43",0)
    #mmu.addPage(mmu._pagedDisk[0])
    print(mmu._pagedDisk)
    print()
    print(mmu._pageTable)
    print(mmu.getOperation(0))


