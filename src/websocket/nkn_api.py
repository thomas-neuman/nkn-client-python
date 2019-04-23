import asyncio
import json

from nkn_client.websocket.api_client import WebsocketApiClient


class NknWebsocketApiClientError(Exception):
  def __init__(self, Error=None, Desc=None):
    msg = "Got error from NKN API!\nCode: %s\nDesc: %s" % (Error, Desc)
    Exception.__init__(msg)

class NknWebsocketApiClient(WebsocketApiClient):
  def __init__(self, url):
    WebsocketApiClient.__init__(self, url)

    # Retains incoming messages, to be handled by other classes.
    self._inbox = asyncio.Queue()

    # The latest block hash.
    self._latest_hash = None

    self.INTERRUPT_HANDLERS = {
      "receivePacket": self.receive_packet,
      "updateSigChainBlockHash": self.update_sig_chain_block_hash
    }

  async def interrupt(self, msg):
    method = msg["Action"]
    try:
      handler = self.INTERRUPT_HANDLERS[method]
      await handler(**msg)
    except KeyError:
      # TODO: Log unhandled message with a warning.
      pass

  async def _call_rpc(self, method, **kwargs):
    """
    Wraps the usual client 'call_rpc' method with additional handling to
    raise errors and return the actual result value from the response.

    See WebsocketApiClient.call_rpc for args.
    """
    res = await self.call_rpc(self, method, **kwargs)
    self.raise_error(**res)
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

  async def get_session_count(self, host):
    """
    Get session amount of websocket.

    Args:
      host (str)  : Websocket to query.
    Returns:
      int         : The session count.
    """
    res = await self._call_rpc("getsessioncount", Addr=host)
    return res

  async def set_client(self, addr):
    """
    Register a client. Note that a client should call getwsaddr to get
    the node it should register with. If a client tries to register with
    other nodes, an error will be returned.

    Args:
      addr (str)  : NKN address to register to the connected node.
    """
    res = await self._call_rpc("setclient", Addr=addr)
    return res

  async def send_packet(self, dest, payload, signature):
    """
    Send a packet to destination NKN client. Destination NKN address
    should be a client NKN address in the form of "identifier.pubkey".

    Args:
      dest (str)      : NKN address to send to.
      payload (str)   : The message to send.
      signature (str) : Signature of packet, signed by client.
    """
    res = await self._call_rpc(
        "sendPacket",
        Dest=dest,
        Payload=payload,
        Signature=signature
    )
    return res

  async def receive_packet(
      self,
      Action=None,
      Src=None,
      Payload=None,
      Digest=None
  ):
    """
    Push a packet to client.

    Args:
      Action (str)  : Method of the API. Must be "receivePacket".
      Src (str)     : NKN address of the source client.
      Payload (str) : The message received.
      Digest (str)  : Ignored currently.
    """
    assert Action == "receivePacket"

    await self._inbox.put( (Src, Payload, Digest) )

  async def get_incoming_packet(self):
    """
    Get the next packet received on this client.

    Returns:
      (str, str, str) : Source address, payload, digest.
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
    self._latest_hash = Result

  @property
  def sig_chain_block_hash(self):
    return self._latest_hash