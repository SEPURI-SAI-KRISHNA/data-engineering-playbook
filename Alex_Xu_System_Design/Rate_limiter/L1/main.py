import time
import threading


class InMemoryRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        """
        :param capacity: Maximum tokens the bucket can hold.
        :param refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}
        self.lock = threading.Lock()

    def _refill(self, user_id: str, now: float):
        bucket = self.buckets.get(user_id)
        if not bucket:
            self.buckets[user_id] = {"tokens": self.capacity, "last_refill": now}
            return

        time_passed = now - bucket["last_refill"]
        new_tokens = time_passed * self.refill_rate

        bucket["tokens"] = min(self.capacity, bucket["tokens"] + new_tokens)
        bucket["last_refill"] = now

    def allow_request(self, user_id: str) -> bool:
        now = time.time()

        with self.lock:
            self._refill(user_id, now)
            bucket = self.buckets[user_id]

            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True
            else:
                return False


limiter = InMemoryRateLimiter(capacity=5, refill_rate=1.0)
user = "user_123"

for i in range(7):
    allowed = limiter.allow_request(user)
    print(f"Request {i + 1}: {'Allowed' if allowed else 'Blocked (429)'}")
    time.sleep(0.2)
