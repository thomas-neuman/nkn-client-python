import requests

from .request import JsonRpcRequest, PreparedJsonRpcRequest
from .response import JsonRpcResponse

class JsonRpcSession(object):
  def __init__(self, init_id=1, auth=None, cert=None):
    self._id = init_id
    self._sess = requests.Session(auth, cert)

  def prepare_request(self, req):
    if not isinstance(req, JsonRpcRequest):
      raise ValueError("Must prepare a JsonRpcRequest")

    return PreparedJsonRpcRequest(
      req.url,
      req.method,
      req.params,
      (req.id if req.id else self._id),
      (req.auth if req.auth else self._auth),
      (req.cert if req.cert else self._cert)
    )

  def send(self, req):
    if not isinstance(req, PreparedJsonRpcRequest):
      raise ValueError("Must invoke a prepared request")
    resp = self._sess.send(req.request)
    return JsonRpcResponse(resp)
