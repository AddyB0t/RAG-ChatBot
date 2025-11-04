"""
Rate limiting middleware for API endpoints
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter using sliding window"""

    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for the identifier (IP address)

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        request_times = self.requests[identifier]

        request_times = [t for t in request_times if t > window_start]
        self.requests[identifier] = request_times

        if len(request_times) < self.requests_per_minute:
            self.requests[identifier].append(current_time)
            remaining = self.requests_per_minute - len(request_times) - 1
            return True, remaining
        else:
            remaining = 0
            return False, remaining

    def cleanup_old_entries(self):
        """Remove old entries to prevent memory leak"""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        to_remove = []
        for ip, times in self.requests.items():
            if not times or max(times) < window_start:
                to_remove.append(ip)

        for ip in to_remove:
            del self.requests[ip]

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to all requests"""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)
        self.cleanup_counter = 0

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/", "/health", "/api/v1/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        is_allowed, remaining = self.limiter.is_allowed(client_ip)

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.limiter.requests_per_minute} requests per minute",
                    "retry_after": 60
                }
            )

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

        self.cleanup_counter += 1
        if self.cleanup_counter >= 1000:
            self.limiter.cleanup_old_entries()
            self.cleanup_counter = 0

        return response

_rate_limiter = None

def get_rate_limiter(requests_per_minute: int = 100) -> RateLimitMiddleware:
    """Get or create rate limiter middleware"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimitMiddleware(None, requests_per_minute)
    return _rate_limiter

