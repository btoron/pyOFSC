"""Rate limiting and retry logic for parallel test execution.

This module provides HTTP client wrappers with built-in rate limiting and retry
logic specifically designed for parallel test execution scenarios.
"""

import asyncio
import random
import time
import threading
from typing import Optional, Callable, Any, Dict
from contextlib import asynccontextmanager
import logging

import httpx

logger = logging.getLogger(__name__)


class RateLimitedHTTPClient:
    """HTTP client wrapper with rate limiting and retry logic for parallel tests."""
    
    def __init__(
        self,
        base_client: httpx.AsyncClient,
        max_concurrent_requests: int = 10,
        rate_limit_delay: float = 0.1,
        max_retries: int = 3,
        base_backoff: float = 1.0,
        max_backoff: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True
    ):
        """Initialize rate-limited HTTP client.
        
        Args:
            base_client: The underlying httpx.AsyncClient to wrap
            max_concurrent_requests: Maximum number of concurrent requests
            rate_limit_delay: Minimum delay between requests (seconds)
            max_retries: Maximum number of retry attempts for 429 errors
            base_backoff: Base backoff time for exponential backoff (seconds)
            max_backoff: Maximum backoff time (seconds)
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Whether to add random jitter to backoff times
        """
        self.base_client = base_client
        self.max_concurrent_requests = max_concurrent_requests
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        
        # Request throttling
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._last_request_time = 0.0
        self._request_lock = threading.Lock()
        
        # Statistics
        self._stats = {
            'total_requests': 0,
            'retried_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'total_retry_delay': 0.0,
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the underlying client."""
        if hasattr(self.base_client, 'aclose'):
            await self.base_client.aclose()
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time with exponential backoff and optional jitter."""
        backoff = self.base_backoff * (self.backoff_multiplier ** attempt)
        backoff = min(backoff, self.max_backoff)
        
        if self.jitter:
            # Add ±20% jitter to prevent thundering herd
            jitter_amount = backoff * 0.2
            backoff += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, backoff)
    
    async def _throttle_request(self):
        """Throttle requests to respect rate limits."""
        with self._request_lock:
            now = time.time()
            time_since_last = now - self._last_request_time
            
            if time_since_last < self.rate_limit_delay:
                delay = self.rate_limit_delay - time_since_last
                logger.debug(f"Rate limiting: waiting {delay:.3f}s")
                await asyncio.sleep(delay)
            
            self._last_request_time = time.time()
    
    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with automatic retry on 429 errors."""
        
        for attempt in range(self.max_retries + 1):
            try:
                # Throttle request rate
                await self._throttle_request()
                
                # Make the actual request
                response = await self.base_client.request(method, url, **kwargs)
                
                # Check for rate limiting
                if response.status_code == 429:
                    self._stats['rate_limited_requests'] += 1
                    
                    if attempt < self.max_retries:
                        # Extract retry-after header if present
                        retry_after = response.headers.get('retry-after')
                        if retry_after:
                            try:
                                retry_delay = float(retry_after)
                            except ValueError:
                                retry_delay = self._calculate_backoff(attempt)
                        else:
                            retry_delay = self._calculate_backoff(attempt)
                        
                        self._stats['retried_requests'] += 1
                        self._stats['total_retry_delay'] += retry_delay
                        
                        logger.warning(
                            f"Rate limited (attempt {attempt + 1}/{self.max_retries + 1}), "
                            f"retrying in {retry_delay:.2f}s"
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Rate limited, max retries ({self.max_retries}) exceeded")
                        self._stats['failed_requests'] += 1
                
                # Return response (success or non-429 error)
                return response
                
            except Exception as e:
                if attempt < self.max_retries:
                    retry_delay = self._calculate_backoff(attempt)
                    self._stats['retried_requests'] += 1
                    self._stats['total_retry_delay'] += retry_delay
                    
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}, "
                        f"retrying in {retry_delay:.2f}s"
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Request failed after {self.max_retries} retries: {e}")
                    self._stats['failed_requests'] += 1
                    raise
        
        # This should never be reached, but just in case
        raise RuntimeError("Unexpected end of retry loop")
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make a rate-limited HTTP request with retry logic."""
        async with self._semaphore:
            self._stats['total_requests'] += 1
            return await self._make_request_with_retry(method, url, **kwargs)
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make a GET request."""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make a POST request."""
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Make a PUT request."""
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Make a DELETE request."""
        return await self.request("DELETE", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> httpx.Response:
        """Make a PATCH request."""
        return await self.request("PATCH", url, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        stats = self._stats.copy()
        if stats['total_requests'] > 0:
            stats['retry_rate'] = stats['retried_requests'] / stats['total_requests']
            stats['failure_rate'] = stats['failed_requests'] / stats['total_requests']
            stats['rate_limit_rate'] = stats['rate_limited_requests'] / stats['total_requests']
            stats['average_retry_delay'] = (
                stats['total_retry_delay'] / stats['retried_requests'] 
                if stats['retried_requests'] > 0 else 0
            )
        else:
            stats.update({
                'retry_rate': 0,
                'failure_rate': 0, 
                'rate_limit_rate': 0,
                'average_retry_delay': 0
            })
        
        return stats
    
    def reset_stats(self):
        """Reset rate limiting statistics."""
        self._stats = {
            'total_requests': 0,
            'retried_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'total_retry_delay': 0.0,
        }


@asynccontextmanager
async def rate_limited_client(
    base_client: httpx.AsyncClient,
    **kwargs
) -> RateLimitedHTTPClient:
    """Create a rate-limited HTTP client context manager.
    
    Args:
        base_client: The underlying httpx.AsyncClient
        **kwargs: Additional arguments passed to RateLimitedHTTPClient
    
    Yields:
        RateLimitedHTTPClient instance
    """
    client = RateLimitedHTTPClient(base_client, **kwargs)
    try:
        yield client
    finally:
        await client.close()


# Global rate limiter for test configuration
class GlobalTestRateLimiter:
    """Global rate limiter to coordinate requests across all test workers."""
    
    def __init__(self, max_global_requests_per_second: float = 10.0):
        """Initialize global rate limiter.
        
        Args:
            max_global_requests_per_second: Maximum requests per second across all workers
        """
        self.max_requests_per_second = max_global_requests_per_second
        self.min_request_interval = 1.0 / max_global_requests_per_second
        self._last_request_time = 0.0
        self._lock = threading.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        with self._lock:
            now = time.time()
            time_since_last = now - self._last_request_time
            
            if time_since_last < self.min_request_interval:
                delay = self.min_request_interval - time_since_last
                self._last_request_time = now + delay
                await asyncio.sleep(delay)
            else:
                self._last_request_time = now


# Global instance for test coordination
_global_rate_limiter = GlobalTestRateLimiter()


def get_global_rate_limiter() -> GlobalTestRateLimiter:
    """Get the global rate limiter instance."""
    return _global_rate_limiter