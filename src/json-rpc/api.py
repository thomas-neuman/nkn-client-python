import requests

class NknJsonRpcApi(object):
  """
  A client for the NKN JSON-RPC API. Communicates over plaintext HTTP to submit
  RPC requests according to the JSON-RPC 2.0 specification.

  Args:
    hostname (str) : The hostname on which the API is served.
  """
  def __init__(self, hostname):
    self._host = hostname

  def get_latest_block_height(self):
    """
    Returns the height of the latest block in the chain.
    """
    pass

  def get_latest_block_hash(self):
    """
    Returns the hash of the latest block in the chain.
    """
    pass

  def get_block_count(self):
    """
    Return the number of blocks in the chain.
    """
    pass

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
    pass

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
    pass

  def get_connection_count(self):
    """
    Returns the number of connections to this node.
    """
    pass

  def get_raw_mempool(self):
    """
    Returns the list of transactions in the transaction mempool.
    """
    pass

  def get_transaction(self, hash):
    """
    Given a hash, returns the matching transaction.

    Args:
      hash (str)  : Hash of the transaction.
    Returns:
      dict        : Contents of the transaction, or None if no such transaction
                    exists.
    """
    pass

  def get_websocket_address(self, client_addr):
    """
    Given an NKN client address, returns the websocket address for that client
    to connect to this node.

    Args:
      client_addr (str) : The client address, typically of the form
                          'identifier.pubkey'.
    Returns:
      str               : Hostname and port of the Websocket server, to be
                          concatenated with 'ws://' or 'wss://' to connect.
    """
    pass

  def get_version(self):
    """
    Returns the version of the server.
    """
    pass

  def get_neighbor(self):
    """
    Returns all neighbor nodes of this server.
    """
    pass

  def get_node_state(self):
    """
    Returns the status information of this server.
    """
    pass

  def get_chord_ring_info(self):
    """
    Returns the chord information of this server.
    """
    pass
