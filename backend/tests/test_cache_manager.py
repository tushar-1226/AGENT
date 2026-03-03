"""
Tests for Cache Manager
"""

import pytest
import time
from modules.cache_manager import CacheManager


class TestCacheManager:
    
    def test_set_and_get(self):
        """Test basic set and get operations"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_get_nonexistent(self):
        """Test getting non-existent key"""
        cache = CacheManager()
        assert cache.get("nonexistent") is None
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        cache = CacheManager()
        
        cache.set("expiring", "value", ttl=1)
        assert cache.get("expiring") == "value"
        
        time.sleep(1.1)
        assert cache.get("expiring") is None
    
    def test_delete(self):
        """Test delete operation"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_clear(self):
        """Test clear all"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_stats(self):
        """Test cache statistics"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["entries"] == 1
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        cache = CacheManager()
        
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=10)
        
        time.sleep(1.1)
        cache.cleanup_expired()
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
