import json

from nkn_client.websocket.client import WebsocketClient


class NknWebsocketApi(object):
  """
  Implements a client for the NKN Websocket API.

  Args:
    client (WebsocketClient)  : The client through which API requests
                                will be submitted.
  """
  def __init__(self, client):
    self._client = client

    self._client.connect()

  def __del__(self):
    self._client.disconnect()
  
  def _call_rpc(self, *args, **kwargs):
    result = self._client.send()

  def get_latest_block_height(self):
    pass

  def get_block(self, height=None, hash=None):
    pass

  def get_connection_count(self):
    pass

  def get_transaction(self, hash):
    pass

  def heartbeat(self):
    pass

  def get_session_count(self):
    pass

  def set_client(self, addr):
    pass

  def send_packet(self, packet):
    pass

  def receive_packet(self, packet):
    pass

  def update_sig_blockchain_hash(self):
    pass