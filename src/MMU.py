from math import *
from Packager import Packager
from Operation import Package
KEY_TO_FRAME = 1
CELDAS_EN_RAM = 4

FRAME_SIZE = 8
VALID_SYMBOLS = {"+", "-", "*", "/", "^"}
names = {"sqrt":sqrt}

OPERATION = 0
REFERENCE = 1
COMPLETE = 2
GARVAGE = 3
OPERATION_PAGE = 4
PRESENT_BIT = 5
FRAME_RAM = 6

##Class MMU 
#Simulate the function of a MMU
class MMU:
    
    def __init__(self):
        #server attributes
        self._pageTable = [] #List for the Page Table
        self._pagedDisk = [] #List for the entries in Disk 
        self._pagesInRam = [] #List whit the pages in RAM
        self._ram = bytearray(32) #RAM memory of 32 bytes
        self._packager = Packager() #Packager to maintain order of the operations

    # @brief Update the Paged Disk with a new entrie
	# @details metod to determine the amount of pages of one operation
	# @param diskOperation string of one operation in the disk
	# @param index integer to represent the position os the operation on the disk
    def updatePagedDisk(self, diskOperation, index):
        pageFrames = [] #Represents the frames of the operation
        op  = self._packager.run(diskOperation, 0) #Divide the operation for the RAM
        for i in op:
            complete = True #Flag to know if the operation  in a frame is complete
            if(len(i.operation) > FRAME_SIZE):
                complete = False
            for char in range(0, len(i.operation), FRAME_SIZE):
                page = i.operation[char:char+FRAME_SIZE]
                #If is the last part of a incomplete operation put the comcplete flag in true to know the final
                if(len(page) < FRAME_SIZE):
                    pageFrames.append((page, True))
                else:
                    pageFrames.append((page, complete))
        #Create a dictionary for the operation and put it in pagedDisk
        entrie = {"index":index,"operation":diskOperation,"qtypags":len(pageFrames),"parts" : pageFrames}
        self._pagedDisk.append(entrie)

    # @brief add pages to the Page Table
	# @param pageFrames is an entrie of pagedDisk
    def addPages(self, pageFrames):
        # For every frame thad a operation need create a new page
        for pag in range(pageFrames["qtypags"]):
            complete = pageFrames["parts"][pag][1]
                #[Index, Reference, Complete, Garbage, OperationPage, PresentBit,FrameRam]
            page = [pageFrames["index"], False, complete, False, pag, False, -1]
            self._pageTable.append(page)
    
    # @brief Saves in RAM one operation
	# @param Operation string of the operation to put in a frame
    # @frame The frame where put the operation in bytes
    def saveRAM(self, operation, frame):
        operation = bytes(operation, encoding="utf-8")
        char = 0
        for byt in range(frame, frame+FRAME_SIZE):
            if(char > len(operation)-1):
                for i in range(byt, frame+FRAME_SIZE):
                    self._ram[i] = 0
                break
            self._ram[byt] = operation[char]
            char += 1
        #print(self._ram)

    # @brief update the page table whit the operation in the pagedDisk
	# @param operationNumber represents the position in pagedDisk
    # @frame The frame where put the operation in bytes
    def updatePageTable(self, operationNumber):
        pageFrames = self._pagedDisk[operationNumber]
        self.addPages(pageFrames)

    # @brief gets the result of an operation
    # @details metod to determines the amount of pages of one operation
	# @param operationNumber represents the requested operation
    def getOperation(self, operationNumber):
        operationPart = 0
        operation = ""
        count = 0
        while(True):
            #Gets the page to be use
            page  = self._getPage(operationPart, operationNumber)
            #If the operation page is not on the pageTable update the page table
            if(page == -1 and count == 0):
                self.updatePageTable(operationNumber)
                page  = self._getPage(operationPart, operationNumber)
            #return if no more operations
            elif(page == -1):
                operation = eval(operation.replace("^","**"), names)
                return operation
            #If page is not in RAM run the pagination
            if(self._pageTable[page][PRESENT_BIT] == False):
                err = self.runPagination(page, operation, False)
                if(err == -1):
                    return -1
                operation = ""
            #Translates to know the real position of the data in RAM
            frame = self._translate(page)
            #If the operation is complete or all parts are in RAM concatenate
            if(self._pageTable[page][COMPLETE] == True or 
            (self._pageTable[page][COMPLETE] == False and self.__arePartsInRam(page))):
                operation = self.concatenateRam(operation, frame)
                operationPart += 1
                #Put the reference and Garvage bits in True
                self._pageTable[page][REFERENCE] = True
                self._pageTable[page][GARVAGE] = True
            #If all part of an operation are not in RAM, page the parts
            else:
                err = self.runPagination(self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][0]),operation, True)
                if(err == -1):
                    return -1
                operation = ""
                #Concatenates the new parts in RAM
                frame = self._translate(page)
                operation = self.concatenateRam(operation, frame)
                operationPart += 1
                self._pageTable[page][REFERENCE] = True
                self._pageTable[page][GARVAGE] = True

            count += 1
    
    # @brief metod to translate the frame in the page to real position in RAM  
	# @param page represent the page to get the index in RAM
    def _translate(self, page):
        return self._pageTable[page][FRAME_RAM] * 8

    # @brief run the pagination
    # @details metod that run the pagination, if data is in RAM operate then an put in disk
        #The pagination will use working space
	# @param page is the page that will be paginated
    # @param operation is the operatio in ram to be evaluated
    # @param prevPag is bool to know if is necesarioa do page-1
    def runPagination(self, page, operation, prevPag):
        if(prevPag):
            page -= 1
        while(True):
            pagedOperation = self._pagedDisk[self._pageTable[page][OPERATION]]
            #If RAM is not full in use
            if(len(self._pagesInRam) < 4):
                #The present bit turn in True
                self._pageTable[page][PRESENT_BIT] = True
                #sets the Frame where the data will be
                self._pageTable[page][FRAME_RAM] = len(self._pagesInRam)
                self._pagesInRam.append(page)
                #Saves in RAM the data on Disk that the page represents
                operationPart = pagedOperation["parts"][self._pageTable[page][OPERATION_PAGE]]
                self.saveRAM(operationPart[0], self._pageTable[page][FRAME_RAM]*FRAME_SIZE)
                #Gets the next page to put on RAM
                page = self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][0]) 
                if(page == -1):
                    return

            #If RAM is in full use
            if(len(self._pagesInRam) == 4):
                for i in self._pagesInRam:
                    #Verifies if we can substitute the page in RAM
                    if(self._pageTable[i][REFERENCE] == True and self._pageTable[i][PRESENT_BIT] == True):
                        #if the garbage bit is in true save in the disk the data in RAM
                        if(self._pageTable[i][GARVAGE] == True and operation != ""):
                            self.saveInPagedDisk(operation, page)
                            operation = ""
                        #Puts the Present bit in the old page in False
                        self._pageTable[i][PRESENT_BIT] = False
                        #Bit of new page in True
                        self._pageTable[page][PRESENT_BIT] = True
                        #set the frame of the new page
                        self._pageTable[page][FRAME_RAM] = self._pageTable[i][FRAME_RAM]
                        #Update the data in ram whit the data of the new page
                        operationPart = pagedOperation["parts"][self._pageTable[page][OPERATION_PAGE]]
                        self.saveRAM(operationPart[0], self._pageTable[page][FRAME_RAM]*FRAME_SIZE)
                        self._pagesInRam[self._pageTable[page][FRAME_RAM]] = page
                        #Gets the next page
                        page = self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][OPERATION])
                        if(page == -1):
                            return
                        if(page in self._pagesInRam):
                            page += 1

                return

    # @brief save a new data in paged disk(disk)
    # @details metod to calculate the operation in RAM and save the result in Disk
	# @param operation is the opereation to calculate
    # @param page is the page that will be put in RAM
    def saveInPagedDisk(self, operation, page):
        prefix = operation[0]
        #evaluates the operatios
        if(prefix in VALID_SYMBOLS):
            operation = prefix + str(round(eval(operation.replace("^","**"), names),2))
            if(len(operation) > FRAME_SIZE*3):
                return -1
        else:
            operation = str(round(eval(operation.replace("^","**"), names),2))
            if(len(operation) > FRAME_SIZE*3):
                return -1
        complete = True
        if(len(operation) > FRAME_SIZE):
            complete = False
        #Put the parts of the operation in Disk
        for char in range(0, len(operation), FRAME_SIZE):
            op = operation[char:char+FRAME_SIZE]
            if(len(op) < FRAME_SIZE):
                complete = True
            self._pagedDisk[self._pageTable[page][OPERATION]]["parts"].insert(self._pageTable[page][OPERATION_PAGE],(op, complete))
            newPage = [self._pageTable[page][OPERATION], False, complete, False,self._pageTable[page][OPERATION_PAGE], False, -1]
            #Modifies the page table for the new data
            self.__incrementOperationParts(page)
            self._pagedDisk[self._pageTable[page][OPERATION]]["qtypags"] += 1
            self._pageTable.insert(page,newPage)
            if(page in self._pagesInRam):
                self._pagesInRam[self._pagesInRam.index(page)] += 1
            page += 1
            
    # @brief gets the index of a page in the PageTable
    # @param operationPart represents the part of the that page represents for the operationNumber
	# @param operationNumber represents the requested operation
    def _getPage(self, operationPart, operationNUmber):
        for i in range(len(self._pageTable)):
            if(self._pageTable[i][OPERATION] == operationNUmber and 
            self._pageTable[i][OPERATION_PAGE] == operationPart):
                return i
        return -1

    # @brief Concatenates the data in one ram frame
    # @param operation is the actual data concatenated
	# @param frame is the frame to be concatenated to operation
    def concatenateRam(self, operation, frame):
        for i in range(frame, (frame+FRAME_SIZE)):
                    if(self._ram[i] != 0):
                        operation += (chr(self._ram[i]))
        return operation
    

    # @brief increment the operationParts in page table
    # @param page from wich it will be increased
    def __incrementOperationParts(self, page):
        self._pageTable[page][OPERATION_PAGE] += 1
        while(True): 
            if(page + 1 < len(self._pageTable)):
                if(self._pageTable[page+1][OPERATION] == self._pageTable[page][OPERATION]):
                    self._pageTable[page+1][OPERATION_PAGE] += 1
                    page += 1
                else:
                    return
            else:
                return


    # @brief Determine if all parts of the data are in RAM
    # @param page is the page to be evaluated if al parts are RAM

    def __arePartsInRam(self, page):
        page = self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][OPERATION])
        while(page != -1):
            if(page in self._pagesInRam and self._pageTable[page][COMPLETE]):
                return True
            else:
                page = self._getPage(self._pageTable[page][OPERATION_PAGE]+1, self._pageTable[page][OPERATION])
        return False
                



        
if(__name__ == '__main__'):
    mmu = MMU()
    mmu.updatePagedDisk("sqrt(25)+(2+3)*2+4^10+2+123313123",0)
    mmu.updatePagedDisk("+23+3241*2+4^10-5000",1)
    mmu.updatePagedDisk("23+1-10+5+2*2",2)
    mmu.updatePagedDisk("3231231212134312321234-121323",3) 
    #mmu.updatePagedDisk("2+3+",3)
    #mmu.addPage(mmu._pagedDisk[0])
    #print(mmu._pagedDisk)
    #print()
    #print(mmu._pageTable)
    print(mmu.getOperation(0))
    print(mmu.getOperation(1))
    print(mmu.getOperation(2))
    print(mmu.getOperation(3))
    


