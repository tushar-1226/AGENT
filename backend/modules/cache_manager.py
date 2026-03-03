"""
Cache Manager Module
Implements caching for expensive operations
"""

import json
import logging
from typing import Optional, Any, Dict
from functools import wraps
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheManager:
    """
    In-memory cache manager with TTL support
    For production, use Redis or Memcached
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check expiration
            if entry["expires_at"] and datetime.now() > entry["expires_at"]:
                self.delete(key)
                self.cache_stats["misses"] += 1
                return None
            
            self.cache_stats["hits"] += 1
            return entry["value"]
        
        self.cache_stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL in seconds"""
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl else None
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now()
        }
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            self.cache_stats["evictions"] += 1
    
    def clear(self):
        """Clear all cache"""
        count = len(self.cache)
        self.cache.clear()
        self.cache_stats["evictions"] += count
        logger.info(f"Cleared {count} cache entries")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests * 100
            if total_requests > 0
            else 0
        )
        
        return {
            "entries": len(self.cache),
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "hit_rate": round(hit_rate, 2)
        }
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry["expires_at"] and now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = f"{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 3600):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=1800)
        async def expensive_operation(param1, param2):
            # ... expensive code ...
            return result
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from app.main import get_cache_manager
            
            cache = get_cache_manager()
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl=ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create cache manager singleton"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
