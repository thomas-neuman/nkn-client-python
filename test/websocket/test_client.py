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

    def disconnect():
      sleep(1)
      self.client.disconnect()
    self.unmockThreads()
    threading.Thread(target=disconnect).start()
    self.mockThreads()

    with patch("asyncio.gather", new=CoroutineMock()) as mock_gather:
      mock_gather.return_value = "OK"
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

    with patch("asyncio.gather", new=CoroutineMock()) as mock_gather:
      mock_gather.return_value = "OK"
      self.client.connect()

    self.client.disconnect()

  def test_send_one_succeeds(self):
    pass

  def test_send_many_succeeds(self):
    pass

  def test_send_fails(self):
    pass

  def test_send_after_disconnect_fails(self):
    self.client.disconnect()
    with self.assertRaises(WebsocketClientException):
      self.client.send("message")


if __name__ == "__main__":
  unittest.main()