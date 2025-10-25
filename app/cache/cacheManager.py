"""
High-level caching manager for application-specific caching
"""
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import uuid

from app.cache.redisClient import redisClient
from app.utils.logger import setup_logger

logger = setup_logger()

class CacheManager:
    """
    Application-specific caching layer
    """
    
    # Cache key prefixes
    PREFIX_AGENT = "agent:"
    PREFIX_TASK = "task:"
    PREFIX_AGENT_STATUS = "agent_status:"
    PREFIX_TASK_QUEUE = "task_queue:"
    PREFIX_METRICS = "metrics:"
    PREFIX_SESSION = "session:"
    
    # Default TTL values (in seconds)
    TTL_SHORT = 300  # 5 minutes
    TTL_MEDIUM = 1800  # 30 minutes
    TTL_LONG = 3600  # 1 hour
    TTL_DAY = 86400  # 24 hours
    
    # ========== Agent Caching ==========
    
    @staticmethod
    def cache_agent_status(agent_id: uuid.UUID, status_data: Dict) -> bool:
        """
        Cache agent status for quick access
        
        Args:
            agent_id: Agent UUID
            status_data: Dict with status, last_heartbeat, etc.
        """
        key = f"{CacheManager.PREFIX_AGENT_STATUS}{agent_id}"
        status_data['cached_at'] = datetime.utcnow().isoformat()
        return redisClient.set(key, status_data, expire=CacheManager.TTL_SHORT)
    
    @staticmethod
    def get_agent_status(agent_id: uuid.UUID) -> Optional[Dict]:
        """Get cached agent status"""
        key = f"{CacheManager.PREFIX_AGENT_STATUS}{agent_id}"
        return redisClient.get(key, as_json=True)
    
    @staticmethod
    def cache_all_agent_statuses(agents_data: List[Dict]) -> bool:
        """Cache multiple agent statuses at once"""
        try:
            for agent in agents_data:
                agent_id = agent.get('agent_id')
                if agent_id:
                    CacheManager.cache_agent_status(agent_id, agent)
            return True
        except Exception as e:
            logger.error(f"Error caching agent statuses: {e}")
            return False
    
    @staticmethod
    def get_active_agents() -> List[str]:
        """Get list of currently active agent IDs from cache"""
        return list(redisClient.smembers("active_agents"))
    
    @staticmethod
    def add_active_agent(agent_id: uuid.UUID) -> int:
        """Add agent to active agents set"""
        return redisClient.sadd("active_agents", str(agent_id))
    
    @staticmethod
    def remove_active_agent(agent_id: uuid.UUID) -> int:
        """Remove agent from active agents set"""
        return redisClient.srem("active_agents", str(agent_id))
    
    # ========== Task Queue Caching ==========
    
    @staticmethod
    def add_pending_task(agent_id: uuid.UUID, task_data: Dict) -> int:
        """Add task to agent's pending queue"""
        key = f"{CacheManager.PREFIX_TASK_QUEUE}{agent_id}"
        return redisClient.rpush(key, task_data)
    
    @staticmethod
    def get_pending_tasks(agent_id: uuid.UUID, limit: int = 10) -> List[Dict]:
        """Get pending tasks for agent from cache"""
        key = f"{CacheManager.PREFIX_TASK_QUEUE}{agent_id}"
        return redisClient.lrange(key, 0, limit - 1, as_json=True)
    
    @staticmethod
    def pop_pending_task(agent_id: uuid.UUID) -> Optional[Dict]:
        """Pop next pending task for agent"""
        key = f"{CacheManager.PREFIX_TASK_QUEUE}{agent_id}"
        return redisClient.lpop(key, as_json=True)
    
    @staticmethod
    def clear_pending_tasks(agent_id: uuid.UUID) -> bool:
        """Clear all pending tasks for agent"""
        key = f"{CacheManager.PREFIX_TASK_QUEUE}{agent_id}"
        return redisClient.delete(key) > 0
    
    # ========== Metrics Caching ==========
    
    @staticmethod
    def increment_metric(metric_name: str, value: int = 1) -> int:
        """Increment a metric counter"""
        key = f"{CacheManager.PREFIX_METRICS}{metric_name}"
        return redisClient.client.incr(key, value)
    
    @staticmethod
    def get_metric(metric_name: str) -> int:
        """Get metric value"""
        key = f"{CacheManager.PREFIX_METRICS}{metric_name}"
        value = redisClient.get(key)
        return int(value) if value else 0
    
    @staticmethod
    def cache_daily_stats(date: str, stats: Dict) -> bool:
        """Cache daily statistics"""
        key = f"{CacheManager.PREFIX_METRICS}daily:{date}"
        return redisClient.set(key, stats, expire=CacheManager.TTL_DAY * 7)
    
    @staticmethod
    def get_daily_stats(date: str) -> Optional[Dict]:
        """Get cached daily statistics"""
        key = f"{CacheManager.PREFIX_METRICS}daily:{date}"
        return redisClient.get(key, as_json=True)
    
    # ========== Real-time Transfer Tracking ==========
    
    @staticmethod
    def start_transfer(task_id: uuid.UUID, transfer_info: Dict) -> bool:
        """Mark transfer as in progress"""
        key = f"transfer:active:{task_id}"
        transfer_info['started_at'] = datetime.utcnow().isoformat()
        return redisClient.set(key, transfer_info, expire=CacheManager.TTL_LONG)
    
    @staticmethod
    def update_transfer_progress(task_id: uuid.UUID, bytes_transferred: int, total_bytes: int) -> bool:
        """Update transfer progress"""
        key = f"transfer:active:{task_id}"
        progress_data = {
            'bytes_transferred': bytes_transferred,
            'total_bytes': total_bytes,
            'progress_percent': (bytes_transferred / total_bytes * 100) if total_bytes > 0 else 0,
            'updated_at': datetime.utcnow().isoformat()
        }
        return redisClient.hset(key, 'progress', progress_data)
    
    @staticmethod
    def complete_transfer(task_id: uuid.UUID) -> bool:
        """Remove completed transfer from active tracking"""
        key = f"transfer:active:{task_id}"
        return redisClient.delete(key) > 0
    
    @staticmethod
    def get_active_transfers() -> List[str]:
        """Get all active transfer IDs"""
        return redisClient.keys("transfer:active:*")
    
    # ========== Session Management ==========
    
    @staticmethod
    def create_session(user_id: str, session_data: Dict, ttl: int = None) -> str:
        """Create user session"""
        session_id = str(uuid.uuid4())
        key = f"{CacheManager.PREFIX_SESSION}{session_id}"
        session_data['user_id'] = user_id
        session_data['created_at'] = datetime.utcnow().isoformat()
        redisClient.set(key, session_data, expire=ttl or CacheManager.TTL_DAY)
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"{CacheManager.PREFIX_SESSION}{session_id}"
        return redisClient.get(key, as_json=True)
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete session"""
        key = f"{CacheManager.PREFIX_SESSION}{session_id}"
        return redisClient.delete(key) > 0
    
    # ========== Rate Limiting ==========
    
    @staticmethod
    def check_rate_limit(identifier: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if identifier is within rate limit
        
        Args:
            identifier: User ID, IP address, or other identifier
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            True if within limit, False if exceeded
        """
        key = f"ratelimit:{identifier}"
        current = redisClient.client.incr(key)
        
        if current == 1:
            # First request, set expiry
            redisClient.expire(key, window_seconds)
        
        return current <= max_requests
    
    @staticmethod
    def get_rate_limit_remaining(identifier: str, max_requests: int) -> int:
        """Get remaining requests in current window"""
        key = f"ratelimit:{identifier}"
        current = redisClient.get(key)
        current = int(current) if current else 0
        return max(0, max_requests - current)
    
    # ========== Distributed Locks ==========
    
    @staticmethod
    def acquire_lock(lock_name: str, timeout: int = 10) -> bool:
        """
        Acquire distributed lock
        
        Args:
            lock_name: Name of lock
            timeout: Lock timeout in seconds
        
        Returns:
            True if lock acquired, False otherwise
        """
        key = f"lock:{lock_name}"
        return redisClient.client.set(key, "1", nx=True, ex=timeout)
    
    @staticmethod
    def release_lock(lock_name: str) -> bool:
        """Release distributed lock"""
        key = f"lock:{lock_name}"
        return redisClient.delete(key) > 0
    
    # ========== Leaderboard (Sorted Set) ==========
    
    @staticmethod
    def update_agent_ranking(agent_id: uuid.UUID, score: float) -> int:
        """Update agent performance score"""
        return redisClient.zadd("agent_leaderboard", {str(agent_id): score})
    
    @staticmethod
    def get_top_agents(limit: int = 10) -> List:
        """Get top performing agents"""
        return redisClient.zrange("agent_leaderboard", 0, limit - 1, withscores=True)
    
    # ========== Utility Methods ==========
    
    @staticmethod
    def clear_cache(pattern: str = None) -> int:
        """
        Clear cache entries matching pattern
        
        Args:
            pattern: Redis key pattern (e.g., "agent:*")
        
        Returns:
            Number of keys deleted
        """
        if pattern:
            keys = redisClient.keys(pattern)
            if keys:
                return redisClient.delete(*keys)
        return 0
    
    @staticmethod
    def get_cache_stats() -> Dict:
        """Get cache statistics"""
        info = redisClient.info('stats')
        return {
            'total_keys': redisClient.dbsize(),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'uptime_days': info.get('uptime_in_days', 0)
        }

# Export singleton
cache_manager = CacheManager()
