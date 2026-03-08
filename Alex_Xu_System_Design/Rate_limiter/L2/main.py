import time
import redis


class RedisFixedWindowLimiter:
    def __init__(self, redis_client, limit: int, window_size_sec: int):
        self.redis = redis_client
        self.limit = limit
        self.window_size_sec = window_size_sec

    def allow_request(self, user_id: str) -> bool:
        # e.g., if time is 10:05:32 and window is 60s, window_key represents the 10:05:00 bucket
        current_window = int(time.time() // self.window_size_sec)
        redis_key = f"rate_limit:{user_id}:{current_window}"

        # Use a Redis pipeline to execute commands atomically
        pipeline = self.redis.pipeline()
        pipeline.incr(redis_key)
        # Set expiration to slightly longer than the window to auto-cleanup
        pipeline.expire(redis_key, self.window_size_sec + 5)

        # Execute pipeline; result[0] contains the output of incr
        result = pipeline.execute()
        current_count = result[0]

        return current_count <= self.limit


# --- Usage Example ---
# Assuming Redis is running on localhost:6379
redis_conn = redis.Redis(host='localhost', port=6379, db=0)
limiter = RedisFixedWindowLimiter(redis_conn, limit=5, window_size_sec=10)
user = "user_456"

for i in range(7):
    allowed = limiter.allow_request(user)
    print(f"Request {i + 1}: {'Allowed' if allowed else 'Blocked (429)'}")
