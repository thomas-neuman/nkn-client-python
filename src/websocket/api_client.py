from nkn_client.websocket.client import WebsocketClient

class WebsocketJsonRpcClient(WebsocketClient):
  """
  Extends the original WebsocketClient by implementing a flow for
  API call-and-response. This flow is synchronous in nature, and
  calls made are therefore blocking. An additional 'interrupt'
  interface is provided for handling messages received outside of
  such a context.
  """
  def __init__(self, url):
    self._lk = threading.Lock()

    self._handlers = {}
    pass

  def interrupt(self, msg):
    """
    Handle an unprompted message from the peer. To be implemented
    by subclasses.

    Args:
      msg (str) : The message received.
    """
    raise NotImplementedError

  def call_rpc(self, method, params=None):
    """
    Invoke an RPC on the peer.

    Args:
      method (str)      : The name of the remote API to call.
      params (iterable) : Any arguments required for the invocation.
                          A list may be provided for positional
                          arguments, or a dict for keywords.
    Returns:
      dict              : The API response.
    """
    pass

  def _parse_json_rpc(self, msg):
    """
    Parse a received message as a JSON RPC.

    Args:
      msg (str)                 : The message.
    Returns:
      dict                      : The parsed JSON RPC.
    Raises:
      WebsocketJsonRpcException : If the message could not be
                                  parsed as an RPC.
    """
    pass

  async def recv(self, msg):
    """
    See WebsocketClient.recv()

    If an API request is outstanding, messages are attempted
    to be handled via the corresponding response handler.
    Otherwise, the message defaults to the interrupt handler.

    Raises:
      WebsocketJsonRpcException : If the message could not be
                                  handled.
    """
    try:
      msg = self._parse_json_rpc(msg)
    except WebsocketJsonRpcException:
      self.interrupt(msg)
    with self._lk:
      method = msg["method"]
      params = msg.get("params")
      try:
        handler, enabled = self._handlers[method]
        assert enabled
        handler(method, params)
      except KeyError:
        raise WebsocketJsonRpcException()