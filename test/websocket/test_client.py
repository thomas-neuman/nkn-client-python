import asyncio
import asynctest
from asynctest import CoroutineMock, MagicMock, patch
import threading
import websockets
from websockets.exceptions import ConnectionClosed

import nkn_client.websocket.client as mod
from nkn_client.websocket.client import (
  WebsocketClient,
  WebsocketClientException
)


class MockWebsocketsConnection(object):
  def __init__(self):
    self._running = True
    self.send = CoroutineMock()

  async def close(self):
    self._running = False

  async def recv(self):
    if not self._running:
      raise ConnectionClosed(1, "str")
    val = MagicMock()
    val.result = MagicMock(return_value="OK")
    return val

class MockAsyncioQueue(object):
  def __init__(self):
    self.put = CoroutineMock()
    self.get = CoroutineMock()

class TestWebsocketClient(asynctest.TestCase):
  def setUp(self):
    self.client = WebsocketClient("ws://url")
    self.client.recv = lambda msg: msg

  def tearDown(self):
    self.client = None

  @patch("websockets.client")
  def test_connect_opens_connection(self, mock_ws):
    mock_ws.connect = mock_connect = CoroutineMock(
        return_value=MockWebsocketsConnection()
    )

    self.client.connect()
    self.client.disconnect()

    mock_connect.assert_awaited()

  def test_disconnect_before_connect_succeeds(self):
    # No errors raised.
    self.client.disconnect()

  @patch("websockets.client")
  def test_disconnect_after_connect_succeeds(self, mock_ws):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())

    self.client.connect()
    self.client.disconnect()

  @patch("asyncio.Queue")
  @patch("websockets.client")
  def test_send_one_succeeds(self, mock_ws, mock_queue):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())
    mock_queue.return_value = mock_queue_obj = MockAsyncioQueue()

    self.client.connect()
    self.client.send("message")
    self.client.disconnect()

    mock_queue_obj.put.assert_awaited()

  @patch("asyncio.Queue")
  @patch("websockets.client")
  def test_send_many_succeeds(self, mock_ws, mock_queue):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())
    mock_queue.return_value = mock_queue_obj = MockAsyncioQueue()

    self.client.connect()
    self.client.send("message")
    self.client.send("next")
    self.client.disconnect()

    mock_queue_obj.put.assert_awaited()

  def test_send_after_disconnect_fails(self):
    self.client.disconnect()
    with self.assertRaises(WebsocketClientException):
      self.client.send("message")


if __name__ == "__main__":
  unittest.main()