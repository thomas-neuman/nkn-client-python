import json
import uuid

from nkn_client.jsonrpc.client import HttpClient, HttpClientException


class JsonRpcError(Exception):
  pass

class JsonRpcApiClient(HttpClient):
  def __init__(self):
    HttpClient.__init__(self)

  def _generate_request_id(self):
    return str(uuid.uuid4())

  def call(self, url, method, *args, req_id=None, **kwargs):
    """
    Call a JSON-RPC at the given URL.

    Args:
      url (str)     : URL to call.
      method (str)  : Name of the remote procedure to invoke.
      args          : Positional arguments to provide when invoking the
                      remote procedure.
      kwargs        : Named arguments to provide when invoking the
                      remote procedure.
      req_id (str)  : An identifier for this request. If none is provided,
                      one will be generated automatically.
    Returns:
      dict          : JSON response from the server.
    Raises:
      JsonRpcError  : If the response indicated failure, or the ID from
                      the RPC result did not match the provided ID.
    """
    req = {
      "method": method
    }

    if args:
      assert not kwargs
      req["params"] = list(args)
    if kwargs:
      req["params"] = kwargs

    if req_id is None:
      req_id = self._generate_request_id()
    req["id"] = req_id

    resp = self.post(url, json=req)

    result = resp.json()
    if result["id"] != req_id:
      raise JsonRpcError(
          "Mismatched request ID! Sent: %s, received %s" %
          (req_id, result["id"])
      )

    if "error" in result:
      raise JsonRpcError("JSON-RPC reported error!\n%s" % (json.dumps(result)))

    return result["result"]