import asyncio
import json

from nkn_client.websocket.client import WebsocketClient

class WebsocketApiClient(WebsocketClient):
  """
  Extends the original WebsocketClient by implementing a flow for
  API call-and-response. This flow is synchronous in nature, and
  calls made are therefore blocking. An additional 'interrupt'
  interface is provided for handling messages received outside of
  such a context.
  """
  def __init__(self, url):
    WebsocketClient.__init__(self, url)

    # Set of response handlers. Each key is a method name, and
    # the value is a list of functions which handle responses for
    # responses on that method.
    self._handlers = {}

    # Locks access to the handlers dict.
    self._handlers_lk = asyncio.Lock()

  async def interrupt(self, msg):
    """
    Handle an unprompted message from the peer. To be implemented
    by subclasses.

    Args:
      msg (str) : The message received.
    """
    pass

  async def call_rpc(self, method, timeout=None, **kwargs):
    """
    Invoke an RPC on the peer.

    Args:
      method (str)      : The name of the remote API to call.
      timeout (int)     : Maximum time to await a response, in
                          seconds.
      kwargs            : Additional parameters to supply with the API call.
    Returns:
      dict              : The API response.
    """
    resp = None
    done = asyncio.Event()
    def handle(msg):
      resp = msg
      done.set()

    msg = {
      "Action": method
    }
    if kwargs is not None:
      msg.update(kwargs)
    msg = json.dumps(msg)

    # Register the response handler at the same time as we issue
    # the request.
    async with self._handlers_lk:
      handlers = []
      try:
        handlers = self._handlers[method]
      except KeyError:
        self._handlers[method] = handlers
      handlers.append(handle)

      await self.send(msg)

    try:
      await asyncio.wait_for(done.wait(), timeout=timeout)
    except asyncio.TimeoutError:
      # TODO: Log timeout with error or warning.
      pass
    finally:
      async with self._handlers_lk:
        handlers = self._handlers[method]
        handlers.pop()

    return resp

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
      msg = json.loads(msg)
    except ValueError:
      # If we cannot parse the response, defer to the interrupt handler.
      # TODO: Log parse failure.
      await self.interrupt(msg)
      return

    method = msg["Action"]
    async with self._handlers_lk:
      try:
        # Find the handler for this message, and call it.
        handlers = self._handlers[method]
        handler = handlers[0]

        handler(msg)
      except KeyError:
        # A method for which a request was never sent, defer to the
        # interrupt handler.
        # TODO: Log unknown message.
        await self.interrupt(msg)
      except IndexError:
        # A request was sent at one point for this method, but all
        # of the handlers have either been consumed or timed out.
        # TODO: Log stray message.
        return