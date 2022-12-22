import asyncio

import aioredis

from tests.functional.settings import test_settings


async def wait_redis():
    redis_client = aioredis.Redis(
        host=test_settings.redis_host, port=test_settings.redis_port, socket_connect_timeout=1
    )
    ping_redis = await redis_client.ping()
    print(f'get_ping: {ping_redis}')
    while await redis_client.ping() is False:
        await asyncio.sleep(1)
    await redis_client.close()
    return


if __name__ == '__main__':
    print('waiting for Redis...')
    asyncio.run(wait_redis())
    print('Redis is ok')