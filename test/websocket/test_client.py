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
    self.recv = CoroutineMock(side_effect=self._recv)
    self.wait_closed = CoroutineMock(side_effect=self._close)
    self.close = CoroutineMock(side_effect=self._close)
    self.__aiter__ = self.recv

  def _close(self):
    self._running = False

  async def _recv(self):
    if not self._running:
      raise ConnectionClosed(1, "str")
    val = MagicMock()
    val.result = MagicMock(return_value="OK")
    return val

class TestWebsocketClient(asynctest.TestCase):
  def setUp(self):
    self.client = WebsocketClient("ws://url")
    self.client.recv = CoroutineMock(side_effect=ConnectionClosed(1, "reason"))

  def tearDown(self):
    self.client = None

  @patch("websockets.client")
  async def test_connect_opens_connection(self, mock_ws):
    mock_ws.connect = mock_connect = CoroutineMock(
        return_value=MockWebsocketsConnection()
    )

    await self.client.connect()
    await self.client.disconnect()

    mock_connect.assert_awaited()

  async def test_disconnect_before_connect_succeeds(self):
    # No errors raised.
    await self.client.disconnect()

  @patch("websockets.client")
  async def test_disconnect_after_connect_succeeds(self, mock_ws):
    connection = MockWebsocketsConnection()
    mock_ws.connect = CoroutineMock(return_value=connection)

    await self.client.connect()
    await self.client.disconnect()

    connection.wait_closed.assert_awaited()

  @patch("websockets.client")
  async def test_send_one_succeeds(self, mock_ws):
    connection = MockWebsocketsConnection()
    mock_ws.connect = CoroutineMock(return_value=connection)
    mock_send = connection.send

    await self.client.connect()

    await self.client.send("message")
    mock_send.assert_awaited()

    await self.client.disconnect()

  @patch("websockets.client")
  async def test_send_many_succeeds(self, mock_ws):
    connection = MockWebsocketsConnection()
    mock_ws.connect = CoroutineMock(return_value=connection)
    mock_send = connection.send

    await self.client.connect()

    await self.client.send("message")
    mock_send.assert_awaited()
    mock_send.reset_mock()

    await self.client.send("next")
    mock_send.assert_awaited()
    mock_send.reset_mock()

    await self.client.disconnect()

  async def test_send_after_disconnect_fails(self):
    await self.client.disconnect()
    with self.assertRaises(WebsocketClientException):
      await self.client.send("message")


if __name__ == "__main__":
  unittest.main()