import network
import dataStorage
from utils import *
from time import time

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size', 'block']
	
	def __init__(self, prev_block, threshold, block):
		self.previous_hash = prev_block.hash
		self.timestamp = time()
		self.target_threshold = threshold
		self.block = block
		self.height = prev_block.header.height + 1
	
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
		self._merkle_root = getMerkleRoot(self)
		self._nonce = getNonce(self)
		self._size = getSize(self)

	def __repr__(self):
		return "<%s> Header of Block %s" %(self.timestamp, self.block.height)



class Block(object):
	__slots__ = ['header', 'transactions', 'flags', 'chain', 'threshold', 'hash', 'difficulty', 'signature', 'miner']

	def __init__(self, chain, threshold = 4):
		prev_block = chain.getHead()
		if prev_block:
			self.header = BlockHeader(prev_block,threshold, self)
		else:
			raise ValidityError("The chain has no Genesis")
		self.transactions = []
		self.flags = 0x00
		self.chain = chain
		self.threshold = threshold
		
	def addTransaction(sender_address, receiver_address, amount):
		transaction = Transaction(sender_address, receiver_address, amount, self)
		self.transactions.append(transaction)
		self.flags = 0x11

	def save(self):
		self.hash = self.Hash(self)
		self.difficulty = self.Difficulty(self.hash)
		self.signature = None
		self.miner = None
		# self.signature = self.generateSignature(network.getCurrent().key())
		# self.miner = network.getMiner(self)
		# self.chain.append(self)
		self.header.save()

	def __repr__(self):
		try:
			return "Block %s : <%s>" %(self.height, self.hash)
		except:
			return "Block %s" % self.height



class Transaction(object):
	__slots__ = ['id', 'block', 'sender', 'receiver', 'value', 'chain']
	
	def __init__(self, sender_address, receiver_address, amount, block):
		self.id = self.Hash(sender_address, receiver_address, amount)
		self.block = block
		self.sender = sender_address
		self.receiver = receiver_address
		self.value = amount
	
	def __repr__(self):
		return "<%s> * %s *" %(self.block, self.hash[:10])



class indieChain(object):
	__slots__ = ['transactions', 'blocks']

	def __init__(self):
		self.blocks = []
		self.transactions = []

	def getHead(self):
		if blocks == []:
			return None
		else:
			return self.blocks[-1]

	def push(self, block):
		def validateBlock(self, block):
			head = self.getHead()
			try:
				assert(isinstance(block, Block))
				assert(block.timestamp > head.timestamp)
				assert(block.height > head.height)
			except AssertionError:
				return 'Block: Invalid type'
			if self.blocks == []:
				raise ValidityError("Initialise blockchain with Genesis block")
			return (head.hash == block.header.previous_hash)

		if validateBlock(block):
			self.blocks.append(block)
			self.transactions.append

	def getGenesis(self):
		if self.blocks == []:
			return None
		return self.blocks[0]

	def generateGenesis(self, genesisBlock):
		try:
			assert(isinstance(genesisBlock, Block))
		except AssertionError:
			return 'Genesis Block: Invalid type'
		genesisBlock.header.height = 0
		self.blocks.append(block)