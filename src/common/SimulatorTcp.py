from ipaddress import ip_address
import Communicator

class SimulatorTcp(Communicator):

	def __init__(self, socket, destination):
		super().__init__(self, socket) # construtor form parent class
		self._seqValue = 0              # sequence value
		self._ack = 0                   # acknoledgement value
		self._messagePackage = None     # string to accumulate message
		# sefl.timer =                  # timer for connections
		self._destination = destination # tuple with destination addres and port

	def listen(self, ):

	
