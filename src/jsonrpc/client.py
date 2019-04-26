import requests


class HttpClientException(Exception):
  pass

class HttpClient(object):
  def __init__(self):
    self._sess = requests.Session()

  def _request(self, method, url, **kwargs):
    resp = self._sess.request(method, url, **kwargs)
    try:
      resp.raise_for_status()
    except requests.RequestException:
      raise HttpClientException(resp.text)

    return resp

  def get(self, url, **kwargs):
    return self._request("GET", url, **kwargs)

  def put(self, url, **kwargs):
    return self._request("PUT", url, **kwargs)

  def patch(self, url, **kwargs):
    return self._request("PATCH", url, **kwargs)

  def post(self, url, **kwargs):
    return self._request("POST", url, **kwargs)

  def delete(self, url, **kwargs):
    return self._request("DELETE", url, **kwargs)