import peers
from core.nodes import Miner, Node, Wallet
from core.base import indieChain, Block
import tkinter as tk
from tkinter import *
from tkinter import Canvas, Entry, Label

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

nodelist = ['a', 'b', 'c', 'd','e','f','g','h']

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

def peer1(id, main_port, recvaddr, amount,sender):
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
        # man.broadcastTrx(t1)
        for i in range(0, len(recvaddr), 2):
            wallet.finalizeTransaction([wallet.makePayment(recvaddr[i], int(amount[i]) ), wallet.makePayment(recvaddr[i+1], int(amount[i+1]) )])
        # man.broadcastToMiners(b)
        if len(recvaddr)%2 == 1:
            j = len(recvaddr) -1
            wallet.finalizeTransaction([wallet.makePayment(recvaddr[j], int(amount[j]) ), wallet.makePayment(sender,0) ] )
        print(peer._key.exportKey())

        # blk = loop.run_until_complete(man.getBlock(peer.id, '3248234a983b7894d923c49'))
        # print(blk)
        man.activity_loop()

    except Exception as e:
        man.close()
        raise(e)


class MainWindow(tk.Frame):
    wallet_counter = 0
    miner_counter = 0

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        # self.button1 = tk.Button(self, text="Create new node", command=self.create_node)
        #self.button2 = tk.Button(self, text="Create new miner", command=self.create_miner)
        self.button3 = tk.Button(self, text="Create new wallet", command=self.create_wallet)
        # self.button1.pack(side="top")
        #self.button2.pack(side="top")
        self.button3.pack(side="top")


    def create_wallet(self):
        self.wallet_counter += 1
        self.recvaddr = []
        self.amount = []

        t = tk.Toplevel(self)
        t.wm_title("Wallet #%s" % self.wallet_counter)
        

        lr = Label(t,text='Receiver address: ').pack(side=TOP, padx=10, pady=10)
        entryr = Entry(t, width=20)
        entryr.pack(side=TOP,padx=10,pady=10)

        ln = Label(t,text='Amount: ').pack(side=TOP, padx=10, pady=10)
        entryn = Entry(t, width=20)
        entryn.pack(side=TOP,padx=10,pady=10)


        @coroutine
        def onTransact():
            recvaddr1 = entryr.get()
            self.recvaddr = recvaddr1.split(',')
            amount1 = entryn.get()
            self.amount = amount1.split(',')

            sender = nodelist[self.wallet_counter]
            try:
                t1 = Thread(target=main, args=(main_port,))
                t1.start()
                t2 = Thread(target=peer1, args=(1, main_port, self.recvaddr, self.amount, sender)  )
                t2.start()
                t1.join()
                print("Thread-1 joined")

            except KeyboardInterrupt as kb:
                pass
            except Exception as e:
                print("Error: unable to start thread")
                raise(e)

        Button(t, text='GO', command=onTransact).pack(side=TOP)

        



root = tk.Tk()
main_win = MainWindow(root)
main_win.pack(side="top", fill="both", expand=True)
root.mainloop()



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




# ex: set tabstop=4 shiftwidth=4  expandtab:
