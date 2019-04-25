from nacl.encoding import HexEncoder as Encoder
from nacl.signing import SigningKey as Key

from nkn_client.client.packet import *
from nkn_client.jsonrpc.api import NknJsonRpcApi
from nkn_client.websocket.nkn_api import NknWebsocketApiClient

class NknClient(object):
  """
  Client for the NKN blockchain network.

  Args:
    identifier (str)              : Client identifier.
    seed (str)                    : Private seed for the client key, as hex.
    rpc_server_addr (str)         : Address to bootstrap from JSON-RPC.
    reconnect_interval_min (int)  : Unsupported.
    reconnect_interval_max (int)  : Unsupported.
    response_timeout_secs (int)   : Unsupported.
    msg_holding_secs (int)        : Unsupported.
  """
  def __init__(
      self,
      identifier,
      seed=None,
      rpc_server_addr="devnet-seed-0001.nkn.org:30003",
      reconnect_interval_min=100,
      reconnect_interval_max=64000,
      response_timeout_secs=5,
      msg_holding_secs=3600,
      **kwargs
  ):
    key = Key.generate()
    if seed is not None:
      key = Key.from_seed(seed, Encoder)

    self._key = key
    pubkey = self._key.verify_key

    # NKN client address.
    self._addr = ".".join([ identifier, pubkey.encode(Encoder) ])

    # JSON-RPC API client.
    self._jsonrpc = NknJsonRpcApi(rpc_server_addr)

    # Websocket API client.
    self._ws = None

  @property
  def sig_chain_block_hash(self):
    if self._ws is None:
      return None
    return self._ws.sig_chain_block_hash

  async def connect(self):
    if self._ws is None:
      host = self._jsonrpc.get_websocket_address(self._addr)
      self._ws = NknWebsocketApiClient(hostname)

    await self._ws.connect()

  async def disconnect(self):
    if self._ws is None:
      return

    await self._ws.disconnect()
    self._ws = None

  def _sign_packet(self, packet):
    signature = self._key.sign(packet.payload)
    packet.sign(signature)

  async def send(self, destination, payload):
    if self._ws is None:
      return

    pkt = NknSentPacket(destination, payload)
    self._sign_packet(pkt)

    await self._ws.send_packet(pkt.destination, pkt.payload, pkt.signature)

  async def recv(self):
    if self._ws is None:
      return

    src, payload, digest = await self._ws.get_incoming_packet()
    pkt = NknReceivedPacket(src, payload, digest)

    return pkt