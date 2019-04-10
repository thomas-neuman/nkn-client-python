import asyncio
import asynctest
from asynctest import CoroutineMock, MagicMock, Mock, patch
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
    real_queue = asyncio.Queue()
    self.put = CoroutineMock(wraps=real_queue.put)
    self.get = real_queue.get

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

  @patch("asyncio.Queue", return_value=MockAsyncioQueue())
  @patch("websockets.client")
  def test_send_one_succeeds(self, mock_ws, mock_queue):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())
    mock_put = mock_queue.return_value.put

    self.client.connect()

    self.client.send("message")
    mock_put.assert_awaited()

    self.client.disconnect()

  @patch("asyncio.Queue", return_value=MockAsyncioQueue())
  @patch("websockets.client")
  def test_send_many_succeeds(self, mock_ws, mock_queue):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())
    mock_put = mock_queue.return_value.put

    self.client.connect()

    self.client.send("message")
    mock_put.assert_awaited()
    mock_put.reset_mock()

    self.client.send("next")
    mock_put.assert_awaited()
    mock_put.reset_mock()

    self.client.disconnect()

  def test_send_after_disconnect_fails(self):
    self.client.disconnect()
    with self.assertRaises(WebsocketClientException):
      self.client.send("message")


if __name__ == "__main__":
  unittest.main()