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


class PeerStreamReader(asyncio.StreamReader):
    _cb = None
    _cb_active = False

    def __init__(self, callBack, loop):
        super().__init__(loop=loop)
        self._cb = callBack
        self._cb_active = True

    def _trigger_cb(self):
        if self._cb_active:
            self._loop.call_soon(self._cb)

    def feed_data(self, data):
        print("Data feed received")
        self._trigger_cb()

        super().feed_data(data)
