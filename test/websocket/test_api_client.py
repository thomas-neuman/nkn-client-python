import asyncio
import asynctest
from asynctest import CoroutineMock, MagicMock, Mock, patch
import json

from nkn_client.websocket.api_client import WebsocketApiClient
from nkn_client.websocket.api_request import (
    WebsocketApiRequest,
    WebsocketApiTimeoutException
)

class TestWebsocketApiClient(asynctest.TestCase):
  def setUp(self):
    self._client = WebsocketApiClient("url")

  def tearDown(self):
    pass

  async def test_json_parse_fails_interrupt(self):
    msg = "definitely_not_json"

    mock_interrupt = MagicMock()
    self._client.interrupt = mock_interrupt

    await self._client.recv(msg)

    mock_interrupt.assert_called_once_with(msg)

  async def test_unhandled_method_interrupt(self):
    msg = json.dumps({
      "Action": "unknown"
    })

    mock_interrupt = MagicMock()
    self._client.interrupt = mock_interrupt

    await self._client.recv(msg)

    mock_interrupt.assert_called_once_with(msg)

  @patch.object(nkn_client.websocket.api_client, "WebsocketApiRequest")
  async def test_call_rpc_successful_response(self, mock_api_req):
    method = "method"
    expected = {
      "Action": method
    }

    mock_req = MagicMock(WebsocketApiRequest)
    mock_request = CoroutineMock()
    mock_req.request = mock_request
    mock_response = CoroutineMock(side_effect=expected)
    mock_req.response = mock_response
    mock_api_req.return_value = mock_req

    actual = await self._client.call_rpc(method)

    mock_request.assert_awaited_once()
    mock_response.assert_awaited_once()
    self.assertEqual(actual, expected)

  @patch.object(nkn_client.websocket.api_client, "WebsocketApiRequest")
  async def test_recv_cleans_up_handler(self, mock_api_req):
    method = "method"
    expected = {
      "Action": method
    }

    mock_req = MagicMock(WebsocketApiRequest)
    mock_handle = MagicMock()
    mock_req.handle = mock_handle
    mock_req.request = CoroutineMock()
    mock_req.response = CoroutineMock(side_effect=expected)
    mock_api_req.return_value = mock_req

    req_task = asyncio.create_task(self._client.call_rpc(method))
    msg = json.dumps(expected)
    await self._client.recv(msg)
    actual = await req_task

    assert method not in self._client._handlers
    mock_handle.assert_called_once_with(expected)

  @patch.object(nkn_client.websocket.api_client, "WebsocketApiRequest")
  async def test_call_rpc_with_kwargs(self, mock_api_req):
    method = "method"
    kwargs = {"a": "b"}

    await self._client.call_rpc(method, **kwargs)
    mock_api_req.assert_called_once_with(method, **kwargs)

  @patch.object(nkn_client.websocket.api_client, "WebsocketApiRequest")
  async def test_call_rpc_timeout(self, mock_api_req):
    method = "method"

    mock_req = MagicMock(WebsocketApiRequest)
    mock_handle = MagicMock()
    mock_req.response = CoroutineMock(side_effect=WebsocketApiTimeoutException)
    mock_api_req.return_value = mock_req

    await self._client.call_rpc(method)

    assert method not in self._client._handlers