# nkn-client-python
Python client library for the NKN blockchain network.

This client is only compatible with Python 3.
All of the client methods use the `asyncio` framework.

## Usage

Instantiate an [`NknClient`](./src/nkn_client/client/client.py).
The client needs, at the very least, an identifier string.
You may provide some secret seed material (hex-encoded) to associate it with a wallet's ED25519 keypair.
```python
import nkn_client

client = nkn_client.NknClient("id", "deadbeef")
```

Open up a connection to a node.
The node to connect will automatically be selected.
```python
await client.connect()
```

Once the connection is opened, your client may begin to receive packets.
Pick them up by the `recv` method.
The resulting structure is an [`NknPacket`](./src/nkn_client/client/packet.py).
```python
next_packet = await client.recv()

# Source address
print(next_packet.source)
# Digest
print(next_packet.digest)

# Packet payload
print(next_packet.payload)
```

In addition, you may send packets out over the network.
```python
# Destination NKN address
destination = "identifier.pubkey"
payload = "Extra! Extra!"

await client.send(destination, payload)
```

When you're done, you may disconnect from the network.
```python
await client.disconnect()
```