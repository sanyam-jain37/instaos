"""Bounded retry policy for retryable publisher failures."""

from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from typing import TypeVar

from app.publishers.exceptions import PublisherError


ResultT = TypeVar("ResultT")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded exponential retry policy with an injectable sleeper."""

    max_attempts: int
    initial_delay_seconds: float
    backoff_multiplier: float
    sleeper: Callable[[float], None] = sleep

    def __post_init__(self) -> None:
        """Validate retry-policy bounds."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one.")

        if self.initial_delay_seconds < 0:
            raise ValueError("initial_delay_seconds must be non-negative.")

        if self.backoff_multiplier < 1:
            raise ValueError("backoff_multiplier must be at least one.")

    def execute(self, operation: Callable[[], ResultT]) -> ResultT:
        """Execute an operation until success or a terminal failure."""
        for attempt in range(1, self.max_attempts + 1):
            try:
                return operation()
            except PublisherError as error:
                is_final_attempt = attempt == self.max_attempts

                if not error.retryable or is_final_attempt:
                    raise

                delay = (
                    self.initial_delay_seconds
                    * self.backoff_multiplier ** (attempt - 1)
                )
                self.sleeper(delay)

        raise RuntimeError("Retry policy exhausted without returning a result.")