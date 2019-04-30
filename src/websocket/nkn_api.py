import asyncio
import json
import logging

from nkn_client.websocket.api_client import WebsocketApiClient
from nkn_client.proto.packet_pb2 import OutboundPacket, InboundPacket

log = logging.getLogger(__name__)


class NknWebsocketApiClientError(Exception):
  def __init__(self, Error=None, Desc=None):
    msg = "Got error from NKN API!\nCode: %s\nDesc: %s" % (Error, Desc)
    Exception.__init__(self, msg)

class NknWebsocketApiClient(WebsocketApiClient):
  def __init__(self):
    WebsocketApiClient.__init__(self)

    # Retains incoming messages, to be handled by other classes.
    self._inbox = asyncio.Queue()

    # The latest block hash.
    self._latest_hash = None

    self.INTERRUPT_HANDLERS = {
      "updateSigChainBlockHash": self.update_sig_chain_block_hash
    }

  async def interrupt(self, msg):
    if isinstance(msg, bytes):
      log.debug("Attempting to receivePacket with message %s" % (msg))
      pkt = InboundPacket()
      pkt.ParseFromString(msg)
      
      await self.receive_packet(pkt)
      return

    method = msg["Action"]
    try:
      handler = self.INTERRUPT_HANDLERS[method]
      await handler(**msg)
    except KeyError:
      log.warn("Uknown method %s!" % (method))
      pass

  async def _call_rpc(self, method, timeout=None, **kwargs):
    """
    Wraps the usual client 'call_rpc' method with additional handling to
    raise errors and return the actual result value from the response.

    See WebsocketApiClient.call_rpc for args.
    """
    log.debug(
      "Call RPC: method %s, timeout %s, kwargs %s" %
      (method, timeout, kwargs)
    )
    res = await self.call_rpc(method, timeout=timeout, **kwargs)
    self.raise_error(**res)
    log.debug("Call RPC result: %s" % (res))
    return res["Result"]

  def raise_error(self, Error=None, Desc=None, **kwargs):
    """
    Extracts error information from a response, and uses it to raise an
    error through the Client. If there is no error reported from the API
    response, then this method is effectively a no-op.

    Args:
      Error (int)                 : Error code from the response.
      Desc (str)                  : Error description from the response.
    Raises:
      NknWebsocketApiClientError  : If any error is present.
    """
    if Error != 0:
      raise NknWebsocketApiClientError(Error=Error, Desc=Desc)

  async def get_latest_block_height(self):
    """
    Get the height of current block.

    Returns:
      int : The current block height.
    """
    res = await self._call_rpc("getlatestblockheight")
    return res

  async def get_block(self, height=None, hash=None):
    """
    Get the block information by height or hash. Only one of height or
    hash may be set.

    Args:
      height (int)  : Height of block to query.
      hash (str)    : Hash of block to query.
    Returns:
      dict          : Block information.
    """
    if height is not None:
      assert hash is None
      res = await self._call_rpc("getblock", height=height)
      return res

    assert hash is not None
    res = await self._call_rpc("getblock", hash=hash)
    return res

  async def get_connection_count(self):
    """
    Get the connection amount to this node.

    Returns:
      int : The connection count.
    """
    res = await self._call_rpc("getconnectioncount")
    return res

  async def get_transaction(self, hash):
    """
    Get a transaction by hash.

    Args:
      hash (str)  : Hash of the transaction to query.
    Returns:
      dict        : The transaction information.
    """
    res = await self._call_rpc("gettransaction", hash=hash)
    return res

  async def heartbeat(self):
    """
    Send a heartbeat.
    """
    res = await self._call_rpc("heartbeat")
    return res

  async def get_session_count(self, Addr):
    """
    Get session amount of websocket.

    Args:
      Addr (str)  : Websocket to query.
    Returns:
      int         : The session count.
    """
    res = await self._call_rpc("getsessioncount", Addr=Addr)
    return res

  async def set_client(self, Addr):
    """
    Register a client. Note that a client should call getwsaddr to get
    the node it should register with. If a client tries to register with
    other nodes, an error will be returned.

    Args:
      Addr (str)  : NKN address to register to the connected node.
    """
    res = await self._call_rpc("setclient", Addr=Addr)
    return res

  async def send_packet(self, packet):
    """
    Send a packet to destination NKN client. Destination NKN address
    should be a client NKN address in the form of "identifier.pubkey".

    Args:
      packet (OutboundPacket) : Packet to transmit.
    """
    msg = packet.SerializeToString()

    await self.send(msg)

  async def receive_packet(self, packet):
    """
    Push a packet to client.

    Args:
      packet (InboundPacket)  : The incoming packet.
    """
    log.debug(
      "Received packet: src %s, payload %s" %
      (packet.src, packet.payload)
    )

    await self._inbox.put(packet)

  async def get_incoming_packet(self):
    """
    Get the next packet received on this client.

    Returns:
      InboundPacket : Next packet received.
    """
    res = await self._inbox.get()
    return res

  async def update_sig_chain_block_hash(
      self,
      Action=None,
      Error=None,
      Desc=None,
      Result=None,
      Version=None
  ):
    """
    Push latest block hash to client. Clients will need this in the
    future when sending packets.

    Args:
      Action (str)  : Method of the API. Must be "updateSigChainBlockHash".
      Error (int)   : Error code, if applicable.
      Desc (str)    : Error description, if applicable.
      Result (str)  : The block hash.
      Version (str) : NKN version.
    """
    log.info("Updating sig chain block hash: %s" % (Result))
    self._latest_hash = Result

  @property
  def sig_chain_block_hash(self):
    return self._latest_hash