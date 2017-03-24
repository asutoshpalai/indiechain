from time import time
import network

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size']
	
	def __init__(self, prev_hash, threshold):
		self.previous_hash = prev_hash
		self.timestamp = time()
		self.target_threshold = threshold
		self.block = None
	
	def getNonce(self):
		block = self.block
		pass
	@property
	def nonce(self):
		return self._nonce
	@nonce.setter
	def nonce(self, value):
		if value == getNonce(self):
			self._nonce = value
		else:
			raise TypeError("Immutable data")

	def getMerkleRoot(self):
		block = self.block
		ids = [transaction for transaction in block.transactions]
		pass
	@property
	def merkle_root(self):
		return self._merkle_root
	@merkle_root.setter
	def merkle_root(self, value):
		if value == getMerkleRoot(self):
			self._merkle_root = value
		else:
			raise TypeError("Immutable data")

	def save(self, transactions, block):
		self.merkle_root = getMerkleRoot(self)
		self.nonce = getNonce(self)
		self.size = getSize(self)


class Block(object):
	def __init__(self, threshold = 4):
		prev_block = network.getLocalHead()
		self.header = BlockHeader(prev_block.hash,threshold)
		self.header.block = self
		self.flags = 0x00
		self.transactions = []
		self.height = prev_block.height + 1

	def addTransaction(sender_id, receiver_id, amount):
		sender = network.getNode(sender_id)
		receiver = network.getNode(receiver_id)
		try:
			transaction = Transaction(sender_id, receiver_id, amount, self)
			self.transactions.append(transaction)
		except TransactionError:
			return 'Invalid transaction. Try again.'	

	def save(self):
		self.header.save()
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
		if (self.verify(sender_id, receiver_id, amount)):
			self.block = block
			chain.transactions.append(self.hash)
		else:
			raise TransactionError
	
	def __repr__(self):
		return "<%s> * %s *" %(self.block, self.hash[:10])

	def verify(sender_id, receiver_id, amount):
		sender = network.getNode(sender_id)
		receiver = network.getNode(receiver_id)
		if transaction_valid:
			return True
		return False


class indieChain(object):
	pass


class TransactionError(Exception):
	pass