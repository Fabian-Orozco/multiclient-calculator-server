class DiskManager:

    def __init__(self):
        self.disk = []
    
    def getElement(self, index):
        return self.disk[index]
    
    def addOperation(self, packet, operation, order):
        operationObject = {"packet": packet, "operation": operation, "order": order}
        self.disk.append(operationObject)