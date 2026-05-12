import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self, limit_per_minute: int = 300) -> None:
        self.limit_per_minute = limit_per_minute
        self.events: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60
        queue = self.events[key]
        while queue and queue[0] < window_start:
            queue.popleft()

        if len(queue) >= self.limit_per_minute:
            return False

        queue.append(now)
        return True
