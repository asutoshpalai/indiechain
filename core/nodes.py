import network
import dataStorage
from core.merkle import *
from core.utils import *

from Crypto.PublicKey import RSA
from time import time

class Wallet(object):
	import string
	def __init__(self, node, initial_amount):
		assert(isinstance(node, Node))
		self.node = node
		self.publicKey = node.getPublicKey()
		self.receiver_endpoint = []
		self.sender_endpoint = []
		self.initial_amount = initial_amount
		self.address = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

	def makePayment(self, receiver_address, amount):
		utxo = UTXO(self.address, receiver_address, amount)
		receiver = dataStorage.getWallet(receiver_address)
		self_inputs = filter(lambda u: u['used'] is False, self.receiver_endpoint)
		larger_input = filter(lambda u: u['data'].amount >= amount ,self_inputs)
		if larger_input:
			larger_input[0]['used'] = True
			utxo.inputs.append(larger_input[0]['data'])
		else:
			timestamp_sorted_inputs = sort(self_inputs, key=lambda u: u['data'].timestamp)
			iterator_sum = 0
			for received_inputs in timestamp_sorted_inputs:
				if iterator_sum + received_inputs['data'].amount <= amount:
					iterator_sum += received_inputs['data'].amount
					received_inputs['used'] = True
					utxo.inputs.append(received_inputs['data'])
				else:
					break
		if not utxo.inputs:
			raise TransactionError("Cannot make the required transaction, due to insufficient funds.")
		receiver.receiver_endpoint.append({'data': utxo, 'used': False})
		self.sender_endpoint.append(utxo)

	def finalizeTransaction(self, utxos):
		transaction = Transaction(utxos)
		map(lambda u: u.transaction = transaction, utxos)
		signTransaction(transaction)
		self.node.pushTransaction(transaction)

	@classmethod
	def signTransaction(transaction):
		assert(isinstance(transaction, Transaction))
		transaction_hash = str(transaction)
		transaction.signature = self.node._key.sign(transaction_hash, None)

class Node(object):`
	MAX_POOL_LIMIT = 10
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
			write_key = open("../.indiechain/.rsa/private.pem", 'w').write(key.exportKey())
			write_key = open("../.indiechain/.rsa/public.pem", 'w').write(key.publicKey().exportKey())
		write_key.close()
		self._key = key
		return key.publicKey()

	def signBlock(self, block):
		block.signature = self._key.sign(block.hash, None)
		block.node = self

	def createBlock(self,threshold):
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
			peer_miner.addBlock(block, block.chain)
			self.chain.push(block)
		except AssertionError:
			raise TypeError("Incorrect data instance")
		except:
			raise ValidityError("Invalid transactions")

	# Node adds the tran
	def orphanisePool(block):
		assert(isinstance(block, Block))
		assert(len(pool) < MAX_POOL_LIMIT)
		for transaction in block.transactions:
			if not parent(transaction):
				self.pool.append(transaction)
		return pool == []

	def pushTransaction(self, transaction):
		self.current_block.addTransaction(transaction)
		peers = network.getPeers()
		for peer in peers:
			peer.receiveTransaction(transaction)

	def receiveTransaction(self, transaction):
		if transaction not in self.current_block.transactions:
			self.current_block.addTransaction(transaction)

	def __repr__(self):
		return '<%s> %s' % (self.ROLE, self.id)



class Miner(Node):
	__slots__ = ['id', 'role', 'chain', 'pool']
	ROLE = 'M'

	def __init__(self, chain):
		self.id = network.getNetworkId()
		self.chain = chain
		self.pool = []


	def addBlock(block, chain):
		assert(isinstance(chain, indieChain))
		assert(isinstance(block, Block))
		signerPublicKey = block.node.getPublicKey()
		assert(signerPublicKey.verify(str(block), block.signature))
		for transaction in block.transactions:
			if transaction in chain.transactions:
				return
		if reduce(lambda x, y: x and y, map(verifyTransaction, block.transactions)):
			try:
				assert(block.nonce[:block.threshold] == '0'*block.threshold)
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
		# try:
		# 	assert(merkleVerify(transaction))
		# except:
		# 	raise ValidityError("Merkle Tree: Transaction route doesn't exist in block")
		signer = transaction.sender.node.getPublicKey()
		try:
			assert(signer.verify(str(transaction), transaction.signature))
		except AssertionError:
				raise TransactionError(str(transaction) + ": Unauthorized transaction")
		return True

	@classmethod
	def consesus(chain, block):
		miner_peers = network.getMiner()
		miner_peers