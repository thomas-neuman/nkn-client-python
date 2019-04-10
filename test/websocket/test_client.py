import asyncio
import asynctest
from asynctest import CoroutineMock, patch
import threading
import websockets

import nkn_client.websocket.client as mod
from nkn_client.websocket.client import (
  WebsocketClient,
  WebsocketClientException
)

class MockWebsocketsConnection(object):
  def __init__(self):
    self.send = CoroutineMock()
    self.recv = CoroutineMock()
    self.close = CoroutineMock()

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

    step_one = threading.BoundedSemaphore()
    step_two = threading.BoundedSemaphore()

    def disconnect():
      with step_two:
        with step_one:
          self.client.disconnect()

    with step_one:
      threading.Thread(target=disconnect).start()

      with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
        mock_wait.return_value = [ [ "OK" ], [ ] ]
        self.client.connect()

    with step_two:
      mock_connect.assert_awaited()

  def test_disconnect_before_connect_succeeds(self):
    # No errors raised.
    self.client.disconnect()

  @patch("websockets.client")
  def test_disconnect_after_connect_succeeds(self, mock_ws):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())

    with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
      mock_wait.return_value = [ [ "OK" ], [ ] ]
      self.client.connect()

    self.client.disconnect()

  @patch("asyncio.Queue")
  @patch("websockets.client")
  def test_send_one_succeeds(self, mock_ws, mock_queue):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())
    mock_queue.return_value = mock_queue_obj = MockAsyncioQueue()

    step_one = threading.BoundedSemaphore()
    step_two = threading.BoundedSemaphore()
    step_three = threading.BoundedSemaphore()

    def send_and_disconnect():
      with step_two:
        with step_one:
          self.client.send("message")
        with step_three:
          self.client.disconnect()

    with step_three:
      with step_one:
        threading.Thread(target=send_and_disconnect).start()

        # Do connect, then allow next step to proceed.
        with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
          mock_wait.return_value = [ [ "OK" ], [ ] ]
          self.client.connect()

    with step_two:
      mock_queue_obj.put.assert_awaited()

  @patch("asyncio.Queue")
  @patch("websockets.client")
  def test_send_many_succeeds(self, mock_ws, mock_queue):
    mock_ws.connect = CoroutineMock(return_value=MockWebsocketsConnection())
    mock_queue.return_value = mock_queue_obj = MockAsyncioQueue()

    step_one = threading.BoundedSemaphore()
    step_two = threading.BoundedSemaphore()
    step_three = threading.BoundedSemaphore()

    def send_and_disconnect():
      with step_two:
        with step_one:
          self.client.send("message")
          self.client.send("next")
        with step_three:
          self.client.disconnect()

    with step_three:
      with step_one:
        threading.Thread(target=send_and_disconnect).start()

        # Do connect, then allow next step to proceed.
        with patch("asyncio.wait", new=CoroutineMock()) as mock_wait:
          mock_wait.return_value = [ [ "OK" ], [ ] ]
          self.client.connect()

    with step_two:
      mock_queue_obj.put.assert_awaited()

  def test_send_after_disconnect_fails(self):
    self.client.disconnect()
    with self.assertRaises(WebsocketClientException):
      self.client.send("message")


if __name__ == "__main__":
  unittest.main()