import asyncio
import asynctest
from asynctest import CoroutineMock, MagicMock, Mock, patch

from nkn_client.websocket.nkn_api import (
    NknWebsocketApiClient,
    NknWebsocketApiClientError
)


class TestNknWebsocketApiClient(asynctest.TestCase):
  def setUp(self):
    self._client = NknWebsocketApiClient()

  def tearDown(self):
    pass

  async def test_interrupt_receive_packet(self):
    action = "receivePacket"
    src = "src"
    payload = "payload"
    digest = "digest"

    msg = {
      "Action": action,
      "Src": src,
      "Payload": payload,
      "Digest": digest
    }

    mock_receive_packet = CoroutineMock()
    with patch(
        "nkn_client.websocket.nkn_api.NknWebsocketApiClient.receive_packet",
        new=mock_receive_packet
    ):
      client = NknWebsocketApiClient()
      await client.interrupt(msg)

      mock_receive_packet.assert_awaited_once()
      mock_receive_packet.assert_awaited_once_with(
        Action=action,
        Src=src,
        Payload=payload,
        Digest=digest
      )

  async def test_interrupt_update_sig_chain_block_hash(self):
    action = "updateSigChainBlockHash"
    error = 0
    desc = ""
    result = "result"
    version = "version"

    msg = {
      "Action": action,
      "Error": error,
      "Desc": desc,
      "Result": result,
      "Version": version
    }

    mock_update_sig_chain_block_hash = CoroutineMock()
    with patch(
        "nkn_client.websocket.nkn_api.NknWebsocketApiClient.update_sig_chain_block_hash",
        new=mock_update_sig_chain_block_hash
    ):
      client = NknWebsocketApiClient()
      await client.interrupt(msg)

      mock_update_sig_chain_block_hash.assert_awaited_once_with(
        Action=action,
        Error=error,
        Desc=desc,
        Result=result,
        Version=version
      )

  async def test_get_latest_block_height_success(self):
    expected = 660
    mock_call = CoroutineMock(return_value={
      "Action": "getlatestblockheight",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.get_latest_block_height()

    self.assertEqual(actual, expected)

  async def test_get_latest_block_height_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "getlatestblockheight",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.get_latest_block_height()

  async def test_get_block_by_height_success(self):
    expected = {
      "hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6",
      "header": "..."
    }
    mock_call = CoroutineMock(return_value={
      "Action": "getblock",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.get_block(height=1)

    self.assertEqual(actual, expected)

  async def test_get_block_by_height_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "getblock",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.get_block(height=1)

  async def test_get_block_by_hash_success(self):
    hash = "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    expected = {
      "hash": hash,
      "header": "..."
    }
    mock_call = CoroutineMock(return_value={
      "Action": "getblock",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.get_block(hash=hash)

    self.assertEqual(actual, expected)

  async def test_get_block_by_hash_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "getblock",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.get_block(hash="deadbeef")

  async def test_get_connection_count_success(self):
    expected = 3
    mock_call = CoroutineMock(return_value={
      "Action": "getconnectioncount",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.get_connection_count()

    self.assertEqual(actual, expected)

  async def test_get_connection_count_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "getconnectioncount",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.get_connection_count()

  async def test_get_transaction_success(self):
    expected = {
      "hash": "327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9",
      "inputs": "..."
    }
    mock_call = CoroutineMock(return_value={
      "Action": "gettransaction",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.get_transaction(
      "327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
    )

    self.assertEqual(actual, expected)

  async def test_get_transaction_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "gettransaction",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.get_transaction("deadbeef")

  async def test_heartbeat_success(self):
    expected = "5a232d0c-79ea-11e8-a7f5-6a00030e74b0"
    mock_call = CoroutineMock(return_value={
      "Action": "heartbeat",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.heartbeat()

    self.assertEqual(actual, expected)

  async def test_heartbeat_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "heartbeat",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.heartbeat()

  async def test_get_session_count_success(self):
    expected = 1
    mock_call = CoroutineMock(return_value={
      "Action": "getsessioncount",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.get_session_count("127.0.0.1:30002")

    self.assertEqual(actual, expected)

  async def test_get_session_count_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "getsessioncount",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.get_session_count("127.0.0.1:30002")

  async def test_set_client_success(self):
    expected = None
    mock_call = CoroutineMock(return_value={
      "Action": "setclient",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.set_client("anything.pubkey")

    self.assertEqual(actual, expected)

  async def test_set_client_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "setClient",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.set_client("anything.pubkey")

  async def test_send_packet_success(self):
    expected = None
    mock_call = CoroutineMock(return_value={
      "Action": "sendPacket",
      "Error": 0,
      "Desc": "SUCCESS",
      "Result": expected,
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    actual = await self._client.send_packet(
        "nkn.address",
        "message",
        "signature"
    )

    self.assertEqual(actual, expected)

  async def test_send_packet_error(self):
    mock_call = CoroutineMock(return_value={
      "Action": "sendPacket",
      "Error": 41002,
      "Desc": "SERVICE CEILING",
      "Result": "result",
      "Version": "1.0.0"
    })
    self._client.call_rpc = mock_call

    with self.assertRaises(NknWebsocketApiClientError):
      _ = await self._client.send_packet("nkn.address", "message", "sig")

  async def test_get_incoming_packet(self):
    Action = "receivePacket"
    Src = "source"
    Payload = "payload"
    Digest = "digest"

    await self._client.receive_packet(
        Action=Action,
        Src=Src,
        Payload=Payload,
        Digest=Digest
    )

    asrc, apayload, adigest = await self._client.get_incoming_packet()

    self.assertEqual(asrc, Src)
    self.assertEqual(apayload, Payload)
    self.assertEqual(adigest, Digest)

  async def test_sig_chain_block_hash(self):
    Action = "updateSigChainBlockHash"
    Error = 0
    Desc = ""
    Result = "result"
    Version = "version"

    await self._client.update_sig_chain_block_hash(
        Action=Action,
        Error=Error,
        Desc=Desc,
        Result=Result,
        Version=Version
    )

    actual = self._client.sig_chain_block_hash

    self.assertEqual(actual, Result)