import asyncio
import threading
import websockets


# Utility function for coroutines
def finish(task):
  asyncio.get_event_loop().run_until_complete(task)


class WebSocketClient(object):
  def __init__(self, url):
    self._url = url
    self._ws = None

    # Manages intended connection state.
    self._running = False

    # Used to lock construction/destruction of WebSocket connection.
    self._lk = threading.Lock()

    # For outgoing messages.
    self._outbox = asyncio.Queue()

  def __del__(self):
    self.disconnect()

  def _main_loop(self):
    # Wraps the main handler in a non-coroutine way.
    while self._running:
      finish(self._handle())

  def connect(self):
    """
    Opens a connection to the WebSocket server, enabling the client to send
    and receive messages.
    """
    # Set the intended connection state and begin handling messages.
    self._running = True
    threading.Thread(target=self._main_loop).start()

  def disconnect(self):
    """
    Closes the connection to the WebSocket server.
    """
    # Modification to the connection must occur under the lock.
    with self._lk:
      if self._ws is not None:
        finish(self._ws.close())
        self._ws = None

      # Terminate the main loop, if it is running.
      self._running = False

  async def _handle_send(self):
    async for msg in self._outbox:
      await self._ws.send(msg)

  def send(self, msg):
    """
    Send a message to the server. The message is enqueued with other messages
    for this client, so it is not guaranteed to be sent immediately; it may
    not be sent at all if the connection is closed via 'disconnect'.

    Args:
      msg (str) : Message, as a string, to send to the server.
    """
    finish(self._outbox.put(msg))

  async def _handle_recv(self):
    async for msg in self._ws:
      self.recv(msg)

  def recv(self, msg):
    """
    Handle a newly received message from the server, which is passed in as
    the given string.

    To be implemented by subclasses. Must not raise any Exception.

    Args:
      msg (str) : Message, as a string, received from the server.
    """
    raise NotImplementedError

  async def _handle(self):
    # Set up the connection. Modification must occur under the lock.
    with self._lk:
      if self._ws is None:
        self._ws = await websockets.client.connect(self._url)

    # Wrap the handlers, to ensure they can be 'wait'ed on.
    send = asyncio.ensure_future(self._handle_send)
    recv = asyncio.ensure_future(self._handle_recv)

    done, pending = await asyncio.wait(
        send,
        recv,
        return_when=asyncio.FIRST_COMPLETED
    )

    # The handlers only return once the connecton is broken; therefore
    # tear down the attribute on the client.
    with self._lk:
      self._ws = None

    # Make sure no tasks linger.
    for fut in pending:
      fut.cancel()
