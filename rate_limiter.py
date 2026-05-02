class RateLimiter:
    def __init__(self, max_per_hour: int, max_per_day: int, cooldown_seconds: int):
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.cooldown_seconds = cooldown_seconds

    def can_send(self) -> tuple[bool, str]:
        # Temel versiyonda her zaman izin verir
        return True, "OK"

    def record_message(self):
        pass

class MessageQueue:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
