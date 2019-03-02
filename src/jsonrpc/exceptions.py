from enum import IntEnum, unique

class JsonRpcException(Exception):
  def __init__(self, method, params, error):
    code = error.get("code", 1)
    msg = error.get("message", "")
    data = error.get("data", "")

    self.message = ("Invocation: %s(%s) yielded error.\n%s %s\n%s" % (
        method,
        params if params else "",
        code,
        msg,
        data
    )

class JsonRpcInvokeError(JsonRpcException):
  def __init__(self, method, params, error):
    JsonRpcException.__init__(self, method, params, error)
    self.message += "\tDid not receive JSON-RPC compliant response!\n"

class JsonRpcNoResponseError(JsonRpcInvokeError):
  def __init__(self, method, params, error):
    JsonRpcInvokeError.__init__(self, method, params, error)
    self.message += "\t\tNo response received!"

class JsonRpcInvalidResponseError(JsonRpcInvokeError):
  def __init__(self, method, params, response):
    JsonRpcInvokeError.__init__(self, method, params, {})
    self.message += "\t\tInvalid response received!\n\t\t%s\n" % (response)


class JsonRpcClientError(JsonRpcException):
  def __init__(self, method, params, error):
    JsonRpcException.__init__(self, method, params, error)
    self.message += "\tJSON-RPC client caused an error!\n"

class JsonRpcMethodNotFoundError(JsonRpcClientError):
  def __init__(self, method, params, error):
    JsonRpcClientError.__init__(self, method, params, error)
    self.message += "\t\tMethod %s not found!\n" % (method)

class JsonRpcInvalidParamsError(JsonRpcClientError):
  def __init__(self, method, params, error):
    JsonRpcClientError.__init__(self, method, params, error)
    self.message += "\t\tParameters %s invalid for method %s!\n" % (
        params if params else "",
        method
    )

class JsonRpcInternalError(JsonRpcClientError):
  def __init__(self, method, params, error):
    JsonRpcClientError.__init__(self, method, params, error)
    self.message += "\t\tJSON-RPC encountered an internal error!\n"


class JsonRpcServerError(JsonRpcException):
  def __init__(self, method, params, error):
    JsonRpcException.__init__(self, method, params, error)
    self.message += "\tJSON-RPC server encountered an error!\n"


@unique
class JsonRpcErrorCodes(IntEnum):
  PARSE_ERROR = -32700
  INVALID_REQUEST = -32600
  METHOD_NOT_FOUND = -32601
  INVALID_PARAMS = -32602
  INTERNAL_ERROR = -32603
  SERVER_ERROR_UPPER = -32000
  SERVER_ERROR_LOWER = -32099

ERROR_CODES = {
  JsonRpcErrorCodes.METHOD_NOT_FOUND = JsonRpcMethodNotFoundError,
  JsonRpcErrorCodes.INVALID_PARAMS = JsonRpcInvalidParamsError,
  JsonRpcErrorCodes.INTERNAL_ERROR = JsonRpcInternalError
}
