
KEY_TO_FRAME = 1
CELDAS_EN_RAM = 4
class MMU:
    
    def __init__(self):
        self._pageTable = []
        self._pagedDisk = []
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
            #Verificar si esta en RAM si no:
                #Agregar varas de paginacion
            #else:
            frame = self._translate(page)
            for i in range(frame, (frame+4)):
                operation += (chr(self._ram[i]))
            operationPart += 1
            count += 1


    def _translate(self, page):
        return page[4] * 4
        
    def runPagination(self, page):
        
        
    def _getPage(self, operationPart, operationNUmber):
        for i in self._pageTable:
            if(i[0] == operationNUmber and i[2] == operationPart):
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
    #Agrega a la page table
    mmu._pageTable[0][4] = 0
    mmu._pageTable[1][4] = 1
    mmu._pageTable[2][4] = 2
    mmu._pageTable[3][4] = 3
    #Mete manualmente a la ram
    mmu.saveRAM(mmu._pagedDisk[0]["parts"][0],0)
    mmu.saveRAM(mmu._pagedDisk[0]["parts"][1], 4)
    mmu.saveRAM(mmu._pagedDisk[0]["parts"][2], 8)
    mmu.saveRAM(mmu._pagedDisk[0]["parts"][3], 12)
    print(mmu.getOperation(0))

