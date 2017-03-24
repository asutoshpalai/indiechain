import network
from utils import *
from time import time

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size', 'block']
	
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
		ids = [transaction.id for transaction in block.transactions]
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
		self.flags = 0x01
		self.transactions = []
		self.height = prev_block.height + 1

	def addTransaction(sender_address, receiver_address, amount):
		try:
			transaction = Transaction(sender_address, receiver_address, amount, self)
			self.transactions.append(transaction)
			self.flags = 0x11
		except TransactionError:
			return 'Invalid transaction. Try again.'	

	def save(self):
		self.header.save()
		try:
			self.reward = self.transactions[0].amount
		self.hash = self.Hash(self)
		self.difficulty = self.Difficulty(self.hash)
		self.signature = self.generateSignature(network.getCurrent().key())
		self.miner = network.getMiner(self)
		self.chain = network.getChain()
		self.chain.append(self)


class Transaction(object):
	__slots__ = ['id', 'block', 'sender', 'receiver', 'chain']
	
	def __init__(self, sender_address, receiver_address, amount, block):
		if verify(sender_address, receiver_address, amount, block.chain):
			self.chain = chain
			self.id = self.Hash(sender_address, receiver_address, amount)
			self.block = block
			self.sender = sender_address
			self.receiver = receiver_address
			chain.transactions.append(self.hash)
		else:
			raise TransactionError
	
	def __repr__(self):
		return "<%s> * %s *" %(self.block, self.hash[:10])

	@classmethod
	def verify(sender_address, receiver_addres, amount, chain):
		inputs = getInputs(chain, sender_address)
		sender_value = sum(inputs.value)
		if amount + reward <= sender_value:
			return True
		return False

	@classmethod
	def getInputs(chain, address):
		return filter(lambda u: u.receiver=address, chain.transactions)

class indieChain(object):
	__slots__ = ['transactions', 'blocks']