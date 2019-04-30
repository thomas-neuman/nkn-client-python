import asyncio
from concurrent.futures import CancelledError
import logging
import sys
import websockets
from websockets.exceptions import ConnectionClosed

log = logging.getLogger(__name__)


class WebsocketClientException(Exception):
  pass

class WebsocketClient(object):
  """
  Client class for interacting with a Websocket server. Handles the connect
  and disconnect logic, re-opening the connection as necessary until the
  caller explicitly tears it down. Able to send and receive messages
  asynchronously; the handler for received messages must be implemented by a
  subclass.

  Args:
    url (str) : The remote server to communicate with.
  """
  def __init__(self):
    # Tracks the main loop execution.
    self._task = None

    # The underlying connection.
    self._socket = None

    # Tracks when the connection is actually open.
    self._ready = asyncio.Event()

    # Manages intended connection state.
    self._running = False

  async def connect(self, hostname):
    """
    Opens a connection to the WebSocket server, enabling the client to send
    and receive messages.
    """
    url = "ws://%s" % hostname
    self._task = asyncio.create_task(self._main_loop(url))

    await self._ready.wait()

  async def disconnect(self):
    """
    Closes the connection to the WebSocket server.
    """
    # Terminate the main loop, if it is running.
    self._running = False

    # Close the underlying connection.
    if self._socket is not None:
      await self._socket.wait_closed()

      await self._task
      self._task = None

  async def send(self, msg):
    """
    Send a message to the server. The message is enqueued with other messages
    for this client, so it is not guaranteed to be sent immediately; it may
    not be sent at all if the connection is closed via 'disconnect'. If the
    client requests a message be sent before connecting, an error is raised.

    Args:
      msg (str)                 : Message, as a string, to send to the server.
    Raises:
      WebsocketClientException  : If the client is not connected.
    """
    if not self._running:
      raise WebsocketClientException("Client is not connected!")
    await self._ready.wait()
    await self._socket.send(msg)

  async def recv(self, msg):
    """
    Handle a newly received message from the server, which is passed in as
    the given string.

    To be implemented by subclasses. Must not raise any Exception.

    Args:
     msg (str) : Message, as a string, received from the server.
    """
    pass

  async def _main_loop(self, url):
    """
    The main loop which houses the client logic for handling send/recv events.
    Run as a coroutine which establishes, destroys, and re-establishes the
    underlying websocket connection based on the current state of the caller's
    intent.

    Args:
      url (str)             : URL to connect to.
    """
    log.debug("Connect requested to %s" % (url))
    if self._running:
      return
    self._running = True

    while self._running:
      # Set up the connection.
      self._socket = await websockets.client.connect(url, ping_interval=None)

      log.debug("Socket setup: %s" % (self._socket))

      self._ready.set()

      try:
        while True:
          msg = await self._socket.recv()
          log.debug("Received message: %s" % (msg))
          await self.recv(msg)
      except ConnectionClosed:
        log.debug("Websocket connection closed.")
        pass

      log.debug("Reopen connection? %s" % (str(self._running)))
      self._ready.clear()

    self._socket = None