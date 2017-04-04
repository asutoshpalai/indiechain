# import network
# import dataStorage
# from core.merkle import *
from utils import *
from functools import reduce

from Crypto.PublicKey import RSA
from time import time

class Wallet(object):
	import string
	def __init__(self, node, initial_amount):
		assert(isinstance(node, Node))
		self.node = node
		self.publicKey = node.getPublicKey()
		self.sender_endpoint = []
		self.address = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		coinbaseTransaction = UTXO(self.address, self.address, initial_amount)
		self.receiver_endpoint = [{'data': coinbaseTransaction, 'used': 0}]

	def makePayment(self, receiver_address, amount):
		utxo = UTXO(self.address, receiver_address, amount)
		self.sender_endpoint.append(utxo)

	def finalizeTransaction(self, utxos):
		transaction = Transaction(utxos)
		for utxo in utxos:
			utxo.transaction = transaction
		outgoing_sum = sum(utxo.value for utxo in utxos)
		self_inputs = filter(lambda u: u['used'] is False, self.receiver_endpoint)
		larger_input = filter(lambda u: u['data'].value >= outgoing_sum ,self_inputs)
		if larger_input:
			larger_input = sort(larger_input, key = lambda u: u['data'].value)
			larger_input[0]['used'] = True
			transaction.inputs.append(larger_input[0]['data'])
			transaction.reward = larger_input[0]['data'].value - outgoing_sum
		else:
			timestamp_sorted_inputs = sort(self_inputs, key=lambda u: u['data'].timestamp)
			iterator_sum = 0
			transaction.reward = 0
			for received_inputs in timestamp_sorted_inputs:
				if iterator_sum + received_inputs['data'].value <= outgoing_sum:
					iterator_sum += received_inputs['data'].value
					received_inputs['used'] = True
					transaction.inputs.append(received_inputs['data'])
					transaction.reward += received_inputs[0]['data'].value - outgoing_sum
				else:
					break
		if not transaction.inputs:
			raise TransactionError("Cannot make the required transaction, due to insufficient balance.")
		#destination = network.getWallet(receiver_address)
		#destination.receiveUTXO(utxo)
		signTransaction(transaction)
		self.node.pushTransaction(transaction)

	def receiveUTXO(self, utxo):
		self.receiver_endpoint.append({'data': utxo, 'used': False})

	@classmethod
	def signTransaction(transaction):
		assert(isinstance(transaction, Transaction))
		transaction.signature = self.node._key.sign(str(transaction), None)

class Node(object):
	MAX_TX_LIMIT = 10
	__slots__ = ['id', 'ROLE', 'chain', 'pool', '_key']
	ROLE = 'N'

	def __init__(self, chain):
		self.id = network.getNetworkId()
		assert(isinstance(chain, indieChain))
		self.chain = chain
		self.pool = []

	def getNodePublicKey(self):
		write_key = open("../.indiechain/.rsa/private.pem",'r')
		if write_key:
			key = RSA.importKey(write_key.read())
		else:
			key = RSA.generate(2048)
			write_key = open("../.config/.rsa/private.pem", 'w').write(key.exportKey())
			write_key = open("../.config/.rsa/public.pem", 'w').write(key.publicKey().exportKey())
		write_key.close()
		self._key = key
		return key.publicKey()

	def signBlock(self, block):
		block.signature = self._key.sign(block.hash, None)
		block.node = self.id

	def createBlock(self, threshold = 4):
		self.current_block = Block(self.chain, threshold)
		if self.pool != []:
			for transaction in self.pool:
				self.current_block.addTransaction(transaction)
			self.pool = []

	def addBlock(self, block):
		try:
			assert(isinstance(block, Block))
			self.signBlock(block)
			peer_miner = network.getMiner()
			try:
				nonce = peer_miner.addBlock(block)
				block.nonce = nonce
				self.chain.push(block)
			except TransactionError:
				correct, faulty = peer_miner.analyseBlock(block, block.chain)
				self.pool += correct
			except PreviousHeadError:
				fork_height = peer_miner.getForkId(block)
				pooled_blocks = filter(lambda u: u.header.height > fork_height, chain.blocks)
				self.pool += [pooled_block.transactions for pooled_block in pooled_blocks]
				i = 1
				while True:
					miner_block = peer_miner.getBlockByHeight(fork_height+i)
					
					pass

		except AssertionError:
			raise TypeError("Incorrect data instance")

	def pushTransaction(self, transaction):
		self.current_block.addTransaction(transaction)
		peers = network.getPeers()
		for peer in peers:
			peer.receiveTransaction(transaction)

	#listening service
	def receiveTransaction(self, transaction):
		if transaction not in self.current_block.transactions:
			self.current_block.addTransaction(transaction)
		if len(self.current_block.transactions) > MAX_TX_LIMIT:
			self.addBlock(self.current_block)
			self.createBlock()

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