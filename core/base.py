import network
import dataStorage
from utils import *
from time import time

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size', 'block']
	
	def __init__(self, prev_hash, threshold, block):
		self.previous_hash = prev_hash
		self.timestamp = time()
		self.target_threshold = threshold
		self.block = block
	
	def __repr__(self):
		return "<%s> Header of Block %s" %(self.timestamp, self.block)

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
		prev_block = dataStorage.getLocalHead()
		self.header = BlockHeader(prev_block.hash,threshold, self)
		self.transactions = []
		self.height = prev_block.height + 1
		self.flags = 0x00

	def __repr__(self):
		try:
			return "Block %s : <%s>" %(self.height, self.hash)
		except:
			return "Block %s" % self.height

	def addTransaction(sender_address, receiver_address, amount):
		transaction = Transaction(sender_address, receiver_address, amount, self)
		self.transactions.append(transaction)
		self.flags = 0x11

	def save(self):
		self.header.save()
		# try:
		# 	self.reward = self.transactions[0].amount
		self.hash = self.Hash(self)
		self.difficulty = self.Difficulty(self.hash)
		self.signature = self.generateSignature(network.getCurrent().key())
		self.miner = network.getMiner(self)
		self.chain = network.getChain()
		self.chain.append(self)


class Transaction(object):
	__slots__ = ['id', 'block', 'sender', 'receiver', 'chain']
	
	def __init__(self, sender_address, receiver_address, amount, block):
		self.chain = chain
		self.id = self.Hash(sender_address, receiver_address, amount)
		self.block = block
		self.sender = sender_address
		self.receiver = receiver_address
		self.value = amount
		chain.transactions.append(self.hash)
	
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

	def __init__(self):
		self.blocks = []
		self.transactions = []

	def getHead(self):
		try:
			return self.blocks[-1]
		else:
			return None

	def push(self, block):
		def validateBlock(self, block):
			head = self.getHead()
			assert(isinstance(block, Block))
			if self.blocks = []:
				raise ValidityError("Initialise blockchain with Genesis block")
			return (head.hash == block.header.previous_hash)

		if validateBlock(block):
			self.blocks.append(block)

	def getGenesis(self):
		if self.blocks == []:
			return None
		return self.blocks[0]

	def generateGenesis(self, genesisBlock):
		assert(isinstance(genesisBlock, Block))
		self.blocks.append(block)