# import network
# import dataStorage
# from core.merkle import *
from .utils import *
from .base import *

from functools import reduce
import random, string
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as pkcs1_15
from time import time

class Wallet(object):
	import string
	def __init__(self, node, initial_amount):
		assert(isinstance(node, Node))
		self.node = node
		self.publicKey = node.getNodePublicKey()
		self.sender_endpoint = []
		self.address = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		coinbaseTransaction = UTXO(self.address, self.address, initial_amount)
		self.receiver_endpoint = [{'data': coinbaseTransaction, 'used': 0}]
		self.transactions = []

	def makePayment(self, receiver_address, amount):
		utxo = UTXO(self.address, receiver_address, amount)
		return utxo

	def finalizeTransaction(self, utxos):
		def balance(utxo):
			return utxo['data'].value - utxo['used']

		transaction = Transaction(utxos)
		receiver_endpoint_copy = self.receiver_endpoint
		sender_endpoint_copy = self.sender_endpoint
		for utxo in utxos:
			utxo.transaction = transaction
		outgoing_sum = sum(utxo.value for utxo in utxos)
		self_inputs = list(filter(lambda u: balance(u) > 0, self.receiver_endpoint))
		self_inputs.sort(key = lambda u: balance(u))
		larger_input = list(filter(lambda u: balance(u) >= outgoing_sum ,self_inputs))
		if larger_input:
			larger_input[0]['used'] += outgoing_sum
			transaction.inputs.append(larger_input)
		else:
			iterator_sum = 0
			for received_inputs in self_inputs:
				if iterator_sum + balance(received_inputs) <= outgoing_sum:
					iterator_sum += balance(received_inputs)
					received_inputs['used'] = received_inputs['data'].value
					transaction.inputs.append(received_inputs)
				else:
					break
			if iterator_sum < outgoing_sum:
				partial_balances = list(filter(lambda u: balance(u) > 0, self_inputs))
				if partial_balances:
					partial_balance = partial_balances[0]
					partial_balance['used'] += outgoing_sum - iterator_sum
					transaction.inputs.append(partial_balance)
					iterator_sum = outgoing_sum
			if iterator_sum < outgoing_sum:
				self.receiver_endpoint = receiver_endpoint_copy
				self.sender_endpoint = sender_endpoint_copy
				del transaction
				raise TransactionError("Cannot make the required transaction, due to insufficient balance.")
		#destination = network.getWallet(receiver_address)
		#destination.receiveUTXO(utxo)
		for utxo in utxos:
			self.sender_endpoint.append({'data': utxo, 'amount': utxo.value})
		self.signTransaction(transaction)
		self.transactions.append(transaction)
		self.node.pushTransaction(transaction)

	def signTransaction(self, transaction):
		assert(isinstance(transaction, Transaction))
		transaction.signature = pkcs1_15.new(self.node._key).sign(SHA256.new(str(transaction).encode('utf-8')))

	#listening service on each wallet
	def receiveUTXO(self, utxo):
		self.receiver_endpoint.append({'data': utxo, 'used': False})

	#for demonstration purposes only
	def selfAdd(self, amount):
		selfTransaction = UTXO(self.address, self.address, amount)
		self.receiver_endpoint += [{'data': selfTransaction, 'used': 0}]

class Node(object):
	MAX_TX_LIMIT = 3
	__slots__ = ['id', 'chain', 'pool', '_key', 'current_block', 'network']
	ROLE = 'N'

	def __init__(self, chain):
		# self.id = network.getNetworkId()
		self.id = ''.join(random.choice(string.digits) for _ in range(3))
		assert(isinstance(chain, indieChain))
		self.chain = chain
		self.pool = []
		self._key = self.getNodeKey()

	def setNetwork(self, network):
		self.network = network

	def getNodePublicKey(self):
		return self._key.publickey()

	def getNodeKey(self):
		try:
			with open(".rsa/private.pem",'r') as write_key:
				key = RSA.importKey(write_key.read())
		except:
			key = RSA.generate(2048)
			with open(".rsa/private.pem",'wb') as write_key:
			    write_key.write(key.exportKey())
			with open(".rsa/public.pem",'wb') as write_key:
			    write_key.write(key.publickey().exportKey())
		return key

	def signBlock(self, block):
		block.signature =  pkcs1_15.new(self._key).sign(SHA256.new(block.hash.encode('utf-8')))
		block.node = self.id

	def createBlock(self):
		self.current_block = Block(self.chain)
		if self.pool != []:
			for transaction in self.pool:
				self.current_block.addTransaction(transaction)
			self.pool = []

	def addBlock(self):
		block = self.current_block
		self.signBlock(block)
		#transmit block to peers
		self.network.broadcastToMiners(block)
		#list of response received from Miners. In case block is correct, response is (MinerID, Nonce). In case of Fork,
		#(MinerID, [<blocks>]]) is received & if invalid, (MinerID, 'INVALID') is the response.
		#responseFromMiners must execute evaluateBlock() on miners which yields the value
		responses = self.network.responseFromMiners()
		responses = dict(response)

		if 'INVALID' in responses.values():
			self.current_block = None
			raise ValidityError("Block terminated due to invalidation from Miner")

		temp_nonce = None
		for value in responses.values():
			if isinstace(value, int):
				temp_nonce = value
				break
		if all(value == temp_nonce for value in responses.values()):
			block.save(temp_nonce)
			self.network.TransmitToPeers(block)
			#executes receiveBlock on all peers
		else:
			lagBlocks = []
			for key, value in responses.items():
				if isinstace(value, list):
					lagBlocks += value
			lagBlocks = list(set(lagBlocks))
			# lagHead = filter(lambda u: ,lagBlocks)
			#push the blocks correctly and update current_block.header.prev_hash


	def pushTransaction(self, transaction):
		try:
			self.current_block.addTransaction(transaction)
			print(self.current_block.transactions)
			if len(self.current_block.transactions) >= self.MAX_TX_LIMIT:
				self.addBlock()
		except Exception as e:
			self.createBlock()
			self.current_block.addTransaction(transaction)
		## peers = network.getPeers()
		## or get network layer to do it
		## for peer in peers:
		## 	peer.receiveTransaction(transaction)
		self.network.broadcastToPeers(transaction)
		# **CORRECT-> broadcast the transaction block to all it peers in Network Layer**

	#listening service for transaction
	def receiveTransaction(self, transaction):
		try:
			if transaction not in self.chain.transactions:
				self.current_block.addTransaction(transaction)
			if len(self.current_block.transactions) > self.MAX_TX_LIMIT:
				self.addBlock()
				self.createBlock()
		except AttributeError:
			self.pool.append(transaction)

	#listening service for block
	def receiveBlock(self, block):
		if self.ROLE == 'M':
			if self.anayseBlock(block):
				self.addBlock(block)
		elif block not in self.chain.blocks:
			if self.current_block:
				self.chain.push(block)
				current_block.header.prev_hash = block.hash
				current_block.header.height = block.height + 1
			self.network.TransmitToPeers(block)
			#executes receiveBlock on all peers

	def __repr__(self):
		return '<%s> %s' % (self.ROLE, self.id)


#current version of code expects the miner to be live throughout. Thereby implying persistance among miners
class Miner(Node):
	ROLE = 'M'

	#listening service corresponding to getForkedBlocks
	def evaluateBlock(self, block):
		assert(isinstance(block, Block))
		if not block.nonce:
			for transaction in block.transactions:
				if transaction in self.chain.transactions:
					return 'INVALID'

			signerPublicKey = self.network.getNodePublicKey(block.node)
			try:
				signerPublicKey.verify(SHA256.new(block.hash.encode('utf-8')), block.signature)
			except (ValueError, TypeError):
				return 'Incorrect Signature'

			if block.flags == 0x11:
				if not reduce(lambda x, y: x and y, map(verifyTransaction, block.transactions)):
					return 'INVALID'

		local_parent = filter(lambda u: u.header.height == block.header.height - 1, self.chain.blocks)[0]
		#Miner contains uptill the parent of the block. Hence no fork. simply add the block
		if local_parent.height == len(self.chain.blocks):
			#generateNonce calculates the nonce and returns the nonce value
			return generateNonce(block)

		elif local_parent.hash == block.header.prev_hash:
			fork_height = block.header.height - 1
			excess_blocks = filter(lambda u: u.header.height > fork_height, self.chain.blocks)
			#this generates the response to FORK condition
			return excess_blocks
		else:
			prev_block = self.network.getBlock(block.node, block.header.prev_hash)
			return self.evaluateBlock(prev_block)

	@classmethod
	def generateNonce(block):
		temp_block = block
		for i in range(5*10**6):
			temp_block.header.nonce = i
			if sha256(str(temp_block).encode('utf-8')).hexdigest()[:block.threshold] == '0'*block.threshold:
				return i
		raise MiningError("Unable to mine block within the constraints.")

	def addBlock(self, block):
		block.miner = self.id
		chain.push(block)
		return 'Successfully appended to the blockchain'

	@classmethod
	def verifyTransaction(transaction):
		signerPublicKey = self.network.getNodePublicKey(wallet_address = transaction.error)
		#returns publickey of node associated with the wallet address
		try:
			signerPublicKey.verify(SHA256.new(str(transaction).encode('utf-8')), transaction.signature)
			return True
		except (ValueError, TypeError):
			return False
