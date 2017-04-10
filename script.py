from core.nodes import *
from core.base import *

# u = [UTXO('a', 'b', 100), UTXO('a', 'c', 500)]

# t = Transaction(u)
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

