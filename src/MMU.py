
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
            self._ram[byt] = operation[char]
            char += 1
        print(self._ram)


    #def _translate(self, page):
        
    #def _getOperation(self, operationNumber):
        
    #def _getPage(self, operationPart):

if(__name__ == '__main__'):
    mmu = MMU()
    mmu.saveRAM("4+33",4)