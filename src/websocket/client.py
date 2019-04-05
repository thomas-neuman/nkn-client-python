import asyncio
import threading
import websockets


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
  def __init__(self, url):
    self._url = url
    self._ws = None

    # Manages intended connection state.
    self._running = False

    # Used to lock construction/destruction of WebSocket connection.
    self._lk = threading.Lock()

    # For outgoing messages. Set up with a Queue when the main loop begins.
    self._outbox = None

  def __del__(self):
    self.disconnect()

  def _main_loop(self):
    # Wraps the main handler in a non-coroutine way.
    async def loop():
      self._outbox = asyncio.Queue()
      running = True
      while running:
        await self._handle()
        with self._lk:
          running = self._running

    asyncio.run(loop())

  def connect(self):
    """
    Opens a connection to the WebSocket server, enabling the client to send
    and receive messages.
    """
    # Set the intended connection state and begin handling messages.
    with self._lk:
      self._running = True
    threading.Thread(target=self._main_loop).start()

  def disconnect(self):
    """
    Closes the connection to the WebSocket server.
    """
    # Modification to the connection must occur under the lock.
    with self._lk:
      # Terminate the main loop, if it is running.
      self._running = False

      if self._ws is not None:
        asyncio.run(self._ws.close())
        self._ws = None

  async def _handle_send(self):
    msg = await self._outbox.get()
    await self._ws.send(msg)

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

  async def _handle_recv(self):
    msg = await self._ws.recv()
    self.recv(msg)

  def recv(self, msg):
    """
    Handle a newly received message from the server, which is passed in as
    the given string.

    To be implemented by subclasses. Must not raise any Exception.

    Args:
     msg (str) : Message, as a string, received from the server.
    """
    pass

  async def _handle(self):
    # Set up the connection. Modification must occur under the lock.
    with self._lk:
      if self._ws is None:
        self._ws = await websockets.client.connect(self._url)

    # Wrap the handlers, to ensure they can be 'wait'ed on.
    send = asyncio.ensure_future(self._handle_send())
    recv = asyncio.ensure_future(self._handle_recv())

    try:
      futures = await asyncio.gather(
          send,
          recv,
          return_exceptions=False
      )
    finally:
      # Reap any lingering tasks.
      send.cancel()
      recv.cancel()

      # The handlers only return once the connection is broken; therefore
      # tear down the attribute on the client.
      with self._lk:
        self._ws = None