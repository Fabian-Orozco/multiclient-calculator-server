KEY_TO_FRAME = 1
CELDAS_EN_RAM = 4

FRAME_SIZE = 8


OPERATION = 0
REFERENCE = 1
OPERATION_PAGE = 2
PRESENT_BIT = 3
FRAME_RAM = 4
class MMU:
    
    def __init__(self):
        self._pageTable = []
        self._pagedDisk = []
        self._pagesInRam = []
        self._ram = bytearray(32)
    
    def getFrame(self, index):
        return index + KEY_TO_FRAME
    
    def getHash(frame):
        return frame % CELDAS_EN_RAM

    def updatePagedDisk(self, diskOperation, index):
        pageFrames = []
        for char in range(0, len(diskOperation), FRAME_SIZE):
            pageFrames.append(diskOperation[char:char+FRAME_SIZE])
        page = {"index":index,"operation":diskOperation,"qtypags":len(pageFrames),"parts" : pageFrames}
        self._pagedDisk.append(page)
    
    def addPage(self, pageFrames):
        for pag in range(pageFrames["qtypags"]):
            page = [pageFrames["index"], False, pag, False, -1]
            self._pageTable.append(page)
    
    def saveRAM(self, operation, frame):
        operation = bytes(operation, encoding="utf-8")
        char = 0
        for byt in range(frame, frame+FRAME_SIZE):
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
            #Si la pagina no esta en RAM se debe paginar
            if(self._pageTable[page][PRESENT_BIT] == False):
                #Agregar varas de paginacion
                self.runPagination(page)
            #Se hace la traduccion
            frame = self._translate(page)
            #Se extrae el fragmento de la RAM
            for i in range(frame, (frame+FRAME_SIZE)):
                operation += (chr(self._ram[i]))
            operationPart += 1
            count += 1
            self._pageTable[page][REFERENCE] = 1
            
    def _translate(self, page):
        return self._pageTable[page][4] * 8

      
    def runPagination(self, page):
    #Paginacion por espacio de trabajo
        while(True):
            pagedOperation = self._pagedDisk[self._pageTable[page][OPERATION]]
            #En caso de que la RAM no este llena
            if(len(self._pagesInRam) < 4):
                #Se pone en True el bit de presente/ausente
                self._pageTable[page][PRESENT_BIT] = True
                #Se indica el marco de pagina donde se encuentra el dato
                self._pageTable[page][FRAME_RAM] = len(self._pagesInRam)
                self._pagesInRam.append(page)
                #Se saca de las operaciones paginadas el dato respectivo que representa la pagina
                operationPart = pagedOperation["parts"][self._pageTable[page][OPERATION_PAGE]]
                self.saveRAM(operationPart, self._pageTable[page][FRAME_RAM]*FRAME_SIZE)
                #Siguiente pagina de esa operacion a poner en Ram
                page = self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][0]) 
                if(page == -1):
                    return

            #Cuando la RAM esta llena y se deben sustituir paginas en RAM
            for i in self._pagesInRam:
                #Se verifica si la pagina se puede sustituir
                if(self._pageTable[i][REFERENCE] == True and self._pageTable[i][3] == True):
                    #Se pone el bit de presente/ausente de la pagina a susutituir en False
                    self._pageTable[i][PRESENT_BIT] = False
                    #Se pone el bit de la pagina a cargar en RAM en True
                    self._pageTable[page][PRESENT_BIT] = True
                    #Se define el Frame al que apunta la pagina nueva a poner en RAM
                    self._pageTable[page][FRAME_RAM] = self._pageTable[i][FRAME_RAM]
                    #Se debe cargar a Ram los datos
                    operationPart = pagedOperation["parts"][self._pageTable[page][OPERATION_PAGE]]
                    self.saveRAM(operationPart, self._pageTable[page][FRAME_RAM]*FRAME_SIZE)
                    page = self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][OPERATION])
                    if(page == -1):
                        return
            

 
    def _getPage(self, operationPart, operationNUmber):
        for i in range(len(self._pageTable)):
            if(self._pageTable[i][OPERATION] == operationNUmber and 
            self._pageTable[i][OPERATION_PAGE] == operationPart):
                return i
        return -1

if(__name__ == '__main__'):
    mmu = MMU()
    mmu.updatePagedDisk("4+2+3+4+3+43+3+3+45",0)
    mmu.updatePagedDisk("2+3",1)
    #mmu.updatePagedDisk("2+4",1)
    #mmu.updatePagedDisk("3+22",2)
    #mmu.updatePagedDisk("2+3+",3)
    #mmu.addPage(mmu._pagedDisk[0])
    print(mmu._pagedDisk)
    print()
    print(mmu._pageTable)
    print(mmu.getOperation(0))
    print(mmu.getOperation(1))
    #print(mmu.getOperation(2))
    #print(mmu.getOperation(3))


