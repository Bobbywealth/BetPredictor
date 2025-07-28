import streamlit as st
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable
import functools

class PerformanceCache:
    """High-performance caching system for SportsBet Pro"""
    
    def __init__(self):
        if 'performance_cache' not in st.session_state:
            st.session_state.performance_cache = {}
        if 'cache_stats' not in st.session_state:
            st.session_state.cache_stats = {
                'hits': 0,
                'misses': 0,
                'total_time_saved': 0
            }
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_string = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str, max_age: int = 300) -> Optional[Any]:
        """Get cached value if still valid"""
        cache_entry = st.session_state.performance_cache.get(key)
        
        if cache_entry:
            cached_time = cache_entry.get('timestamp', 0)
            if time.time() - cached_time < max_age:
                st.session_state.cache_stats['hits'] += 1
                return cache_entry['data']
            else:
                # Remove expired entry
                del st.session_state.performance_cache[key]
        
        st.session_state.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, data: Any, execution_time: float = 0):
        """Store data in cache"""
        st.session_state.performance_cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        if execution_time > 0:
            st.session_state.cache_stats['total_time_saved'] += execution_time
        
        # Keep cache size manageable
        if len(st.session_state.performance_cache) > 100:
            # Remove oldest entries
            oldest_keys = sorted(
                st.session_state.performance_cache.keys(),
                key=lambda k: st.session_state.performance_cache[k]['timestamp']
            )[:20]
            
            for old_key in oldest_keys:
                del st.session_state.performance_cache[old_key]
    
    def cached_function(self, max_age: int = 300):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key, max_age)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                self.set(cache_key, result, execution_time)
                return result
            
            return wrapper
        return decorator
    
    def clear_expired(self):
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in st.session_state.performance_cache.items():
            if current_time - entry['timestamp'] > 3600:  # 1 hour
                expired_keys.append(key)
        
        for key in expired_keys:
            del st.session_state.performance_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = st.session_state.cache_stats.copy()
        total_requests = stats['hits'] + stats['misses']
        
        if total_requests > 0:
            stats['hit_rate'] = (stats['hits'] / total_requests) * 100
        else:
            stats['hit_rate'] = 0
        
        stats['cache_size'] = len(st.session_state.performance_cache)
        return stats

# Global cache instance
performance_cache = PerformanceCache()