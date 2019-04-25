from collections import namedtuple

NknPacket = namedtuple(
    "NknPacket",
    ["source", "destination", "payload", "digest", "signature"],
    defaults=[None, None, None, None, None]
)

def NknSentPacket(dest, payload):
  return NknPacket(destination=dest, payload=payload)

def NknReceivedPacket(source, payload, digest):
  return NknPacket(source=source, payload=payload, digest=digest)

def sign(packet, signature):
  return NknPacket(
      source=packet.source,
      destination=packet.destination,
      payload=packet.payload,
      digest=packet.digest,
      signature=signature
  )