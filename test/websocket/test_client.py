import asyncio
import asynctest
from asynctest import CoroutineMock, MagicMock, Mock, patch, return_once
import threading
from time import sleep
import websockets
from websockets.exceptions import ConnectionClosed

import nkn_client.websocket.client as mod
from nkn_client.websocket.client import (
  WebsocketClient,
  WebsocketClientException
)


class TestWebsocketClient(asynctest.TestCase):
  def mockThreads(self):
    class MockThread(object):
      def __init__(self, target=lambda: None):
        self._target = target

      def start(self):
        self._target()
    self.thread_patcher = patch.object(threading, "Thread", new=MockThread)
    mod = self.thread_patcher.start()

  def unmockThreads(self):
    if not self.thread_patcher:
      return
    self.thread_patcher.stop()
    self.thread_patcher = None

  def setUp(self):
    self.client = WebsocketClient("ws://url")
    self.client.recv = lambda msg: msg
    self.mockThreads()

  def tearDown(self):
    self.client = None
    self.unmockThreads()

  @patch("websockets.client")
  def test_connect_opens_connection(self, mock_ws):
    mock_connection = CoroutineMock()
    mock_connection.close = CoroutineMock()
    mock_connect = CoroutineMock(return_value=mock_connection)
    mock_ws.connect = mock_connect

    step_one = threading.BoundedSemaphore()
    step_two = threading.BoundedSemaphore()

    def disconnect():
      with step_two:
        with step_one:
          sleep(2)
          self.client.disconnect()

    self.unmockThreads()
    threading.Thread(target=disconnect).start()
    self.mockThreads()

    with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
      mock_wait.return_value = [ [ "OK" ], [ ] ]
      self.client.connect()

    mock_connect.assert_awaited()

  def test_disconnect_before_connect_succeeds(self):
    # No errors raised.
    self.client.disconnect()

  @patch("websockets.client")
  def test_disconnect_after_connect_succeeds(self, mock_ws):
    mock_connection = CoroutineMock()
    mock_connection.close = CoroutineMock()
    mock_connect = CoroutineMock(return_value=mock_connection)
    mock_ws.connect = mock_connect

    # Run in threaded mode, reflecting real usage.
    self.unmockThreads()

    with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
      mock_wait.return_value = [ [ "OK" ], [ ] ]
      self.client.connect()

    self.client.disconnect()

  @patch("asyncio.Queue")
  @patch("websockets.client")
  def test_send_one_succeeds(self, mock_ws, mock_queue):
    mock_connection = CoroutineMock()
    mock_connection.close = CoroutineMock()
    mock_connection.send = CoroutineMock(return_value="OK")
    mock_connect = CoroutineMock(return_value=mock_connection)
    mock_ws.connect = mock_connect

    mock_queue_obj = MagicMock()
    mock_queue_obj.put = CoroutineMock()
    mock_queue.return_value = mock_queue_obj

    step_one = threading.BoundedSemaphore()
    step_two = threading.BoundedSemaphore()

    def disconnect():
      with step_two:
        with step_one:
          self.client.send("message")
          self.client.disconnect()

    # Run in threaded mode, reflecting real usage.
    self.unmockThreads()
    threading.Thread(target=disconnect).start()
    self.mockThreads()

    # Do connect, then allow next step to proceed.
    with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
      mock_wait.return_value = [ [ "OK" ], [ ] ]
      self.client.connect()

    mock_queue_obj.put.assert_awaited()

  @patch("asyncio.Queue")
  @patch("websockets.client")
  def test_send_many_succeeds(self, mock_ws, mock_queue):
    mock_connection = CoroutineMock()
    mock_connection.close = CoroutineMock()
    mock_connection.send = CoroutineMock(side_effect=["OK", "OK"])
    mock_connect = CoroutineMock(return_value=mock_connection)
    mock_ws.connect = mock_connect

    mock_queue_obj = MagicMock()
    mock_queue_obj.put = CoroutineMock()
    mock_queue.return_value = mock_queue_obj

    step_one = threading.BoundedSemaphore()
    step_two = threading.BoundedSemaphore()

    def disconnect():
      with step_two:
        with step_one:
          self.client.send("message")
          self.client.send("next")
          self.client.disconnect()

    # Run in threaded mode, reflecting real usage.
    self.unmockThreads()
    threading.Thread(target=disconnect).start()
    self.mockThreads()

    # Do connect, then allow next step to proceed.
    with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
      mock_wait.return_value = [ [ "OK" ], [ ] ]
      self.client.connect()

    mock_queue_obj.put.assert_awaited()

  def test_send_after_disconnect_fails(self):
    self.client.disconnect()
    with self.assertRaises(WebsocketClientException):
      self.client.send("message")


if __name__ == "__main__":
  unittest.main()