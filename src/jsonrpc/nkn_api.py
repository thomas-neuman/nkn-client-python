from nkn_client.jsonrpc.api_client import JsonRpcApiClient

class NknJsonRpcApiClient(JsonRpcApiClient):
  """
  A client for the NKN JSON-RPC API.

  Args:
    hostname (str) : The hostname on which the API is served.
  """
  def __init__(self, hostname):
    JsonRpcApiClient.__init__(self)

    self._url = "http://%s/" % hostname

  def _call(self, method, *args, **kwargs):
    return self.call(self._url, method, *args, **kwargs)

  def get_latest_block_height(self):
    """
    Returns the height of the latest block in the chain.
    """
    return self._call("getlatestblockheight")

  def get_latest_block_hash(self):
    """
    Returns the hash of the latest block in the chain.
    """
    return self._call("getlatestblockhash")

  def get_block_count(self):
    """
    Return the number of blocks in the chain.
    """
    return self._call("getblockcount")

  def get_block(self, height=None, hash=None):
    """
    Given either a height or hash, get the matching block from the chain.

    Args:
      height (int)  : The height of the block to retrieve.
      hash (str)    : The hash of the block to retrieve.
    Returns:
      dict          : The contents of the block, or None if no such block matches.
    Raises:
      ValueError    : If neither height nor hash are provided as parameters, or
                      if both height and hash are provided.
    """
    if (height is not None) and (hash is not None):
      raise ValueError(
          "Cannot supply both of 'height' and 'hash' parameters at once!"
      )

    if height:
      return self._call("getblock", height=height)
    if hash:
      return self._call("getblock", hash=hash)

    raise ValueError("Must supply one of 'height' or 'hash' parameters!")

  def get_block_transactions_by_height(self, height):
    """
    Given the height of a block, returns the transaction hashes from the
    matching block.

    Args:
      height (int)  : The height of the block to look up.
    Returns:
      dict          : The contents of the block, including the list of
                      transactions hashes as strings, or None if no such block
                      exists.
    """
    return self._call("getblocktxsbyheight", height=height)

  def get_connection_count(self):
    """
    Returns the number of connections to this node.
    """
    return self._call("getconnectioncount")

  def get_raw_mempool(self):
    """
    Returns the list of transactions in the transaction mempool.
    """
    return self._call("getrawmempool")

  def get_transaction(self, hash):
    """
    Given a hash, returns the matching transaction.

    Args:
      hash (str)  : Hash of the transaction.
    Returns:
      dict        : Contents of the transaction, or None if no such transaction
                    exists.
    """
    return self._call("gettransaction", hash=hash)

  def get_websocket_address(self, address):
    """
    Given an NKN client address, returns the websocket address for that client
    to connect to this node.

    Args:
      address (str) : The client address, typically of the form
                      'identifier.pubkey'.
    Returns:
      str           : Hostname and port of the Websocket server, to be
                      concatenated with 'ws://' or 'wss://' to connect.
    """
    return self._call("getwsaddr", address=address)

  def get_version(self):
    """
    Returns the version of the server.
    """
    return self._call("getversion")

  def get_neighbor(self):
    """
    Returns all neighbor nodes of this server.
    """
    return self._call("getneighbor")

  def get_node_state(self):
    """
    Returns the status information of this server.
    """
    return self._call("getnodestate")

  def get_chord_ring_info(self):
    """
    Returns the chord information of this server.
    """
    return self._call("getchordringinfo")