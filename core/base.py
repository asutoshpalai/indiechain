from time import time
import network

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size']
	
	def __init__(self, prev_hash, threshold):
		self.previous_hash = prev_hash
		self.timestamp = time()
		self.target_threshold = threshold
	def Root(block):
		ids = [transaction for transaction in block.transactions]
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
		prev_block = network.getHead()
		self.header = BlockHeader(prev_block.hash,threshold)
		self.flags = 0x00
		self.transactions = []
		self.height = prev_block.height + 1

	def addTransaction(sender_id, receiver_id, amount):
		sender = network.getNode(sender_id)
		receiver = network.getNode(receiver_id)
		transaction = Transaction(sender_id, receiver_id, amount, self)
		self.transactions.append(transaction)

	def __save__(self):
		self.reward = 0
		self.hash = self.Hash(self)
		self.difficulty = self.Difficulty(self.hash)
		self.signature = self.generateSignature(network.getCurrent().key())
		self.miner = network.getMiner(self)

class Transaction(object):
	__slots__ = ['hash', 'block']
	
	def __init__(self, sender_id, receiver_id, amount, block):
		chain = network.getChain()
		self.hash = self.Hash(sender_id, receiver_id, amount)
		if (self.verify(self)):
			self.block = block
			chain.transactions.append(self.hash)
	
	def __repr__(self):
		return "<%s> * %s *" %(self.block, self.hash[:10])

	def verify(self):
		if transaction_valid:
			return True
		raise TransactionError("Invalid transaction.")

class indieChain(object):
	pass

class TransactionError(Exception):
	pass