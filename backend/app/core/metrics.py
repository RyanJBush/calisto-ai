from dataclasses import dataclass


@dataclass
class MetricsStore:
    request_count: int = 0

    def increment(self) -> None:
        self.request_count += 1


metrics_store = MetricsStore()
