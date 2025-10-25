"""
Redis client for caching and real-time data storage
"""
import redis
import json
from typing import Any, Optional, Dict, List
from datetime import timedelta
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger()

class RedisClient:
    """
    Redis client wrapper with connection pooling
    """
    
    def __init__(self):
        """Initialize Redis connection pool"""
        self.pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=50,
            decode_responses=True  # Automatically decode bytes to strings
        )
        self.client = redis.Redis(connection_pool=self.pool)
        self._test_connection()
    
    def _test_connection(self):
        """Test Redis connection"""
        try:
            self.client.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    # ========== Basic Operations ==========
    
    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        Set a key-value pair
        
        Args:
            key: Redis key
            value: Value (will be JSON serialized if dict/list)
            expire: Expiration time in seconds
        
        Returns:
            True if successful
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = self.client.set(key, value)
            
            if expire:
                self.client.expire(key, expire)
            
            return result
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    def get(self, key: str, as_json: bool = False) -> Optional[Any]:
        """
        Get value by key
        
        Args:
            key: Redis key
            as_json: If True, parse value as JSON
        
        Returns:
            Value or None if not found
        """
        try:
            value = self.client.get(key)
            
            if value is None:
                return None
            
            if as_json:
                return json.loads(value)
            
            return value
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys
        
        Returns:
            Number of keys deleted
        """
        try:
            return self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key"""
        try:
            return self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """
        Get remaining time to live for key
        
        Returns:
            Seconds remaining, -1 if no expiry, -2 if key doesn't exist
        """
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key '{key}': {e}")
            return -2
    
    # ========== Hash Operations ==========
    
    def hset(self, name: str, key: str, value: Any) -> int:
        """Set field in hash"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis HSET error: {e}")
            return 0
    
    def hget(self, name: str, key: str, as_json: bool = False) -> Optional[Any]:
        """Get field from hash"""
        try:
            value = self.client.hget(name, key)
            if value and as_json:
                return json.loads(value)
            return value
        except Exception as e:
            logger.error(f"Redis HGET error: {e}")
            return None
    
    def hgetall(self, name: str, as_json: bool = False) -> Dict:
        """Get all fields from hash"""
        try:
            data = self.client.hgetall(name)
            if as_json:
                return {k: json.loads(v) for k, v in data.items()}
            return data
        except Exception as e:
            logger.error(f"Redis HGETALL error: {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """Delete fields from hash"""
        try:
            return self.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis HDEL error: {e}")
            return 0
    
    def hexists(self, name: str, key: str) -> bool:
        """Check if field exists in hash"""
        try:
            return self.client.hexists(name, key)
        except Exception as e:
            logger.error(f"Redis HEXISTS error: {e}")
            return False
    
    # ========== List Operations ==========
    
    def lpush(self, name: str, *values: Any) -> int:
        """Push values to head of list"""
        try:
            serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
            return self.client.lpush(name, *serialized)
        except Exception as e:
            logger.error(f"Redis LPUSH error: {e}")
            return 0
    
    def rpush(self, name: str, *values: Any) -> int:
        """Push values to tail of list"""
        try:
            serialized = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
            return self.client.rpush(name, *serialized)
        except Exception as e:
            logger.error(f"Redis RPUSH error: {e}")
            return 0
    
    def lpop(self, name: str, as_json: bool = False) -> Optional[Any]:
        """Pop value from head of list"""
        try:
            value = self.client.lpop(name)
            if value and as_json:
                return json.loads(value)
            return value
        except Exception as e:
            logger.error(f"Redis LPOP error: {e}")
            return None
    
    def rpop(self, name: str, as_json: bool = False) -> Optional[Any]:
        """Pop value from tail of list"""
        try:
            value = self.client.rpop(name)
            if value and as_json:
                return json.loads(value)
            return value
        except Exception as e:
            logger.error(f"Redis RPOP error: {e}")
            return None
    
    def lrange(self, name: str, start: int, end: int, as_json: bool = False) -> List:
        """Get range of elements from list"""
        try:
            values = self.client.lrange(name, start, end)
            if as_json:
                return [json.loads(v) for v in values]
            return values
        except Exception as e:
            logger.error(f"Redis LRANGE error: {e}")
            return []
    
    def llen(self, name: str) -> int:
        """Get length of list"""
        try:
            return self.client.llen(name)
        except Exception as e:
            logger.error(f"Redis LLEN error: {e}")
            return 0
    
    # ========== Set Operations ==========
    
    def sadd(self, name: str, *values: Any) -> int:
        """Add members to set"""
        try:
            return self.client.sadd(name, *values)
        except Exception as e:
            logger.error(f"Redis SADD error: {e}")
            return 0
    
    def smembers(self, name: str) -> set:
        """Get all members of set"""
        try:
            return self.client.smembers(name)
        except Exception as e:
            logger.error(f"Redis SMEMBERS error: {e}")
            return set()
    
    def sismember(self, name: str, value: Any) -> bool:
        """Check if value is member of set"""
        try:
            return self.client.sismember(name, value)
        except Exception as e:
            logger.error(f"Redis SISMEMBER error: {e}")
            return False
    
    def srem(self, name: str, *values: Any) -> int:
        """Remove members from set"""
        try:
            return self.client.srem(name, *values)
        except Exception as e:
            logger.error(f"Redis SREM error: {e}")
            return 0
    
    # ========== Sorted Set Operations ==========
    
    def zadd(self, name: str, mapping: Dict[str, float]) -> int:
        """Add members with scores to sorted set"""
        try:
            return self.client.zadd(name, mapping)
        except Exception as e:
            logger.error(f"Redis ZADD error: {e}")
            return 0
    
    def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> List:
        """Get range from sorted set"""
        try:
            return self.client.zrange(name, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis ZRANGE error: {e}")
            return []
    
    def zrem(self, name: str, *values: Any) -> int:
        """Remove members from sorted set"""
        try:
            return self.client.zrem(name, *values)
        except Exception as e:
            logger.error(f"Redis ZREM error: {e}")
            return 0
    
    # ========== Pub/Sub Operations ==========
    
    def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            return self.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis PUBLISH error: {e}")
            return 0
    
    def subscribe(self, *channels: str):
        """Subscribe to channels (returns pubsub object)"""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            logger.error(f"Redis SUBSCRIBE error: {e}")
            return None
    
    # ========== Pattern Matching ==========
    
    def keys(self, pattern: str) -> List[str]:
        """Get all keys matching pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            return []
    
    def scan_iter(self, match: str = None, count: int = 100):
        """Iterate over keys matching pattern (memory efficient)"""
        try:
            return self.client.scan_iter(match=match, count=count)
        except Exception as e:
            logger.error(f"Redis SCAN_ITER error: {e}")
            return iter([])
    
    # ========== Utility Methods ==========
    
    def flushdb(self):
        """Clear current database - USE WITH CAUTION"""
        try:
            return self.client.flushdb()
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    def ping(self) -> bool:
        """Test connection"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False
    
    def info(self, section: str = None) -> Dict:
        """Get server info"""
        try:
            return self.client.info(section)
        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            return {}
    
    def dbsize(self) -> int:
        """Get number of keys in database"""
        try:
            return self.client.dbsize()
        except Exception as e:
            logger.error(f"Redis DBSIZE error: {e}")
            return 0
    
    def close(self):
        """Close Redis connection"""
        try:
            self.client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Redis CLOSE error: {e}")

# Create singleton instance
redis_client = RedisClient()
