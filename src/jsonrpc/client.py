import requests
from requests import Session

from .exceptions import *

class BaseJsonRpcClient(object):
  """
  A base client for communicating with an HTTP server serving
  JSON-RPC 2.0 requests. The main functionality is provided by
  the 'call' method, which takes at least one parameter
  indicating the remote procedure to invoke:

    result = JsonRpcClient().call('method')

  Parameters for the remote procedure are passed through an
  optional parameter in the method:

    result = JsonRpcClient().call('method', params=['one', 'two'])

  The JSON reponses from the server is returned directly from the
  'call' method. It may contain either a 'result' or an 'error'
  field, and there are no guarantees on the correctness of the
  'jsonrpc' or 'id' fields.

  Args:
    url (str)     : The URL to be used for submitting RPC calls.
    auth (tuple)  : An authentication tuple for the client to provide
                    the server, if necessary. (Default: None)
    cert (str)    : A certificate chain file to use in authenticating
                    the server, if necessary. (Default: None)
  """
  def __init__(self, url, auth=None, cert=None):
    self._url = url
    self._sess = Session(auth, cert)

  def call(self, method, params=None):
    """
    Invoke a remote procedure on the server.

    Args:
      method (str)        : The method to invoke.
      params (iterable)   : Any parameters to include in the RPC call.
                            Positional parameters are provided in the form of
                            a sequence, while named parameters are as a dict.
    Returns:
      dict                : The JSON response from the server.
    Raises:
      JsonRpcInvokeError  : If the server could not be reached, or no JSON-RPC
                            compliant response was received from the server.
    """
    pass

class JsonRpcClient(BaseJsonRpcClient):
  """
  See 'BaseJsonRpcClient' for more details.

  The client will propagate errors returned from the server, in
  the form of exceptions:

    # Raises 'MethodNotFoundError'
    JsonRpcClient.call('non_existent_method')
  """
  def call(self, method, params=None):
    """
    Invoke a remote procedure on the server.

    Args:
      method (str)        : The method to invoke.
      params (iterable)   : Any parameters to include in the RPC call.
                            Positional parameters are provided in the form
                            of a sequence, while named parameters are as a
                            dict.
    Returns:
      dict                : The JSON response from the server.
    Raises:
      JsonRpcClientError  : If the server indicated an erroneous request
                                was received.
      JsonRpcServerError  : If the server encountered an error while
                                serving the request.
    """
    response = BaseJsonRpcClient.call(self, method, params)
    return self.raise_for_status(response)

  def raise_for_status(self, response):
    if "error" not in response:
      return response

    err = response["error"]
    code = err["code"]
    try:
      exc = ERROR_CODES[code]
      raise exc
    except KeyError:
      pass
