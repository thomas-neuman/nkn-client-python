import asyncio
import json


class WebsocketApiTimeoutException(Exception):
  pass

class WebsocketApiRequest(object):
  """
  Represents an API request to be submitted over the Websockets
  connection. Enables the initial request to be logically
  associated with its response, and thereby pick up its result.

  Args:
    client (WebsocketApiClient) : The client through which the request
                                  will be submitted.
    method (str)                : The API method to invoke.
    kwargs                      : Each keyword argument is submitted
                                  as a key-value pair in the parameters
                                  of the API call.
  """
  def __init__(self, client, method, **kwargs):
    self._client = client

    self._method = method
    self._params = kwargs

    # Set when the response is received.
    self._done = asyncio.Event()

    # Retains the result.
    self._res = None
  
  def handle(self, msg):
    """
    Handles an API response.

    Args:
      msg (dict)  : Response, as parsed from JSON.
    """
    self._res = msg
    self._done.set()

  async def request(self):
    """
    Submit the request via the client.
    """
    self._done.clear()

    msg = {
      "Action": self._method
    }
    if self._params is not None:
      msg.update(self._params)

    msg = json.dumps(msg)

    await self._client.send(msg)
  
  async def response(self, timeout=None):
    """
    Returns the response, when ready. If the 'timeout' argument is
    not None, then an exception is raised instead of producing a
    result, if no appropriate response is received within the given
    timeout.

    Args:
      timeout                       : Time to await the response, in
                                      seconds. Wait forever if None.
    Returns:
      dict                          : The API response.
    Raises:
      WebsocketApiTimeoutException  : If the request timed out.
    """
    try:
      await asyncio.wait_for(self._done.wait(), timeout)
      return self._res
    except asyncio.TimeoutError:
      raise WebsocketApiTimeoutException()