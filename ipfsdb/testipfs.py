import ipfs

api = ipfs.ipfsAPI()
f = open('test.txt','w')
f.write("Test passed")
f.close()
f = open('test.txt','r')
block_read = f.read()
val = api.putBlock(str.encode(block_read))
print(val['Key'])
print(val['Size'])
print(api.getBlock(val['Key']))
