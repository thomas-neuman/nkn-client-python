import requests

class JsonRpcRequest(object):
  """
  The base class for interacting with a JSON-RPC server. A JsonRpcRequest is
  formed, prepared, and then eventually submitted to invoke the intended
  procedure. The JsonRpcRequest encapsulates all of the server and client
  context necessary to invoke the procedure, as well as the parameters of the
  procedure itself. Once the request is fully formed and prepared, it can be
  sent by way of a JsonRpcSession, which will then produce a JsonRpcResponse.

  Example usage:
    req = JsonRpcRequest('url', 'method', params=['a', 'b'])
    preq = req.prepare()
    resp = JsonRpcSession().send(preq)

  Args:
    url (str)         : The URL to which this request will be submitted.
    method (str)      : The remote method to invoke.
    params (iterable) : Any parameters to pass to the remote procedure.
                        Positional arguments are provided as a list; named
                        parameters are provided as a dict.
    req_id (int)      : An identifier for this request, to be paired with the
                        same identifier in the server's response.
    auth (tuple)      : An authentication tuple, or requests.AuthBase object,
                        to be used for authenticating with the server if needed.
    cert (str)        : Filename of a certificate file to use in authenticating
                        the server, if needed.
  """
  def __init__(self, url, method, params=None, req_id=None, auth=None, cert=None):
    self.url = url
    self.method = method
    self.params = params
    self.req_id = req_id
    self.auth = auth
    self.cert = cert

  def prepare(self):
    """
    Prepare the request for submission.

    Returns:
      PreparedJsonRpcRequest
    """
    req = PreparedJsonRpcRequest()
    req.prepare(
      url=self.url,
      method=self.method,
      params=self.params,
      req_id=self.req_id,
      auth=self.auth,
      cert=self.cert
    )
    return req


class PreparedJsonRpcRequest(object):
  """
  A prepared request, which is ready for submission to the server.
  """
  def __init__(self):
    self._req = requests.Request(method="POST")

  def prepare_body(self, method, params, req_id):
    """
    Prepare the JSON-RPC body with the given method name, parameters, and ID.
    The RPC is formed and added to the underlying requests.Request object in
    its body.

    Args:
      method (str)      : The remote method to invoke.
      params (iterable) : Any parameters to pass to the remote procedure.
                          Positional arguments are provided as a list; named
                          parameters are provided as a dict.
      req_id (int)      : An identifier for this request, to be paired with the
                          same identifier in the server's response.
    """
    body = self._req.json
    body["jsonrpc"] = "2.0"

    if method is not None:
      body["method"] = method
    if params is not None:
    if req_id is not None:
      body["req_id"] = req_id

    body = {
      "jsonrpc": "2.0",
      "method": method,
      "id": req_id
    }
    if params is not None:
      body["params"] = params
    self._req.json = body

  def prepare_request(self, url, auth, cert):
    """
    Sets up the remaining parameters in the underlying requests.Request object.
    This includes setting the URL and configuring any authentication specified.

    Args:
      url (str)         : The URL to which this request will be submitted.
      auth (tuple)      : An authentication tuple, or requests.AuthBase object,
                          to be used for authenticating with the server if
                          needed.
      cert (str)        : Filename of a certificate file to use in
                          authenticating the server, if needed.
    """
    if url is not None:
      self._req.url = url
    if auth is not None:
      self._req.auth = auth
    if cert is not None:
      self._req.cert = cert

  def prepare(
      self,
      url=None,
      method=None,
      params=None,
      req_id=None,
      auth=None,
      cert=None
  ):
    """
    Prepare the request for submission. Once complete, the request can be
    passed to the server through a JsonRpcSession to invoke the procedure.

    Args:
      url (str)         : The URL to which this request will be submitted.
      method (str)      : The remote method to invoke.
      params (iterable) : Any parameters to pass to the remote procedure.
                          Positional arguments are provided as a list; named
                          parameters are provided as a dict.
      req_id (int)      : An identifier for this request, to be paired with the
                          same identifier in the server's response.
      auth (tuple)      : An authentication tuple, or requests.AuthBase object,
                          to be used for authenticating with the server if
                          needed.
      cert (str)        : Filename of a certificate file to use in
                          authenticating the server, if needed.
    Raises:
      ValueError        : If the URL or remote method name is left unspecified.
    """
    self.prepare_body(method, params, req_id)
    self.prepare_request(url, body, auth, cert)
    self.req = self._req.prepare()
