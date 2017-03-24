import network
import dataStorage
from utils import *
from time import time

class Node(object):
	__slots__ = ['id', 'role', 'chain']

	def __init__(self, chain):
		self.id = network.getNetworkId()
		self.role = 'N'
		self.chain = chain

	def createBlock(self, chain, threshold):
		assert(isinstance(chain, indieChain))
		block = Block(chain, threshold)
		return block

	def addBlock(self, block, chain):
		assert(isinstance(chain, indieChain))
		assert(isinstance(block, Block))
		chain.push(block)	

	def __repr__(self):
		return '<%s> %s' % (self.role, self.id)



class Miner(Node):
	__slots__ = ['id', 'role', 'chain']

	def __init__(self, chain):
		self.id = network.getNetworkId()
		self.role = 'M'
		self.chain = chain

	def getNodeSignature(self):
		pass

	def addBlock(block, chain):
		assert(isinstance(chain, indieChain))
		assert(isinstance(block, Block))
		if block.flags == 0x11 and reduce(lambda x, y: x and y, map(verifyTransaction, block.transactions)):
			assert(consesus(chain, block))
			block.miner = self
			block.signature = self.getNodeSignature()
			chain.push(block)
		else:
			raise TransactionError("Invalid transaction(s). Recheck Block.")
			
	@classmethod
	def verifyTransaction(transaction):
		inputs = getInputs(transaction.sender)
		sender_value = sum(inputs.value)
		return (amount + fee < sender_value)

	@classmethod
	def getInputs(address):
		chain = transaction.chain
		return filter(lambda u: u.receiver=address, chain.transactions)