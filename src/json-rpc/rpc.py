import requests
import uuid

def _generate_id():
  # Returns a randomly generated ID.
  return uuid.uuid4()

def call_rpc(url, method, params=None, req_id=None):
  """
  Call a JSON-RPC at the given URL.

  Args:
    method (str)      : Name of the remote procedure to call.
    params (iterable) : Parameters to pass when invoking the remote
                        procedure. Positional arguments are given as a list,
                        and named arguments are given as a dict.
    req_id (str)      : An identifier for this request. If none is provided,
                        one will be generated automatically.
  Returns:
    dict              : JSON response from the server.
  Raises:
    RuntimeError      : If the response indicated failure, or the ID from
                        the RPC result did not match the provided ID.
  """
  if req_id is None:
    req_id = _generate_id()

  payload = {
    "jsonrpc": "2.0",
    "method": method,
    "id": (req_id if req_id is not None else _generate_id())
  }
  if params is not None:
    payload["params"] = params

  resp = requests.post(url, json=payload)
  if resp is None or not resp.ok:
    raise RuntimeError(
        "Error calling RPC!\n%s : %s" % (resp.status_code, resp.text)
    )

  result = resp.json()
  if result["id"] != req_id:
    raise RuntimeError(
        "RPC server returned a reponse with the wrong ID!\n"
        "  Sent: %s\n  Received: %s" % (req_id, result["id"])
    )

  return result
