import network
from utils import *
from time import time

class Node(object):
	def __init__(self):
		self.id = network.getLocalId()
		self.nature = 'N'

	def addBlock(block):
		chain = dataStorage.getLocalChain()
		if 
		else:
			raise ValidityError("Invalid block")

	

class Miner(Node):
	def __init__(self):
		self.id = network.getLocalId()
		self.nature = 'M'

	def validateBlock(block):
		try:
			if block.flags == 0x11:
				for transaction in block.transactions:
					if verify(transaction):
						continue
				return True
		except TransactionError:
			return False

	@classmethod
	def verify(sender_address, receiver_addres, amount, chain):
		inputs = getInputs(chain, sender_address)
		sender_value = sum(inputs.value)
		if amount + fee <= sender_value:
			return True
		raise TransactionError("Invalid transaction(s)")

	@classmethod
	def getInputs(chain, address):
		return filter(lambda u: u.receiver=address, chain.transactions)