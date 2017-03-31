import network
import dataStorage
from core.merkle import *
from core.utils import *

from Crypto.PublicKey import RSA
from time import time

class Wallet(object):
	import string
	TRANSACTION_FEES = 0.01
	def __init__(self, node, initial_amount):
		assert(isinstance(node, Node))
		self.node = node
		# self.signature = getSignature(sha256(random(2**128, 2**256)))
		# generate priv, pub key using bitcointools
		self.unspent_outputs = []
		self.address = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		selfCredit(self, initial_amount)

	def createTransaction(self, utxos):
		assert(validateTransaction(utxos))
		transaction = Transaction(utxos)
		network.sendToNode(transaction)
		pass 

	def getBalance(self):
		pass

	def createUTXO(self, receiver_address):
		pass

	@classmethod
	def selfCredit(this, initial_amount):
		#create a utxo from admin to wallet user
		self.unspent_outputs.append(coinbaseUTXO)
		pass

	@classmethod
	def verifyTransaction(transaction):
		inputs = getInputs(transaction.sender)
		sender_value = sum(inputs.value)
		return (amount + Wallet.TRANSACTION_FEES < sender_value)

	@classmethod
	def getInputs(wallet_address):
		return dataStorage.getWallet(wallet_address).balance



class Node(object):`
	MAX_POOL_LIMIT = 10
	__slots__ = ['id', 'role', 'chain', 'pool', '_key']
	ROLE = 'N'

	def __init__(self, chain):
		self.id = network.getNetworkId()
		self.chain = chain
		self.pool = []

	def createBlock(self, chain, threshold):
		assert(isinstance(chain, indieChain))
		block = Block(chain, threshold)
		return block

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

	def addBlock(self, block):
		try:
			assert(isinstance(block, Block))
			self.signBlock(block)
			peer_miner = network.getMiner()
			peer_miner.addBlock(block, block.chain)
		except AssertionError:
			raise TypeError("Incorrect data instance")
		except TransactionError:
			raise ValidityError("Invalid transactions")

	# Node adds the tran
	def orphanisePool(block):
		assert(isinstance(block, Block))
		assert(len(pool) < MAX_POOL_LIMIT)
		for transaction in block.transactions:
			if not parent(transaction):
				self.pool.append(transaction)
		return pool == []

	def __repr__(self):
		return '<%s> %s' % (self.ROLE, self.id)



class Miner(Node):
	__slots__ = ['id', 'role', 'chain', 'pool']
	ROLE = 'M'

	def __init__(self, wallet_address, chain):
		self.id = network.getNetworkId()
		self.chain = chain
		self.pool = []
		self.wallet = dataStorage.getWallet(wallet_address)


	def addBlock(block, chain):
		assert(isinstance(chain, indieChain))
		assert(isinstance(block, Block))
		signerPublicKey = block.node.getPublicKey()
		assert(signerPublicKey.verify(str(block), block.signature))
		if reduce(lambda x, y: x and y, map(verifyTransaction, block.transactions)):
			try:
				assert(block.nonce[:block.threshold] == '0'*block.threshold)
				assert(consesus(chain, block))
			except AssertionError:
				raise ValidityError("Invalid block.")
			block.miner = self
			block.signature = self.getNodeSignature(block)
			if block.flags == 0x11: 
				for transaction in block.transactions:
					block.coinbaseTransaction(transaction, self.wallet.address)
			block.save(mine(block))
			chain.push(block)
		else:	
			raise TransactionError("Invalid transaction(s). Recheck Block.")
			
	@classmethod
	def verifyTransaction(transaction):
		def unlock(utxo):
			return math.pow(utxo.lockingScript(), utxo.sender.publicKey, utxo._N)
		def getInputs(wallet_address):
			return dataStorage.getWallet(wallet_address).getBalance()
		try:
			assert(isinstance(transaction, Transaction))
		except:
			raise TypeError("Transaction not of valid data type")
		try:
			assert(merkleVerify(transaction))
		except:
			raise ValidityError("Merkle Tree: Transaction route doesn't exist in block")
		for utxo in transaction.utxos:
			try:
				assert(unlock(utxo) == utxo.id)
				inputs = getInputs(transaction.utxo.sender)
				sender_value = sum(inputs.value)
				assert(amount + Wallet.TRANSACTION_FEES < sender_value)	
			except AssertionError:
				raise TransactionError(str(transaction) + ": Invalid transaction")