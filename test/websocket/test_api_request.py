import asyncio
import asynctest
from asynctest import CoroutineMock, Mock
import json

from nkn_client.websocket.api_request import (
  WebsocketApiRequest,
  WebsocketApiTimeoutException
)
from nkn_client.websocket.client import WebsocketClient


class TestWebsocketApiRequest(asynctest.TestCase):
  def setUp(self):
    self._client = Mock(WebsocketClient)

  async def test_request_submits_message(self):
    mock_send = CoroutineMock()
    self._client.send = mock_send

    req = WebsocketApiRequest(self._client, "method")
    await req.request()

    mock_send.assert_awaited_once()

  async def test_request_with_params(self):
    mock_send = CoroutineMock()
    self._client.send = mock_send

    method = "method"
    params = {"a": "b"}
    expected = json.dumps({
      "Action": method,
      "a": "b"
    })

    req = WebsocketApiRequest(self._client, method, **params)
    await req.request()

    mock_send.assert_awaited_with(expected)

  async def test_response_returns_handled_message(self):
    req = WebsocketApiRequest(self._client, "method")

    msg = "message"
    req.handle(msg)

    res = await req.response()

    self.assertEqual(res, msg)

  async def test_response_times_out(self):
    req = WebsocketApiRequest(self._client, "method")

    with self.assertRaises(WebsocketApiTimeoutException):
      res = await req.response(timeout=1)