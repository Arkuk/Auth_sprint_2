import os

import redis

redis_host = os.getenv("AUTH_REDIS_HOST")
redis_port = os.getenv("AUTH_REDIS_PORT")

jwt_redis_blocklist = redis.Redis(
    host=redis_host, port=int(redis_port), db=1, decode_responses=True
)
