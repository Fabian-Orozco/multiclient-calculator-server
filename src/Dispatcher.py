import ctypes
from Utilities import *
import queue
import socket


class Dispatcher:
	def __init__(self):
		self.x = 9

	def dispatch(self, message):
		# dispatcher just sends tne consumed messages of the queue to another server for now
		printMsgTime(f"{TXT_GREEN}Process B{TXT_RESET} will dispatch the next message: {message}")

			