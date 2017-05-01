from core.nodes import *
from core.base import *

ic = indieChain()
b = Block(ic)

N = Node(ic)
W = Wallet(N, 1000)
u = [W.makePayment('b', 100), W.makePayment('c', 50)]
print('1st transaction')
W.finalizeTransaction(u)

print('self add 500')
W.selfAdd(500)

print('paying 900 to d')
W.finalizeTransaction([W.makePayment('d', 900)])

print('third transaction')
W.finalizeTransaction([W.makePayment('d', 200)])
N.addBlock()
#2
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#3
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#4
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#5
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#6
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#7
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#8
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#9
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#10
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()
#11
W.finalizeTransaction([W.makePayment('d', 2)])
N.addBlock()