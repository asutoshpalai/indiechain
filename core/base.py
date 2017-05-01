from .utils import *
from time import time
from hashlib import sha256
from functools import reduce

class UTXO(object):
	__slots__ = ['sender', 'receiver', 'value', 'timestamp', 'id', 'transaction']
	def __init__(self, sender_address, receiver_address, amount):
		self.sender = sender_address
		self.receiver = receiver_address
		self.value = amount
		self.timestamp = time()
		self.id = sha256((self.sender + self.receiver + str(self.timestamp)).encode('utf-8')).hexdigest()
		self.transaction = None

	def __repr__(self):
		try:
			return "<%s> * %s *" %(self.block, self.id[:10])
		except:
			return "%s" %(self.id[:10])

class Transaction(object):
	__slots__ = ['utxos', 'block', 'sender', 'signature', 'inputs']

	def __init__(self,utxos):
		self.inputs = []
		for utxo in utxos:
			assert(isinstance(utxo, UTXO))
		self.utxos = utxos
		if self.utxos != []:
			self.sender = utxos[0].sender
			try:
				assert(reduce(lambda x, y: x.sender == self.sender and y, self.utxos))
			except AssertionError:
				raise ValidityError("UTXOs of a given transaction must have same sender.")

	def __str__(self):
		return ''.join(map(lambda u: str(u.id), self.utxos)) + str(self.sender)

	def __repr__(self):
		return self.sender + ': ' + ' '.join([utxo.id[:10] for utxo in self.utxos])

class BlockHeader(object):
	__slots__ = ['previous_hash', 'timestamp', 'nonce', 'threshold', 'size', 'block', 'height']

	def __init__(self, prev_block, threshold, block):
		try:
			self.height = prev_block.header.height + 1
			self.previous_hash = prev_block.hash
		except AttributeError:
			self.previous_hash =  None
			self.height = 1
		self.timestamp = time()
		self.threshold = threshold
		self.block = block
		self.nonce = None
		self.size = 0

	def save(self, nonce, size):
		self.nonce = nonce
		self.size = size

	def __repr__(self):
		return "<%s> Header of Block %s" %(self.timestamp, self.block.header.height)

	def __str__(self):
		return '|'.join([str(getattr(self, attr)) for attr in self.__slots__ if attr not in ['block', 'nonce']])

class Block(object):
	__slots__ = ['header', 'transactions', 'flags', 'chain', 'threshold', 'hash', 'signature', 'miner', 'node']
	hash_variables = ['header', 'transactions', 'chain', 'flags', 'signature']

	def __init__(self, chain, threshold = 4):
		prev_block = chain.getHead()
		if prev_block:
			self.header = BlockHeader(prev_block,threshold, self)
		else:
			raise ValidityError("The chain has no Genesis")
		self.transactions = []
		self.flags = 0x00
		self.chain = chain
		self.signature = None
		self.threshold = threshold

	def save(self, nonce):
		size = len(str(self))
		self.header.save(nonce, size)
		self.hash = sha256(str(self).encode('utf-8')).hexdigest()

	def addTransaction(self, transaction):
		self.transactions.append(transaction)
		if self.flags == 0x00:
			self.flags = 0x11

	def __repr__(self):
		try:
			return "indieChain[%s] %s" %(self.header.height, self.hash[:10])
		except:
			return "indieChain[%s]" % self.header.height

	def __str__(self):
		return '|'.join([str(getattr(self, attr)) for attr in self.hash_variables])


class GenesisBlock(object):
	def __init__(self):
		self.header = BlockHeader(None, 0, self)
		self.timestamp = time()
		self.height = 0
		self.hash = sha256(str(self.timestamp).encode('utf-8')).hexdigest()
		self.size = len(self.hash)

class indieChain(object):
	__slots__ = ['transactions', 'blocks']

	def __init__(self):
		self.blocks = [GenesisBlock()]
		self.transactions = []

	def getHead(self):
		if self.blocks == []:
			return None
		else:
			return self.blocks[-1]

	def push(self, block):
		def validateBlock(block):
			head = self.getHead()
			assert(isinstance(block, Block))
			return (head.hash == block.header.previous_hash)

		if validateBlock(block):
			block.header.height = 1 + self.getHead().header.height
			self.blocks.append(block)
			self.transactions += block.transactions

	def getGenesis(self):
		return self.blocks[0]

	def getHeaders(self):
		return [block.header for block in self.blocks]

	def getBlock(self, b_hash):
		return next(block for block in self.blocks if block.hash == b_hash)

	def __repr__(self):
		return 'indieChain: ' + ' '.join([str(block.hash) for block in self.blocks][:10])
