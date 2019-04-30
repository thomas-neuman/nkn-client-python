import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

import nkn_client

async def main():
  from_client = nkn_client.NknClient("one")
  to_client = nkn_client.NknClient("two")

  print("FROM:", from_client.address)
  print("TO:", to_client.address)

  await from_client.connect()
  print(from_client._ws)

  await to_client.connect()
  print(to_client._ws)

  destination = to_client.address
  payload = "It's alive!"

  await from_client.send(destination, payload)

  packet = await to_client.recv()
  assert packet.payload == payload

if __name__ == "__main__":
  asyncio.run(main())