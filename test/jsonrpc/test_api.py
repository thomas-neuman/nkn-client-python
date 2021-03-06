import functools
import json
import responses
import unittest

import nkn_client.jsonrpc.api


class TestNknJsonRpcApi(unittest.TestCase):
  def setUp(self):
    self._host = "hostname"
    self._api = nkn_client.jsonrpc.api.NknJsonRpcApi(self._host)

  @responses.activate
  def _with_rpc_response(self, method, resp_cb):
    responses.add_callback(
        responses.POST,
        "http://%s/" % (self._host),
        callback=resp_cb
    )
    return method()

  def _with_success_response(self, method, expected_result):
    expected_json = {
      "jsonpc": "2.0",
      "result": expected_result,
      "id": 1
    }
    expected_status = 200

    def resp_callback(request):
      req_body = json.loads(request.body)
      resp_body = expected_json.copy()
      resp_body.update({"id": req_body["id"]})

      return (expected_status, {}, json.dumps(resp_body))

    return self._with_rpc_response(method, resp_callback)

  def _with_wrong_id_response(self, method, expected_result):
    expected_json = {
      "jsonpc": "2.0",
      "result": expected_result,
      "id": 1
    }
    expected_status = 200

    def resp_callback(request):
      req_body = json.loads(request.body)
      resp_body = expected_json.copy()
      resp_id = "BAD:%s" % (req_body["id"])
      resp_body.update({"id": resp_id})

      return (expected_status, {}, json.dumps(resp_body))

    return self._with_rpc_response(method, resp_callback)

  def _with_wrong_result_response(self, method, unexpected_result):
    pass


  def test_get_latest_block_height_succeeds(self):
    method = self._api.get_latest_block_height
    expected = 5

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_latest_block_height_fails_with_wrong_id(self):
    method = self._api.get_latest_block_height
    expected = 5

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_latest_block_hash_succeeds(self):
    method = self._api.get_latest_block_hash
    expected = "6cf00422b02f3d99f5c006fcdb36bfb7cc8b2c345b2f34274e50a3d8f3bb8193"

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_latest_block_hash_fails_with_wrong_id(self):
    method = self._api.get_latest_block_hash
    expected = "6cf00422b02f3d99f5c006fcdb36bfb7cc8b2c345b2f34274e50a3d8f3bb8193"

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_block_count_succeeds(self):
    method = self._api.get_block_count
    expected = 270

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_block_count_fails_with_wrong_id(self):
    method = self._api.get_block_count
    expected = 270

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_block_with_height_param_fails_with_wrong_id(self):
    method = functools.partial(self._api.get_block, height=1)
    expected = {
      "hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    }

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_block_with_height_param_succeeds(self):
    method = functools.partial(self._api.get_block, height=1)
    expected = {
      "hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    }

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_block_with_hash_param_fails_with_wrong_id(self):
    method = functools.partial(
      self._api.get_block,
      hash="5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    )
    expected = {
      "hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    }

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_block_with_hash_param_succeeds(self):
    method = functools.partial(
      self._api.get_block,
      hash="5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    )
    expected = {
      "hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6"
    }

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_block_transactions_by_height_fails_with_wrong_id(self):
    method = functools.partial(
      self._api.get_block_transactions_by_height,
      1
    )
    expected = {
			"Hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6",
			"Height": 1,
			"Transactions": [
				"327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
			]
		}

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_block_transactions_by_height_succeeds(self):
    method = functools.partial(
      self._api.get_block_transactions_by_height,
      1
    )
    expected = {
			"Hash": "5f85d1286801c2f1129a02b0b19a3312f8113aaa073b5987346c59e27a12bdc6",
			"Height": 1,
			"Transactions": [
				"327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
			]
		}

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_connection_count_fails_with_wrong_id(self):
    method = self._api.get_connection_count
    expected = 8

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_connection_count_succeeds(self):
    method = self._api.get_connection_count
    expected = 8

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_raw_mempool_fails_with_wrong_id(self):
    method = self._api.get_raw_mempool
    expected = []

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_raw_mempool_succeeds(self):
    method = self._api.get_raw_mempool
    expected = []

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_transaction_fails_with_wrong_id(self):
    method = functools.partial(
      self._api.get_transaction,
      "327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
    )
    expected = {
      "hash": "327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
    }

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_transaction_succeeds(self):
    method = functools.partial(
      self._api.get_transaction,
      "327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
    )
    expected = {
      "hash": "327bb43c2e40ccb2f83011d35602829872ab190171b79047397d000eddda18a9"
    }

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_websocket_address_fails_with_wrong_id(self):
    method = functools.partial(
      self._api.get_websocket_address,
      "identifier.pubkey"
    )
    expected = "127.0.0.1:30002"

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_websocket_address_succeeds(self):
    method = functools.partial(
      self._api.get_websocket_address,
      "identifier.pubkey"
    )
    expected = "127.0.0.1:30002"

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_version_fails_with_wrong_id(self):
    method = self._api.get_version
    expected = "v0.1-alpha-26-gf7b7"

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_version_succeeds(self):
    method = self._api.get_version
    expected = "v0.1-alpha-26-gf7b7"

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_neighbor_fails_with_wrong_id(self):
    method = self._api.get_neighbor
    expected = [
			{"IpAddr":[0,0,0,0,0,0,0,0,0,0,255,255,127,0,0,1],"Port":30013,"ID":8408941800585506307},
			{"IpAddr":[0,0,0,0,0,0,0,0,0,0,255,255,127,0,0,1],"Port":30005,"ID":2956232338651871234},
			{"IpAddr":[0,0,0,0,0,0,0,0,0,0,255,255,127,0,0,1],"Port":30009,"ID":9027538565785539587}
		]

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_neighbor_succeeds(self):
    method = self._api.get_neighbor
    expected = [
			{"IpAddr":[0,0,0,0,0,0,0,0,0,0,255,255,127,0,0,1],"Port":30013,"ID":8408941800585506307},
			{"IpAddr":[0,0,0,0,0,0,0,0,0,0,255,255,127,0,0,1],"Port":30005,"ID":2956232338651871234},
			{"IpAddr":[0,0,0,0,0,0,0,0,0,0,255,255,127,0,0,1],"Port":30009,"ID":9027538565785539587}
		]

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_node_state_fails_with_wrong_id(self):
    method = self._api.get_node_state
    expected = {
      "State": 0,
			"Port": 30001,
			"ID": 4697163132361310211,
			"Time": 1530087472382892000,
			"Version": 0,
			"Services": 0,
			"Relay": True,
			"Height": 0,
			"TxnCnt": 0,
			"RxTxnCnt": 0,
			"ChordID": "04629f17a6a0ec9a573ecfccb60fa42b104212dd1ec9cdb131993cbb4e15fe5e"
		}

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_node_state_succeeds(self):
    method = self._api.get_node_state
    expected = {
      "State": 0,
			"Port": 30001,
			"ID": 4697163132361310211,
			"Time": 1530087472382892000,
			"Version": 0,
			"Services": 0,
			"Relay": True,
			"Height": 0,
			"TxnCnt": 0,
			"RxTxnCnt": 0,
			"ChordID": "04629f17a6a0ec9a573ecfccb60fa42b104212dd1ec9cdb131993cbb4e15fe5e"
		}

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)

  def test_get_chord_ring_info_fails_with_wrong_id(self):
    method = self._api.get_chord_ring_info
    expected = {
      "Vnodes": [
        {
          "Id": "BGKfF6ag7JpXPs/Mtg+kKxBCEt0eyc2xMZk8u04V/l4=",
          "Host": "127.0.0.1:30000",
          "NodePort": 30001,
          "HttpWsPort": 30002
        }
      ]
    }

    with self.assertRaises(RuntimeError):
      _ = self._with_wrong_id_response(method, expected)

  def test_get_chord_ring_info_succeeds(self):
    method = self._api.get_chord_ring_info
    expected = {
      "Vnodes": [
        {
          "Id": "BGKfF6ag7JpXPs/Mtg+kKxBCEt0eyc2xMZk8u04V/l4=",
          "Host": "127.0.0.1:30000",
          "NodePort": 30001,
          "HttpWsPort": 30002
        }
      ]
    }

    actual = self._with_success_response(method, expected)
    self.assertEqual(actual, expected)


if __name__ == "__main__":
  unittest.main()
