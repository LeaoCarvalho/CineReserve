import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    password="senha1234",
    decode_responses=True
)