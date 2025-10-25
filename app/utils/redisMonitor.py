"""
Redis monitoring utilities
"""
from app.cache.redis_client import redis_client
from app.utils.logger import setup_logger

logger = setup_logger()

class RedisMonitor:
    @staticmethod
    def get_memory_usage():
        """Get Redis memory usage"""
        info = redis_client.info('memory')
        return {
            'used_memory_human': info.get('used_memory_human'),
            'used_memory_peak_human': info.get('used_memory_peak_human'),
            'mem_fragmentation_ratio': info.get('mem_fragmentation_ratio')
        }
    
    @staticmethod
    def get_connection_stats():
        """Get connection statistics"""
        info = redis_client.info('clients')
        return {
            'connected_clients': info.get('connected_clients'),
            'client_longest_output_list': info.get('client_longest_output_list'),
            'client_biggest_input_buf': info.get('client_biggest_input_buf')
        }
    
    @staticmethod
    def get_performance_stats():
        """Get performance statistics"""
        info = redis_client.info('stats')
        return {
            'total_commands_processed': info.get('total_commands_processed'),
            'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec'),
            'total_net_input_bytes': info.get('total_net_input_bytes'),
            'total_net_output_bytes': info.get('total_net_output_bytes')
        }
    
    @staticmethod
    def health_check():
        """Comprehensive health check"""
        try:
            # Ping test
            if not redis_client.ping():
                return {'status': 'unhealthy', 'reason': 'Ping failed'}
            
            # Memory check
            memory = RedisMonitor.get_memory_usage()
            
            # Connection check
            connections = RedisMonitor.get_connection_stats()
            
            # Performance check
            performance = RedisMonitor.get_performance_stats()
            
            return {
                'status': 'healthy',
                'memory': memory,
                'connections': connections,
                'performance': performance
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {'status': 'unhealthy', 'reason': str(e)}
