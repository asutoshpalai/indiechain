# import network
# import dataStorage
# from core.merkle import *
from .utils import *
from .base import *

from functools import reduce
import random, string
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
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

	def getBalance(self):
		incoming_amount = sum(receiver['data'].value for receiver in self.receiver_endpoint)
		outgoing_amount = sum(sender['amount'] for sender in self.sender_endpoint)
		return incoming_amount - outgoing_amount

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

	def receiveUTXO(self, utxo):
		self.receiver_endpoint.append({'data': utxo, 'used': False})

	def signTransaction(self, transaction):
		assert(isinstance(transaction, Transaction))
		transaction.signature = pkcs1_15.new(self.node._key).sign(SHA256.new(str(transaction).encode('utf-8')))
	#for demonstration purposes only
	def selfAdd(self, amount):
		selfTransaction = UTXO(self.address, self.address, amount)
		self.receiver_endpoint += [{'data': selfTransaction, 'used': 0}]

class Node(object):
	MAX_TX_LIMIT = 3
	__slots__ = ['id', 'chain', 'pool', '_key', 'current_block']
	ROLE = 'N'

	def __init__(self, chain):
		# self.id = network.getNetworkId()
		self.id = ''.join(random.choice(string.digits) for _ in range(3))
		assert(isinstance(chain, indieChain))
		self.chain = chain
		self.pool = []
		self.getNodePublicKey()

	def getNodePublicKey(self):
		try:
			write_key = open(".rsa/private.pem",'r')
			key = RSA.importKey(write_key.read())
		except:
			key = RSA.generate(2048)
			write_key = open(".rsa/private.pem", 'w').write(key.exportKey())
			write_key = open(".rsa/public.pem", 'w').write(key.publickey().exportKey())
		write_key.close()
		self._key = key
		return key.publickey()

	def signBlock(self, block):	
		block.signature =  pkcs1_15.new(self._key).sign(SHA256.new(block.hash.encode('utf-8')))
		block.node = self.id

	def createBlock(self):
		self.current_block = Block(self.chain)
		if self.pool != []:
			for transaction in self.pool:
				self.current_block.addTransaction(transaction)
			self.pool = []

	def addBlock(self, *args):
		block = self.current_block
		self.signBlock(block)
		peer_miners = network.getMiners()
		try:
			nonce = [peer_miner.addBlock(block) for peer_miner in peer_miners]
			if nonce.count(nonce[0]) != len(nonce):
				raise ValidityError("Nonces not matched by miners.")
			block.nonce = nonce[0]
			self.chain.push(block)
		except UnmatchedHeadError:
			fork_height = peer_miner.getForkId(block)
			pooled_blocks = filter(lambda u: u.header.height > fork_height, chain.blocks)
			self.pool += [pooled_block.transactions for pooled_block in pooled_blocks]
			i = 1
			while True:
				miner_block = peer_miner.getBlockByHeight(fork_height+i)
				
				pass

	def pushTransaction(self, transaction):
		try:
			self.current_block.addTransaction(transaction)
		except:
			self.createBlock()
			self.current_block.addTransaction(transaction)
		# peers = network.getPeers()
		# for peer in peers:
		# 	peer.receiveTransaction(transaction)

	#listening service
	def receiveTransaction(self, transaction):
		try:
			if transaction not in self.current_block.transactions:
				self.current_block.addTransaction(transaction)
			if len(self.current_block.transactions) > MAX_TX_LIMIT:
				self.addBlock(self.current_block)
				self.createBlock()
		except AttributeError:
			self.pool.append(transaction)

	def __repr__(self):
		return '<%s> %s' % (self.ROLE, self.id)



class Miner(Node):
	ROLE = 'M'

	def addBlock(self, block):
		assert(isinstance(block, Block))
		chain = self.chain
		signerPublicKey = network.getNodePublicKey(block.node)
		assert(signerPublicKey.verify(str(block), block.signature))
		for transaction in block.transactions:
			if transaction in chain.transactions:
				return
		if reduce(lambda x, y: x and y, map(verifyTransaction, block.transactions)):
			try:
				# assert(block.nonce[:block.threshold] == '0'*block.threshold)
				assert(consesus(chain, block))
			except AssertionError:
				for transaction in block.transactions:
					self.pool.append(transaction)
				raise ValidityError("Invalid block.")
			block.miner = self
			block.signature = self.getNodeSignature(block)
			if block.flags == 0x11: 
				for transaction in block.transactions:
					block.coinbaseTransaction(transaction, self.wallet.address)
			block.save(mine(block))
			chain.push(block)
			return 'Successfully appended to the blockchain'
		else:	
			raise TransactionError("Invalid transaction(s). Recheck Block.")
			
	@classmethod
	def verifyTransaction(transaction):
		try:
			assert(isinstance(transaction, Transaction))
		except:
			raise TypeError("Transaction not of valid data type")
		signer = network.getNodePublicKey(transaction.sender) #get pubkey given wallet address
		try:
			assert(signer.verify(str(transaction), transaction.signature))
		except AssertionError:
				raise TransactionError(str(transaction) + ": Unauthorized transaction")
		return True

	@classmethod
	def consesus(chain, block):
		miner_peers = network.getMiner()
		miner_peers