"""
Cache Manager
In-memory and persistent caching with TTL, LRU eviction, and serialization.
"""

import time
import threading
import json
import pickle
import hashlib
import logging
import os
from typing import Any, Optional, Dict, Callable, TypeVar, Union
from dataclasses import dataclass, field
from collections import OrderedDict
from pathlib import Path
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def touch(self):
        """Update access metadata."""
        self.access_count += 1
        self.last_accessed = time.time()


class LRUCache:
    """
    Thread-safe LRU (Least Recently Used) cache implementation.
    """
    
    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, key: str) -> str:
        """Generate cache key (can be overridden for custom key generation)."""
        return key
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        key = self._generate_key(key)
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return default
            
            entry = self._cache[key]
            
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return default
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            self._hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        key = self._generate_key(key)
        ttl = ttl if ttl is not None else self.ttl
        
        with self._lock:
            # Remove if exists to update position
            if key in self._cache:
                del self._cache[key]
            
            # Evict oldest if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            expires_at = time.time() + ttl if ttl else None
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                expires_at=expires_at
            )
            self._cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        key = self._generate_key(key)
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def has(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        key = self._generate_key(key)
        
        with self._lock:
            if key not in self._cache:
                return False
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return False
            return True
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        removed = 0
        
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items() 
                if v.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                removed += 1
        
        return removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0,
                "ttl": self.ttl
            }
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        return self.has(key)


class TTLCache:
    """
    Simple TTL-based cache that automatically expires entries.
    """
    
    def __init__(self, ttl: float = 300, cleanup_interval: float = 60):
        self.ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
    
    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            self._maybe_cleanup()
            
            if key not in self._cache:
                return default
            
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                return default
            
            entry.touch()
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        ttl = ttl if ttl is not None else self.ttl
        with self._lock:
            expires_at = time.time() + ttl
            self._cache[key] = CacheEntry(
                value=value,
                created_at=time.time(),
                expires_at=expires_at
            )
    
    def _maybe_cleanup(self):
        """Run cleanup if interval has passed."""
        if time.time() - self._last_cleanup > self._cleanup_interval:
            self._cleanup()
            self._last_cleanup = time.time()
    
    def _cleanup(self):
        """Remove expired entries."""
        expired = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired:
            del self._cache[key]


class PersistentCache:
    """
    Cache with optional disk persistence.
    """
    
    def __init__(self, cache_dir: str = ".cache", 
                 serializer: str = "json",  # json or pickle
                 max_size: int = 1000,
                 ttl: Optional[float] = None):
        self.cache_dir = Path(cache_dir)
        self.serializer = serializer
        self.memory_cache = LRUCache(max_size, ttl)
        
        if serializer == "json":
            self._serialize = json.dumps
            self._deserialize = json.loads
        else:
            self._serialize = pickle.dumps
            self._deserialize = pickle.loads
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_index()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        ext = ".json" if self.serializer == "json" else ".pkl"
        return self.cache_dir / f"{key_hash}{ext}"
    
    def _load_index(self):
        """Load cache index (files that exist on disk)."""
        # Could implement index tracking here
        pass
    
    def get(self, key: str, default: Any = None, 
            load_from_disk: bool = True) -> Any:
        """Get value from cache."""
        # Try memory first
        value = self.memory_cache.get(key, default)
        if value is not default:
            return value
        
        # Try disk if enabled
        if load_from_disk:
            return self._load_from_disk(key, default)
        
        return default
    
    def _load_from_disk(self, key: str, default: Any) -> Any:
        """Load value from disk."""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return default
        
        try:
            with open(cache_path, 'rb') as f:
                data = self._deserialize(f.read())
            
            # Put back in memory cache
            self.memory_cache.set(key, data)
            return data
        except Exception as e:
            logger.warning(f"Failed to load cache from disk: {e}")
            return default
    
    def set(self, key: str, value: Any, 
            persist: bool = True, ttl: Optional[float] = None):
        """Set value in cache."""
        self.memory_cache.set(key, value, ttl)
        
        if persist:
            self._save_to_disk(key, value)
    
    def _save_to_disk(self, key: str, value: Any):
        """Save value to disk."""
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'wb') as f:
                f.write(self._serialize(value))
        except Exception as e:
            logger.warning(f"Failed to save cache to disk: {e}")
    
    def delete(self, key: str):
        """Delete from both memory and disk."""
        self.memory_cache.delete(key)
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def clear(self):
        """Clear all cached data."""
        self.memory_cache.clear()
        for f in self.cache_dir.glob("*"):
            if f.is_file():
                f.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.memory_cache.get_stats()
        stats["disk_files"] = len(list(self.cache_dir.glob("*")))
        return stats


class CacheManager:
    """
    Unified cache manager with multiple cache tiers.
    """
    
    def __init__(self, 
                 l1_size: int = 100,      # In-memory LRU
                 l2_size: int = 1000,     # Persistent cache
                 ttl: float = 300):      # Default TTL
        self.l1_cache = LRUCache(l1_size, ttl)
        self.l2_cache = PersistentCache(
            cache_dir=".cache/l2",
            max_size=l2_size,
            ttl=ttl
        )
        self.default_ttl = ttl
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get from L1, then L2."""
        # Try L1 first
        value = self.l1_cache.get(key, None)
        if value is not None:
            return value
        
        # Try L2
        value = self.l2_cache.get(key, None)
        if value is not None:
            # Promote to L1
            self.l1_cache.set(key, value, self.default_ttl)
            return value
        
        return default
    
    def set(self, key: str, value: Any, 
            ttl: Optional[float] = None,
            persist: bool = True):
        """Set in both caches."""
        ttl = ttl or self.default_ttl
        self.l1_cache.set(key, value, ttl)
        if persist:
            self.l2_cache.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete from all caches."""
        self.l1_cache.delete(key)
        self.l2_cache.delete(key)
    
    def clear(self):
        """Clear all caches."""
        self.l1_cache.clear()
        self.l2_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics."""
        return {
            "l1": self.l1_cache.get_stats(),
            "l2": self.l2_cache.get_stats()
        }


# Decorator for caching function results

def cached(cache: Optional[Union[LRUCache, CacheManager]] = None,
           key_func: Optional[Callable] = None,
           ttl: Optional[float] = None):
    """
    Decorator to cache function results.
    
    Usage:
        @cached()
        def expensive_function(arg1, arg2):
            ...
    """
    _cache = cache or LRUCache(max_size=1000, ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__module__, func.__name__]
                key_parts.extend(str(a) for a in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result
        
        # Expose cache for inspection
        wrapper.cache = _cache
        return wrapper
    return decorator


# Global cache instance
_default_cache = CacheManager()


def get_default_cache() -> CacheManager:
    """Get the default cache manager."""
    return _default_cache


# Example usage

if __name__ == "__main__":
    # Basic LRU cache
    cache = LRUCache(max_size=3, ttl=5)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    
    print("Initial cache:", list(cache._cache.keys()))
    print("Get 'a':", cache.get("a"))
    print("After access:", list(cache._cache.keys()))
    
    cache.set("d", 4)  # Should evict 'b' (LRU)
    print("After adding 'd':", list(cache._cache.keys()))
    
    # Using decorator
    @cached(ttl=10)
    def expensive_computation(n):
        print(f"Computing {n}...")
        time.sleep(0.1)
        return n * 2
    
    print("\nFirst call:", expensive_computation(5))
    print("Second call (cached):", expensive_computation(5))
    print("Stats:", expensive_computation.cache.get_stats())
    
    # Persistent cache
    print("\n--- Persistent Cache ---")
    pcache = PersistentCache(cache_dir="/tmp/my_cache", serializer="json")
    pcache.set("user:1", {"name": "Alice", "age": 30})
    print("Persisted:", pcache.get("user:1"))
    pcache.clear()
