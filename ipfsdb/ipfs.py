import ipfsapi
import io
from sys import argv

ipfs_config_host = '127.0.0.1'
ipfs_config_port = 5001

class ipfsAPI():
	__slots__ = ['api']

	def __init__(self, host=ipfs_config_host, port=ipfs_config_port):
		self.api = ipfsapi.connect(host, port)

	def getAPI():
		return self.api

	def getBlock(self,ipfs_hash):
		return self.api.block_get(ipfs_hash)

	def putBlock(self, block):
		return self.api.block_put(io.BytesIO(block))
