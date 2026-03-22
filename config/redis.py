import redis
import os

redis_client = redis.Redis(
    host="redis",
    port=6379,
    db=0,
    password=os.environ.get("REDIS_PASSWORD"),
    decode_responses=True
)