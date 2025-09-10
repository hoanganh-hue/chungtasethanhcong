"""
Rate Limiting System for OpenManus-Youtu Integrated Framework
Advanced rate limiting and IP management
"""

import time
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import ipaddress
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int
    window: int  # seconds
    burst: int = 0


@dataclass
class RateLimitResult:
    """Rate limit check result."""
    allowed: bool
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None


class RateLimiter:
    """Advanced rate limiter with sliding window."""
    
    def __init__(self):
        self.rate_limits: Dict[str, RateLimit] = {}
        self.request_history: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}
        self.cleanup_interval = 300  # 5 minutes
        self._cleanup_task = None
    
    def add_rate_limit(self, key: str, rate_limit: RateLimit):
        """Add rate limit configuration."""
        self.rate_limits[key] = rate_limit
        logger.info(f"Added rate limit for {key}: {rate_limit.requests}/{rate_limit.window}s")
    
    def is_allowed(self, identifier: str, rate_limit_key: str = "default") -> RateLimitResult:
        """Check if request is allowed."""
        if rate_limit_key not in self.rate_limits:
            return RateLimitResult(allowed=True, remaining=999, reset_time=int(time.time() + 3600))
        
        rate_limit = self.rate_limits[rate_limit_key]
        current_time = time.time()
        
        # Clean old requests
        self._cleanup_old_requests(identifier, current_time, rate_limit.window)
        
        # Check if blocked
        if identifier in self.blocked_ips:
            if current_time < self.blocked_ips[identifier].timestamp():
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=int(self.blocked_ips[identifier].timestamp()),
                    retry_after=int(self.blocked_ips[identifier].timestamp() - current_time)
                )
            else:
                del self.blocked_ips[identifier]
        
        # Check rate limit
        request_count = len(self.request_history[identifier])
        
        if request_count >= rate_limit.requests:
            # Check burst allowance
            if rate_limit.burst > 0 and request_count < rate_limit.requests + rate_limit.burst:
                # Allow burst request
                self.request_history[identifier].append(current_time)
                return RateLimitResult(
                    allowed=True,
                    remaining=rate_limit.requests + rate_limit.burst - request_count - 1,
                    reset_time=int(current_time + rate_limit.window)
                )
            else:
                # Rate limit exceeded
                oldest_request = self.request_history[identifier][0]
                reset_time = int(oldest_request + rate_limit.window)
                retry_after = max(0, int(reset_time - current_time))
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=retry_after
                )
        
        # Allow request
        self.request_history[identifier].append(current_time)
        remaining = rate_limit.requests - request_count - 1
        
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=int(current_time + rate_limit.window)
        )
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Block IP address for specified duration."""
        self.blocked_ips[ip] = datetime.fromtimestamp(time.time() + duration)
        logger.warning(f"Blocked IP {ip} for {duration} seconds")
    
    def unblock_ip(self, ip: str):
        """Unblock IP address."""
        if ip in self.blocked_ips:
            del self.blocked_ips[ip]
            logger.info(f"Unblocked IP {ip}")
    
    def _cleanup_old_requests(self, identifier: str, current_time: float, window: int):
        """Clean up old requests from history."""
        cutoff_time = current_time - window
        
        while (self.request_history[identifier] and 
               self.request_history[identifier][0] < cutoff_time):
            self.request_history[identifier].popleft()
    
    async def start_cleanup_task(self):
        """Start background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")
    
    def _cleanup_expired_data(self):
        """Clean up expired data."""
        current_time = time.time()
        
        # Clean up blocked IPs
        expired_ips = [
            ip for ip, block_time in self.blocked_ips.items()
            if current_time > block_time.timestamp()
        ]
        
        for ip in expired_ips:
            del self.blocked_ips[ip]
        
        # Clean up request history for inactive identifiers
        inactive_identifiers = []
        
        for identifier, history in self.request_history.items():
            if not history or current_time - history[-1] > 3600:  # 1 hour
                inactive_identifiers.append(identifier)
        
        for identifier in inactive_identifiers:
            del self.request_history[identifier]
        
        if expired_ips or inactive_identifiers:
            logger.debug(f"Cleaned up {len(expired_ips)} expired IPs and {len(inactive_identifiers)} inactive identifiers")


class IPWhitelist:
    """IP whitelist management."""
    
    def __init__(self):
        self.whitelisted_ips: List[ipaddress.IPv4Network] = []
        self.whitelisted_ranges: List[ipaddress.IPv4Network] = []
        self.trusted_proxies: List[str] = []
    
    def add_ip(self, ip: str):
        """Add IP to whitelist."""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            self.whitelisted_ips.append(ip_obj)
            logger.info(f"Added IP to whitelist: {ip}")
        except ipaddress.AddressValueError:
            logger.error(f"Invalid IP address: {ip}")
    
    def add_range(self, ip_range: str):
        """Add IP range to whitelist."""
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            self.whitelisted_ranges.append(network)
            logger.info(f"Added IP range to whitelist: {ip_range}")
        except ipaddress.AddressValueError:
            logger.error(f"Invalid IP range: {ip_range}")
    
    def add_trusted_proxy(self, proxy: str):
        """Add trusted proxy."""
        self.trusted_proxies.append(proxy)
        logger.info(f"Added trusted proxy: {proxy}")
    
    def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted."""
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            
            # Check individual IPs
            if ip_obj in self.whitelisted_ips:
                return True
            
            # Check ranges
            for network in self.whitelisted_ranges:
                if ip_obj in network:
                    return True
            
            return False
        except ipaddress.AddressValueError:
            return False
    
    def is_trusted_proxy(self, proxy: str) -> bool:
        """Check if proxy is trusted."""
        return proxy in self.trusted_proxies
    
    def get_real_ip(self, request_headers: Dict[str, str], remote_addr: str) -> str:
        """Get real IP address considering trusted proxies."""
        # Check for forwarded headers
        forwarded_for = request_headers.get('X-Forwarded-For')
        real_ip = request_headers.get('X-Real-IP')
        
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs
            ips = [ip.strip() for ip in forwarded_for.split(',')]
            
            # Find the first non-trusted proxy IP
            for ip in ips:
                if not self.is_trusted_proxy(ip):
                    return ip
            
            # If all are trusted, return the last one
            return ips[-1] if ips else remote_addr
        
        if real_ip and not self.is_trusted_proxy(real_ip):
            return real_ip
        
        return remote_addr


class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.ip_whitelist = IPWhitelist()
        self.user_limits: Dict[str, RateLimit] = {}
        self.endpoint_limits: Dict[str, RateLimit] = {}
        
        # Default rate limits
        self.rate_limiter.add_rate_limit("default", RateLimit(requests=100, window=3600))
        self.rate_limiter.add_rate_limit("api", RateLimit(requests=1000, window=3600))
        self.rate_limiter.add_rate_limit("auth", RateLimit(requests=5, window=300))
        self.rate_limiter.add_rate_limit("upload", RateLimit(requests=10, window=3600))
    
    def set_user_rate_limit(self, user_id: str, rate_limit: RateLimit):
        """Set rate limit for specific user."""
        self.user_limits[user_id] = rate_limit
        logger.info(f"Set rate limit for user {user_id}: {rate_limit.requests}/{rate_limit.window}s")
    
    def set_endpoint_rate_limit(self, endpoint: str, rate_limit: RateLimit):
        """Set rate limit for specific endpoint."""
        self.endpoint_limits[endpoint] = rate_limit
        logger.info(f"Set rate limit for endpoint {endpoint}: {rate_limit.requests}/{rate_limit.window}s")
    
    def check_rate_limit(self, 
                        identifier: str, 
                        endpoint: str = None, 
                        user_id: str = None,
                        ip: str = None) -> RateLimitResult:
        """Check rate limit with multiple strategies."""
        
        # Check IP whitelist
        if ip and self.ip_whitelist.is_whitelisted(ip):
            return RateLimitResult(allowed=True, remaining=999, reset_time=int(time.time() + 3600))
        
        # Determine rate limit key
        rate_limit_key = "default"
        
        if endpoint and endpoint in self.endpoint_limits:
            rate_limit_key = f"endpoint_{endpoint}"
        elif user_id and user_id in self.user_limits:
            rate_limit_key = f"user_{user_id}"
        elif endpoint:
            # Map endpoint to predefined limits
            if "auth" in endpoint:
                rate_limit_key = "auth"
            elif "upload" in endpoint:
                rate_limit_key = "upload"
            elif "api" in endpoint:
                rate_limit_key = "api"
        
        # Check rate limit
        return self.rate_limiter.is_allowed(identifier, rate_limit_key)
    
    def block_user(self, user_id: str, duration: int = 3600):
        """Block user for specified duration."""
        self.rate_limiter.block_ip(f"user_{user_id}", duration)
        logger.warning(f"Blocked user {user_id} for {duration} seconds")
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Block IP address for specified duration."""
        self.rate_limiter.block_ip(ip, duration)
    
    async def start(self):
        """Start rate limiter."""
        await self.rate_limiter.start_cleanup_task()
        logger.info("Advanced rate limiter started")
    
    async def stop(self):
        """Stop rate limiter."""
        await self.rate_limiter.stop_cleanup_task()
        logger.info("Advanced rate limiter stopped")


# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()