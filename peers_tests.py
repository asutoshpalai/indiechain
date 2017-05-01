import peers
from core.nodes import Miner, Node, Wallet
from core.base import indieChain, Block

import logging
from time import sleep
import _thread
from threading import Thread
from core.base import UTXO, Transaction
import random

# loggin.Logger.set
logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.ERROR)

main_port = random.randint(4000, 9999)

man1, man2 = None, None
wal1, wal2 = None, None

def main(port):
    global man1, wal1
    man = peers.Manager('localhost', port)
    man1 = man
    ic = indieChain()
    miner = Miner(ic)
    man.setNode(miner)
    miner.setNetwork(man)
    #print(miner.getNodePublicKey().exportKey())

    try:
        man.activity_loop()
    except Exception as e:
        man.close()
        raise(e)

def peer1(id, main_port):
    global man2, wal2
    sleep(1)
    man = peers.Manager('localhost', main_port + id)
    man2 = man
    ic = indieChain()
    node = Node(ic)
    man.setNode(node)
    node.setNetwork(man)
    wallet = Wallet(node, 10000)
    wal2 = wallet

    try:
        loop = man.loop
        peer = loop.run_until_complete(man.connect_to_peer('localhost', main_port))
        sleep(1)
        # loop.run_until_complete(peer.send_raw_data(b'asdfa'))
        sender = 'acsds'
        # man.broadcastTrx(t1)
        sender = 'qprs'
        wallet.finalizeTransaction([wallet.makePayment('a', 100), wallet.makePayment('z', 50)])
        wallet.finalizeTransaction([wallet.makePayment('b', 100), wallet.makePayment('c', 50)])
        # man.broadcastTrx(t2)
        # sleep(1)
        wallet.finalizeTransaction([wallet.makePayment('e', 100), wallet.makePayment('f', 50)])
        wallet.finalizeTransaction([wallet.makePayment('t', 100), wallet.makePayment('y', 50)])
        # man.broadcastToMiners(b)
        print(peer._key.exportKey())

        # blk = loop.run_until_complete(man.getBlock(peer.id, '3248234a983b7894d923c49'))
        # print(blk)
        man.activity_loop()

    except Exception as e:
        man.close()
        raise(e)

# def peer_tester(id, main_port):
    # man = peers.Manager('localhost', 5003)
    # try:
        # loop = man.loop
        # peer = loop.run_until_complete(man.connect_to_peer('localhost', main_port))
        # loop.run_until_complete(peer.send_raw_data(b'derfadsa'))
        # loop.ensure_future(peer.send_raw_data(b'derfadsa'))
        # print(loop._ready)
        # loop.run_forever()
        # print("DAta sent")
    # except Exception as e:
        # man.close()
        # raise(e)


try:
    t1 = Thread(target=main, args=(main_port,))
    t1.start()
    t2 = Thread(target=peer1, args=(1, main_port)  )
    t2.start()
    t1.join()
    print("Thread-1 joined")

    # t2.join()

    # t1 = Thread(target=peer_tester, args=(1, 5005))
    # t1.start()
    # t1.join()
except KeyboardInterrupt as kb:
    pass
except Exception as e:
    print("Error: unable to start thread")
    raise(e)

# ex: set tabstop=4 shiftwidth=4  expandtab:
