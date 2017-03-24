from time import time
from network import *

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size']
	def __init__(self, prev_hash, threshold):
		self.previous_hash = prev_hash
		self.timestamp = time()
		self.target_threshold = threshold
	def Root(transactions):
		ids = [transaction.id for transaction in transactions]
		#calculate merkle root and return
		pass
	def Nonce():
		pass
	def __save__(self, transactions, block):
		self.merkle_root = Root(transactions)
		self.nonce = Nonce(block)
		self.size = getSize(block)

class Block(object):
	def __init__(self, threshold = 4):
		prev_block = getHead()
		self.header = BlockHeader(prev_block.hash,threshold)
		self.flags = 0x00
		self.transactions = []
		self.height = prev_block.height + 1
		self.difficulty = 0
		self.reward = 0

	def __save__(self):
		self.hash = Hash(self)
		self.difficulty = Difficulty(self.hash)

	def addTransaction(sender_id, receiver_id, amount):
		sender = network.getNode(sender_id)
		receiver = network.getNode(receiver_id)
		transaction = Transaction(sender_id, receiver_id, amount)

class Transaction(object):
	__slots__ = ['id', '']
	def __init__(self, sender_id, receiver_id, amount):
		chain = getChain()
		self.hash = Hash(sender_id, receiver_id, amount)
		chain.transactions.append(self.hash)
	pass

class indieChain(object):
	pass