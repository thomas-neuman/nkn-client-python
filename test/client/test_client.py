import asyncio
import asynctest
from asynctest import ANY, CoroutineMock, MagicMock, Mock, patch

from nkn_client.client.client import NknClient
from nkn_client.proto.packet_pb2 import *

class TestNknClient(asynctest.TestCase):
  def setUp(self):
    self._client = NknClient("id")

  def tearDown(self):
    pass

  async def test_connect(self):
    wsaddr = "host"

    mock_jsonrpc = MagicMock()
    mock_getwsaddr = MagicMock(return_value=wsaddr)
    mock_jsonrpc.get_websocket_address = mock_getwsaddr
    self._client._jsonrpc = mock_jsonrpc

    mock_ready = asyncio.Event()
    mock_unready = asyncio.Event()
    mock_unready.set()

    def ready():
      mock_unready.clear()
      mock_ready.set()
    def unready():
      mock_ready.clear()
      mock_unready.set()

    mock_connect = CoroutineMock(side_effect=lambda _: ready())
    mock_disconnect = CoroutineMock(side_effect=lambda: unready())

    mock_ws = MagicMock()
    mock_ws.ready = mock_ready
    mock_ws.unready = mock_unready
    mock_ws.connect = mock_connect
    mock_ws.disconnect = mock_disconnect
    self._client._ws = mock_ws

    await self._client.connect()

    print("Connected!")
    await self._client.disconnect()

    mock_getwsaddr.assert_called_once()
    mock_connect.assert_awaited_once_with(wsaddr)

  async def test_disconnect(self):
    mock_ws = MagicMock()
    mock_disconnect = CoroutineMock()
    mock_ws.disconnect = mock_disconnect
    self._client._ws = mock_ws

    await self._client.disconnect()

    mock_disconnect.assert_awaited_once()

  async def test_send(self):
    mock_ws = MagicMock()
    mock_send = CoroutineMock()
    mock_ws.send_packet = mock_send
    self._client._ws = mock_ws

    dest = "dest"
    payload = "payload"
    real_payload = payload.encode("utf-8")

    pkt = OutboundPacket()
    pkt.dest = dest
    pkt.payload = real_payload

    await self._client.send(dest, payload)

    mock_send.assert_awaited_once_with(pkt)

  async def test_recv(self):
    src = "src"
    payload = "payload".encode("utf-8")

    expected = InboundPacket()
    expected.src = src
    expected.payload = payload

    mock_ws = MagicMock()
    mock_recv = CoroutineMock(return_value=expected)
    mock_ws.get_incoming_packet = mock_recv
    self._client._ws = mock_ws

    actual = await self._client.recv()

    self.assertEqual(actual, expected)