class NknPacket(object):
  def __init__(self):
    self._src = None
    self._dest = None
    self._payload = None
    self._digest = None
    self._signature = None

  @property
  def source(self):
    return self._src

  @property
  def destination(self):
    return self._dest

  @property
  def payload(self):
    return self._payload

  @property
  def signature(self):
    return self._signature

  @property
  def digest(self):
    return self._digest


class NknReceivedPacket(NknPacket):
  def __init__(self, src, payload, digest):
    NknPacket.__init__(self)
    self._src = src
    self._payload = payload
    self._digest = digest


class NknSentPacket(NknPacket):
  def __init__(self, dest, payload, signature):
    NknPacket.__init__(self)
    self._dest = dest
    self._payload = payload

  def sign(self, signature):
    self._signature = signature