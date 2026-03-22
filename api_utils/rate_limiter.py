"""
API Rate Limiter
Implements token bucket and sliding window algorithms for API rate limiting.
"""

import time
import threading
import logging
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import deque
from functools import wraps
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_second: float = 10.0      # Max requests per second
    requests_per_minute: float = 60.0     # Max requests per minute  
    requests_per_hour: float = 1000.0      # Max requests per hour
    burst_size: int = 10                   # Max burst size
    retry_after: int = 60                  # Seconds to wait when rate limited


class TokenBucket:
    """Token bucket algorithm implementation."""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate      # Tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if successful."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_for_tokens(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """Wait until tokens are available."""
        start = time.time()
        while True:
            if self.consume(tokens):
                return True
            if timeout and (time.time() - start) >= timeout:
                return False
            time.sleep(0.01)  # Small sleep to avoid busy waiting
    
    def get_available_tokens(self) -> float:
        """Get current available tokens."""
        with self._lock:
            self._refill()
            return self.tokens


class SlidingWindowRateLimiter:
    """Sliding window rate limiter implementation."""
    
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self._lock = threading.Lock()
    
    def _cleanup_old_requests(self):
        """Remove requests outside the current window."""
        now = time.time()
        cutoff = now - self.window_seconds
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
    
    def allow_request(self) -> bool:
        """Check if request is allowed."""
        with self._lock:
            self._cleanup_old_requests()
            if len(self.requests) < self.max_requests:
                self.requests.append(time.time())
                return True
            return False
    
    def wait_for_slot(self, timeout: Optional[float] = None) -> bool:
        """Wait until a request slot is available."""
        start = time.time()
        while True:
            if self.allow_request():
                return True
            if timeout and (time.time() - start) >= timeout:
                return False
            time.sleep(0.01)
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window."""
        with self._lock:
            self._cleanup_old_requests()
            return self.max_requests - len(self.requests)
    
    def get_reset_time(self) -> float:
        """Get seconds until window resets."""
        with self._lock:
            self._cleanup_old_requests()
            if not self.requests:
                return 0
            return self.requests[0] + self.window_seconds - time.time()


class MultiLevelRateLimiter:
    """
    Rate limiter with multiple time windows (second, minute, hour).
    Uses token bucket for each level.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.second_limiter = TokenBucket(config.requests_per_second, int(config.burst_size))
        self.minute_limiter = TokenBucket(config.requests_per_second / 60, int(config.requests_per_minute / 60))
        self.hour_limiter = TokenBucket(config.requests_per_second / 3600, int(config.requests_per_hour / 3600))
        self.config = config
        self._lock = threading.Lock()
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Try to acquire permission to make a request.
        Checks all rate limit levels.
        """
        start = time.time()
        
        # Try second limiter
        if not self.second_limiter.wait_for_tokens(tokens, timeout):
            return False
        
        # Try minute limiter
        remaining = timeout - (time.time() - start) if timeout else None
        if not self.minute_limiter.wait_for_tokens(tokens, remaining):
            # Rollback second limiter
            with self.second_limiter._lock:
                self.second_limiter.tokens += tokens
            return False
        
        # Try hour limiter
        remaining = timeout - (time.time() - start) if timeout else None
        if not self.hour_limiter.wait_for_tokens(tokens, remaining):
            # Rollback both
            with self.second_limiter._lock:
                self.second_limiter.tokens += tokens
            with self.minute_limiter._lock:
                self.minute_limiter.tokens += tokens
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return {
            "second": {
                "available": self.second_limiter.get_available_tokens(),
                "rate": self.second_limiter.rate
            },
            "minute": {
                "available": self.minute_limiter.get_available_tokens(),
                "rate": self.minute_limiter.rate
            },
            "hour": {
                "available": self.hour_limiter.get_available_tokens(),
                "rate": self.hour_limiter.rate
            }
        }


class APIRateLimiter:
    """
    Main rate limiter class with per-endpoint tracking.
    Supports both token bucket and sliding window algorithms.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.limiters: Dict[str, MultiLevelRateLimiter] = {}
        self._lock = threading.Lock()
        self._default_limiter = MultiLevelRateLimiter(self.config)
    
    def get_limiter(self, endpoint: str) -> MultiLevelRateLimiter:
        """Get or create a limiter for a specific endpoint."""
        with self._lock:
            if endpoint not in self.limiters:
                self.limiters[endpoint] = MultiLevelRateLimiter(self.config)
            return self.limiters[endpoint]
    
    def acquire(self, endpoint: str = "default", tokens: int = 1, 
                timeout: Optional[float] = None) -> bool:
        """Acquire permission to make a request."""
        limiter = self.get_limiter(endpoint)
        return limiter.acquire(tokens, timeout)
    
    def wait_and_acquire(self, endpoint: str = "default", tokens: int = 1,
                         max_wait: float = 30.0) -> bool:
        """Wait indefinitely until request is allowed (up to max_wait)."""
        return self.acquire(endpoint, tokens, max_wait)
    
    def get_status(self, endpoint: str = "default") -> Dict[str, Any]:
        """Get rate limit status for an endpoint."""
        limiter = self.get_limiter(endpoint)
        return limiter.get_status()
    
    def reset(self, endpoint: Optional[str] = None):
        """Reset rate limits for an endpoint or all endpoints."""
        with self._lock:
            if endpoint:
                self.limiters.pop(endpoint, None)
            else:
                self.limiters.clear()


# Decorator for rate-limited function calls

def rate_limited(config: Optional[RateLimitConfig] = None, 
                 endpoint: Optional[str] = None):
    """
    Decorator to rate-limit a function.
    
    Usage:
        @rate_limited()
        def my_api_call():
            ...
    """
    _config = config or RateLimitConfig()
    _limiter = APIRateLimiter(_config)
    _endpoint = endpoint or "default"
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if _limiter.acquire(_endpoint):
                try:
                    return func(*args, **kwargs)
                finally:
                    pass  # Tokens already consumed
            else:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {func.__name__}. "
                    f"Retry after {_config.retry_after} seconds."
                )
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class RateLimitContext:
    """
    Context manager for rate-limited operations.
    
    Usage:
        with RateLimitContext("api_endpoint") as limiter:
            if limiter.acquire():
                make_api_call()
    """
    
    def __init__(self, endpoint: str = "default", 
                 config: Optional[RateLimitConfig] = None):
        self.endpoint = endpoint
        self.config = config or RateLimitConfig()
        self.limiter = APIRateLimiter(self.config)
    
    def __enter__(self):
        return self.limiter
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Adaptive rate limiter that adjusts based on server responses

class AdaptiveRateLimiter:
    """
    Rate limiter that adapts based on 429 responses from servers.
    """
    
    def __init__(self, initial_config: Optional[RateLimitConfig] = None):
        self.config = initial_config or RateLimitConfig()
        self.limiter = APIRateLimiter(self.config)
        self.penalty_until: Dict[str, float] = {}
        self.backoff_factor = 2.0
        self._lock = threading.Lock()
    
    def acquire(self, endpoint: str, tokens: int = 1) -> bool:
        """Try to acquire permission."""
        # Check if in penalty period
        with self._lock:
            if endpoint in self.penalty_until:
                if time.time() < self.penalty_until[endpoint]:
                    return False
                else:
                    del self.penalty_until[endpoint]
        
        return self.limiter.acquire(endpoint, tokens)
    
    def report_success(self, endpoint: str):
        """Report successful request - could gradually increase rate."""
        pass  # Could implement rate increase here
    
    def report_rate_limit(self, endpoint: str, retry_after: Optional[int] = None):
        """Report rate limited - apply penalty."""
        with self._lock:
            wait_time = retry_after if retry_after else self.config.retry_after
            self.penalty_until[endpoint] = time.time() + wait_time
            
            # Increase penalty for repeated violations
            current = self.config.requests_per_second
            self.config.requests_per_second = max(1.0, current / self.backoff_factor)
            logger.warning(f"Rate limited on {endpoint}. Reducing rate to {self.config.requests_per_second}/s")


# Example usage

if __name__ == "__main__":
    # Basic usage
    config = RateLimitConfig(
        requests_per_second=10,
        requests_per_minute=60,
        requests_per_hour=1000
    )
    
    limiter = APIRateLimiter(config)
    
    # Simulate API calls
    for i in range(15):
        if limiter.acquire("api endpoint"):
            print(f"Request {i + 1}: Allowed")
        else:
            print(f"Request {i + 1}: Blocked")
    
    # Check status
    print("\nRate limit status:")
    print(limiter.get_status("api endpoint"))
    
    # Using decorator
    @rate_limited()
    def my_api_call():
        return "API call successful!"
    
    try:
        result = my_api_call()
        print(f"\n{result}")
    except RateLimitExceeded as e:
        print(f"\n{e}")
