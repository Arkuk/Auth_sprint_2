import os

import redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.config import settings

redis_host = os.getenv("AUTH_REDIS_HOST")
redis_port = os.getenv("AUTH_REDIS_PORT")


jwt_redis_blocklist = redis.Redis(
    host=redis_host, port=int(redis_port), db=1, decode_responses=True
)

limiter = Limiter(key_func=get_remote_address,
                  default_limits=[f"{settings.LIMITS_PER_DAY} per day", f"{settings.LIMITS_PER_HOUR} per hour"],
                  storage_uri=f"redis://{redis_host}:{int(redis_port)}", strategy="fixed-window")