"""
Cache Service
Provides an in-memory caching layer for player and game stats using cachetools.
Cache entries are invalidated on write operations and also expire via TTL as a fallback.
"""
import threading
import logging
from cachetools import TTLCache

logger = logging.getLogger(__name__)

## Cache configuration
CACHE_TTL = 300       # 5-minute TTL as safety-net fallback
CACHE_MAX_SIZE = 100  # Maximum number of cached entries

## Thread-safe in-memory cache
_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL)
_cache_lock = threading.Lock()

## Cache key constants – namespaced as "stats:<category>:<name>"
CACHE_KEY_PLAYER_STATS = 'stats:player:stats'
CACHE_KEY_LEADERBOARD = 'stats:player:leaderboard'
CACHE_KEY_GAME_STATS = 'stats:games:game_stats'


def get_cached(key):
    '''Return the cached value for key, or None if missing or unavailable.'''
    try:
        with _cache_lock:
            return _cache.get(key)
    except Exception as e:
        logger.error(f'Cache get error for key {key}: {e}')
        return None


def set_cached(key, value):
    '''Store value in the cache under key. Silently ignores cache errors.'''
    try:
        with _cache_lock:
            _cache[key] = value
    except Exception as e:
        logger.error(f'Cache set error for key {key}: {e}')


def invalidate(key):
    '''Remove a specific key from the cache. Silently ignores cache errors.'''
    try:
        with _cache_lock:
            if key in _cache:
                del _cache[key]
    except Exception as e:
        logger.error(f'Cache invalidate error for key {key}: {e}')


def invalidate_stats():
    '''Invalidate all stats-related cache entries (prefix "stats:").
    Called whenever game or player data is written so the next read
    fetches fresh data from the API.'''
    try:
        with _cache_lock:
            keys_to_delete = [k for k in list(_cache.keys()) if k.startswith('stats:')]
            for key in keys_to_delete:
                del _cache[key]
        logger.info(f'Stats cache invalidated, removed {len(keys_to_delete)} entries')
    except Exception as e:
        logger.error(f'Cache invalidate_stats error: {e}')
