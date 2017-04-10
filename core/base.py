from utils import *
from time import time
from hashlib import sha256
from functools import reduce

class UTXO(object):
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
	# __slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size', 'block']
	
	def __init__(self, prev_block, threshold, block):
		self.previous_hash = prev_block.hash
		self.timestamp = time()
		self.target_threshold = threshold
		self.block = block
		try:
			self.height = prev_block.header.height + 1
		except AttributeError:
			self.height = 1
		self.size = 0
	
	def save(self, nonce, size):
		self._nonce = nonce
		self.size = size
	
	@property
	def nonce(self):
		return self._nonce
	@nonce.setter
	def nonce(self, value):
		raise TypeError("Immutable data")
	
	def __repr__(self):
		return "<%s> Header of Block %s" %(self.timestamp, self.block.header.height)

	def __str__(self):
		return reduce(lambda x,y: x + '|' + y, [str(getattr(self, attr)) for attr in self.__slots__])

class Block(object):
	__slots__ = ['header', 'transactions', 'flags', 'chain', 'threshold', 'hash', 'signature', 'miner', 'node']

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

	def save(self, nonce):
		size = len(str(self.block))
		self.header.save(nonce, size)
		self.timestamp = time()
		self.hash = sha256(sha256(str(self)).hexdigest()).hexdigest()

	def addTransaction(self, transaction):
		self.transactions.append(transaction)
		self.flags = 0x11

	def __repr__(self):
		try:
			return "Block <%s>" %(self.header.height, self.hash)
		except:
			return "Block %s" % self.header.height

	def __str__(self):
		return reduce(lambda x,y: x + '|' + y, [str(getattr(self, attr)) for attr in self.__slots__ if attr != 'hash'])

class GenesisBlock(object):
	def __init__(self):
		self.timestamp = time()
		self.height = 0
		self.hash = sha256(str(self.timestamp)).hexdigest()
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
			if self.blocks == []:
				block.height = 0
				print('<Genesis Block>')
			else:	
				try:
					assert(block.height > head.height)
				except AssertionError:
					return 'Block: Invalid type'
			return (head.hash == block.header.previous_hash)

		if validateBlock(block):
			self.blocks.append(block)
			for transaction in block.transactions:
				self.transactions.append(transaction)

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

	def getBlock(id):
		for block in self.blocks:
			if block.hash == id:
				return block

	def __repr__(self):
		return 'indieChain: ' + ' '.join([str(block.height) for block in self.blocks])