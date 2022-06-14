from MMU import MMU
from DiskManager import DiskManager
class Calculator:
    def __init__(self):
        self.saver = DiskManager()
        self.mmu = MMU()
        self.count = 0 
    
    def store(self, packet, operation, order):
        self.saver.addOperation(packet, operation, order)

    def calculate(self):
        operation = self.mmu.getOperation(self.count)

