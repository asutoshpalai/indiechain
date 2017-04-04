import network
import dataStorage
from utils import *
from time import time
from hashlib import sha256

class UTXO(object):
	__slots__ = ['id', 'transaction', 'sender', 'receiver', 'value', 'timestamp', 'inputs']
	
	def __init__(self, sender_address, receiver_address, amount, block):
		try:
			self._sender = dataStorage.getWallet(sender_address)
			self._receiver = dataStorage.getWallet(receiver_address)
		except:
			raise ValidityError('Invalid addresses. Try again.')
		# self.block = block
		self.value = amount
		self.amount = amount
		self.timestamp = time()
		self.id = sha256(map(str, [self.sender, self.receiver, self.timestamp])).hashdigest()
		self.inputs = []
		self.transaction = None

	@property
	def sender(self):
		return self._sender
	@sender.setter
	def sender(self, value):
		raise TypeError("Immutable data")

	@property
	def receiver(self):
		return self._receiver
	@sender.setter
	def receiver(self, value):
		raise TypeError("Immutable data")

	def __repr__(self):
		return "<%s> * %s *" %(self.block, self.id[:10])


class Transaction(object):
	__slots__ = ['utxos', 'block', 'sender', 'signature']

	def __init__(self,utxos):
		for utxo in utxos:
			assert(isinstance(utxo, UTXO))
		self.utxos = utxos 
		if self.utxos != []:
		self.sender = utxos[0].sender
			try:
				assert(reduce(lambda x, y: x.sender == sender and y, self.utxos))
			except AssertionError:
				raise ValidityError("UTXOs of a given transaction must have same sender.")

	def __str__(self):
		return ''.join(map(lambda u: str(u.id), self.utxos)) + str(self.sender.address)

class BlockHeader(object):
	__slots__ = ['previous_hash', 'merkle_root', 'timestamp', 'target_threshold', 'nonce', 'size', 'block']
	
	def __init__(self, prev_block, threshold, block):
		self.previous_hash = prev_block.hash
		self.timestamp = time()
		self.target_threshold = threshold
		self.block = block
		self.height = prev_block.header.height + 1
		self.size = 0
	
	def save(self, nonce, size):
		self.merkle_root = getMerkleRoot(self)
		self._nonce = nonce
		self.size = size

	def getMerkleRoot(self):
		block = self.block
		ids = [transaction.id for transaction in block.transactions]
		pass
	
	@property
	def nonce(self):
		return self._nonce
	@nonce.setter
	def nonce(self, value):
		raise TypeError("Immutable data")
	
	@property
	def merkle_root(self):
		return self._merkle_root
	@merkle_root.setter
	def merkle_root(self, value):
		if value == getMerkleRoot(self):
			self._merkle_root = value
		else:
			raise TypeError("Immutable data")

	def __repr__(self):
		return "<%s> Header of Block %s" %(self.timestamp, self.block.height)

	def __str__(self):
		return reduce(lambda x,y: x + '|' + y, [str(getattr(self, attr)) for attr in self.__slots__])

class Block(object):
	__slots__ = ['header', 'transactions', 'flags', 'chain', 'threshold', 'hash', 'signature', 'miner', '_N', 'node']

	def __init__(self, chain, threshold = 4):
		try:
			assert(threshold >= 4)
		except AssertionError:
			return ValidityError("Threshold must be GTE 4")
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

	def addTransaction(Transaction)
		self.transactions.append(transaction)
		self.flags = 0x11

	def __repr__(self):
		try:
			return "Block <%s>" %(self.height, self.hash)
		except:
			return "Block %s" % self.height

	def __str__(self):
		return reduce(lambda x,y: x + '|' + y, [str(getattr(self, attr)) for attr in self.__slots__ if attr != 'hash'])

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
		def validateBlock(block):
			head = self.getHead()
			try:
				assert(isinstance(block, Block))
				assert(block.timestamp > head.timestamp)
				assert(block.height > head.height)
			except AssertionError:
				return 'Block: Invalid type'
			if self.blocks == []:
				block.height = 0
				print '<Genesis Block>'
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
