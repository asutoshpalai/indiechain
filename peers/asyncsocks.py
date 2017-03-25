import asyncio

class PeerAsync(asyncio.Protocol):
    transport = None

    def __init__(self, peer):
        self.peer = peer

    def connection_made(self, transport):
        self.transport = transport
        print("Connection made")

    def data_received(self, data):
        self.peer.data_received(data)

    def connection_lost(self, exc):
        # The socket has been closed, stop the event loop
        loop.stop()
