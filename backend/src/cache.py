"""
Simple in-memory cache for dashboard statistics
"""
import time

# Cache storage: {cache_key: (data, timestamp)}
_cache = {}
_cache_ttl = 5  # seconds


def get_cache_key(user_id: int, cache_type: str = "dashboard_stats") -> str:
    """Generate cache key"""
    return f"{cache_type}_{user_id}"


def get_cached(user_id: int, cache_type: str = "dashboard_stats"):
    """Get cached data if still valid"""
    cache_key = get_cache_key(user_id, cache_type)
    current_time = time.time()
    
    if cache_key in _cache:
        cached_data, cached_time = _cache[cache_key]
        if current_time - cached_time < _cache_ttl:
            return cached_data
    
    return None


def set_cache(user_id: int, data, cache_type: str = "dashboard_stats"):
    """Cache data for user"""
    cache_key = get_cache_key(user_id, cache_type)
    current_time = time.time()
    
    _cache[cache_key] = (data, current_time)
    
    # Clean old cache entries (keep only last 10 users)
    if len(_cache) > 10:
        oldest_key = min(_cache.keys(), key=lambda k: _cache[k][1])
        del _cache[oldest_key]


def clear_cache(user_id: int = None, cache_type: str = "dashboard_stats"):
    """Clear cache for a specific user or all users"""
    if user_id:
        cache_key = get_cache_key(user_id, cache_type)
        if cache_key in _cache:
            del _cache[cache_key]
    else:
        # Clear all caches of this type
        keys_to_remove = [k for k in _cache.keys() if k.startswith(cache_type)]
        for key in keys_to_remove:
            del _cache[key]


def clear_all_cache():
    """Clear all cached data"""
    _cache.clear()

