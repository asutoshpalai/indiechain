from .utils import *
from time import time
from hashlib import sha256
from functools import reduce
import operator

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
		return str(self.sender) +': ' + '|'.join(map(lambda u: str(u.receiver), self.utxos))

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
			self.height = 0
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
		return '|'.join([str(getattr(self, attr)) for attr in self.__slots__ if attr not in ['block']])

class Block(object):
	__slots__ = ['header', 'transactions', 'flags', 'chain', 'threshold', 'hash', 'signature', 'miner', 'node']
	hash_variables = ['header', 'transactions', 'chain', 'flags', 'signature']
	depth = 0

	def __init__(self, chain, threshold = 2):
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
		self.hash = None

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
		self.hash = '0' * 64
		self.size = len(self.hash)
		self.depth = 0

	def __repr__(self):
		try:
			return "indieChain[%s] %s" %(self.header.height, self.hash[:10])
		except:
			return "indieChain[%s]" % self.header.height

class SummaryBlock(object):
	__slots__ = ['depth', 'changes', 'header', 'blocks', 'hash', 'height']

	def __init__(self, blocks, depth, prev_block):
		self.header = BlockHeader(prev_block, 4, self)
		self.depth = depth
		self.changes = {}
		self.createSummary(blocks)
		self.blocks = [block.header.height for block in blocks]
		self.hash = blocks[-1].hash
		self.height = self.blocks[0]

	def createSummary(self, blocks):
		if all(isinstance(block, Block) for block in blocks):
			utxos = []
			for blk in blocks:
				for transaction in blk.transactions:
					utxos += transaction.utxos
			outgoing = [(utxo.sender, utxo.value) for utxo in utxos]
			incoming = [(utxo.receiver, utxo.value) for utxo in utxos]
			senders = set([utxo.sender for utxo in utxos])
			receivers = set([utxo.receiver for utxo in utxos])
			for wallet in list(senders) + list(receivers):
				self.changes[wallet] = 0
			for sender in senders:
				self.changes[sender] = -sum(map(lambda v: v[1], filter(lambda u: u[0] == sender, outgoing)))
			for receiver in receivers:
				self.changes[receiver] += sum(map(lambda v: v[1], filter(lambda u: u[0] == receiver, incoming)))
		elif all(isinstance(block, SummaryBlock) for block in blocks):
			all_keys = reduce(operator.add,[block.changes.keys() for block in blocks])
			for key in all_keys:
				self.changes[key] = 0
			for block in blocks:
				for key, value in block.changes.items():
					self.changes[key] += value
		else:
			raise TypeError('Invalid typing of blocks')

	def __repr__(self):
		return 'Summary: [' + '|'.join(map(str, self.blocks)) +']'

class indieChain(object):
	__slots__ = ['transactions', 'blocks', 'freelen', 'base_pointers', 'end_pointers', 'summary_width']

	def __init__(self, freelen=5, width=5):
		self.blocks = [GenesisBlock()]
		self.transactions = []
		#base_pointer[0] points to first height of normal blocks, base_pointer[1] points to depth1 summary blocks.
		#base_pointer[2] points to first dept2 summary blocks
		self.base_pointers = [1]
		self.end_pointers =[1]
		self.freelen = freelen
		self.summary_width = width

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
			self.end_pointers[0] += 1
			self.blocks.append(block)
			self.transactions += block.transactions

	def getGenesis(self):
		return self.blocks[0]

	def getIndexByHeight(self, h):
		for index, block in enumerate(self.blocks):
			if block.header.height == h:
				return index

	def __repr__(self):
		return 'indieChain: ' + ' '.join([str(block.hash)[:10] for block in self.blocks])

	def getHeaders(self):
		return [block.header for block in self.blocks]

	def getBlock(self, b_hash):
		return next(block for block in self.blocks if block.hash == b_hash)
