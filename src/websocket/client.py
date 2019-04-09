import asyncio
from concurrent.futures import CancelledError
import threading
import websockets


class WebsocketClientException(Exception):
  pass

class WebsocketSessionShutdownException(Exception):
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
  def __init__(self, url):
    self._url = url
    self._ws = None

    # Manages intended connection state.
    self._running = False

    # Used to lock construction/destruction of WebSocket connection.
    self._lk = threading.Lock()

    # The future which loops forever, handling send/recv events.
    self._main_task = None

    # For outgoing messages. Set up with a Queue when the main loop begins.
    self._outbox = None

  def __del__(self):
    self.disconnect()

  def connect(self):
    """
    Opens a connection to the WebSocket server, enabling the client to send
    and receive messages.
    """
    def _start():
      asyncio.run(self._main_loop())

    with self._lk:
      if self._running:
        return
      self._running = True
    threading.Thread(target=_start).start()

  def disconnect(self):
    """
    Closes the connection to the WebSocket server.
    """
    async def func():
      with self._lk:
        # Terminate the main loop, if it is running.
        self._running = False

        # Close the underlying connection.
        if self._ws is not None:
          await self._ws.close()

    asyncio.run(func())

  def send(self, msg):
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
    with self._lk:
      if not self._running:
        raise WebsocketClientException("Client is not connected!")
      asyncio.run(self._outbox.put(msg))

  def recv(self, msg):
    """
    Handle a newly received message from the server, which is passed in as
    the given string.

    To be implemented by subclasses. Must not raise any Exception.

    Args:
     msg (str) : Message, as a string, received from the server.
    """
    pass

  def _create_send_queue(self):
    with self._lk:
      self._outbox = asyncio.Queue()

  def _destroy_send_queue(self):
    with self._lk:
      self._outbox = None

  async def _create_connection(self):
    # Modification must occur under the lock.
    with self._lk:
      assert self._ws is None
      self._ws = await websockets.client.connect(self._url)

  async def _destroy_connection(self):
    # Modification must occur under the lock.
    with self._lk:
      assert self._ws is not None
      self._ws = None

  async def _handle_send(self):
    while True:
      msg = None
      try:
        msg = await self._outbox.get()
      except AttributeError:
        return
      await self._ws.send(msg)

  async def _handle_recv(self):
    while True:
      msg = None
      try:
        msg = await self._ws.recv()
      except AttributeError:
        return
      self.recv(msg)

  async def _send_recv_until_closed(self):
    # Wrap the handlers, to ensure they can be 'wait'ed on.
    send = asyncio.ensure_future(self._handle_send())
    recv = asyncio.ensure_future(self._handle_recv())

    _, pending = await asyncio.wait(
        [send, recv],
        return_when=asyncio.FIRST_COMPLETED
    )

    return pending

  async def _reap_tasks(self, pending):
    for task in pending:
      task.cancel()
      await task

  async def _main_loop(self):
    """
    The main loop which houses the client logic for handling send/recv events.
    Run as a coroutine which establishes, destroys, and re-establishes the
    underlying websocket connection based on the current state of the caller's
    intent.
    """
    # Construct the queue for storing messages to be sent.
    # This must be done in the same async event loop as it is
    # used in.
    self._create_send_queue()

    with self._lk:
      running = self._running

    while running:
      # Set up the connection.
      await self._create_connection()

      # Handle send/recv events.
      pending = await self._send_recv_until_closed()

      # Reap any lingering tasks.
      try:
        await self._reap_tasks(pending)
      except CancelledError:
        pass

      # Tear down the connection on the client.
      await self._destroy_connection()

      with self._lk:
        running = self._running

    # Tear down the queue after the loop has terminated.
    self._destroy_send_queue()