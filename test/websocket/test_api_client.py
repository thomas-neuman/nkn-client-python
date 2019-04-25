import asyncio
import asynctest
from asynctest import CoroutineMock, MagicMock, Mock, patch
import json

from nkn_client.websocket.api_client import WebsocketApiClient

class TestWebsocketApiClient(asynctest.TestCase):
  def setUp(self):
    self._client = WebsocketApiClient()

  def tearDown(self):
    pass

  async def test_json_parse_fails_interrupt(self):
    msg = "definitely_not_json"

    mock_interrupt = CoroutineMock()
    self._client.interrupt = mock_interrupt

    await self._client.recv(msg)

    mock_interrupt.assert_awaited_once_with(msg)

  async def test_unhandled_method_interrupt(self):
    expected = {
      "Action": "unknown"
    }
    msg = json.dumps(expected)

    mock_interrupt = CoroutineMock()
    self._client.interrupt = mock_interrupt

    await self._client.recv(msg)

    mock_interrupt.assert_awaited_once_with(expected)

  async def test_call_rpc_successful_response(self):
    method = "method"
    expected = {
      "Action": method
    }

    mock_send = CoroutineMock()
    self._client.send = mock_send

    mock_wait = CoroutineMock()
    asyncio.wait_for = mock_wait

    await self._client.call_rpc(method)

    mock_send.assert_awaited()

    handlers = self._client._handlers
    self.assertIn(method, handlers)
    self.assertFalse(handlers[method])

  async def test_call_rpc_with_kwargs(self):
    method = "method"
    kwargs = {"a": "b"}

    expected = json.dumps({
      "Action": method,
      "a": "b"
    })

    mock_send = CoroutineMock()
    self._client.send = mock_send

    call_task = self._client.call_rpc(method, **kwargs)
    await self._client.recv(expected)
    await call_task

    mock_send.assert_awaited_with(expected)

  async def test_call_rpc_timeout(self):
    asyncio.wait_for = CoroutineMock(side_effect=asyncio.TimeoutError)
    method = "method"

    mock_send = CoroutineMock()
    self._client.send = mock_send

    await self._client.call_rpc(method)

    handlers = self._client._handlers
    self.assertIn(method, handlers)
    self.assertFalse(handlers[method])