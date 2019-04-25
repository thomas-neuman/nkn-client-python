from nkn_client.client.packet import *
from nkn_client.jsonrpc.api import NknJsonRpcApi
from nkn_client.websocket.nkn_api import NknWebsocketApiClient

class NknClient(object):
  def __init__(self, hostname):
    # NKN client address.
    self._addr = None

    # JSON-RPC API client.
    self._jsonrpc = NknJsonRpcApi(hostname)

    # Websocket API client.
    self._ws = None

  async def connect(self):
    host = self._jsonrpc.get_websocket_address(self._addr)
    self._ws = NknWebsocketApiClient(hostname)

    await self._ws.connect()

  async def disconnect(self):
    await self._ws.disconnect()

  def _sign_packet(self, packet):
    packet.sign("signature")

  async def send(self, dest, message):
    pkt = NknSentPacket(dest, message)
    self._sign_packet(pkt)

    await self._ws.send_packet(pkt.destination, pkt.payload, pkt.signature)

  async def recv(self):
    src, payload, digest = await self._ws.get_incoming_packet()
    pkt = NknReceivedPacket(src, payload, digest)

    return pkt