import os

import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

redis_host = os.getenv("AUTH_REDIS_HOST")
redis_port = os.getenv("AUTH_REDIS_PORT")

jwt_redis_blocklist = redis.Redis(
    host=redis_host, port=int(redis_port), db=1, decode_responses=True
)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{redis_host}:{int(redis_port)}",
    strategy="fixed-window"
)
