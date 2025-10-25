"""
General helper utility functions
"""
import hashlib
import secrets
import string
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import json
from pathlib import Path
import platform
import psutil
import socket


class Helpers:
    """
    Collection of helper methods
    """
    
    # ========== String Helpers ==========
    
    @staticmethod
    def generate_random_string(length: int = 32, include_special: bool = False) -> str:
        """
        Generate secure random string
        
        Example:
            generate_random_string(16)  # "aB3xYz9mN2qW5tP7"
        """
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += string.punctuation
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate secure hex token
        
        Example:
            generate_token()  # "a1b2c3d4e5f6..."
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert string to URL-friendly slug
        
        Example:
            slugify("Hello World!")  # "hello-world"
        """
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    @staticmethod
    def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
        """
        Truncate string to max length
        
        Example:
            truncate_string("Long text here", 10)  # "Long te..."
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def camel_to_snake(text: str) -> str:
        """
        Convert camelCase to snake_case
        
        Example:
            camel_to_snake("camelCaseString")  # "camel_case_string"
        """
        import re
        text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()
    
    @staticmethod
    def snake_to_camel(text: str) -> str:
        """
        Convert snake_case to camelCase
        
        Example:
            snake_to_camel("snake_case_string")  # "snakeCaseString"
        """
        components = text.split('_')
        return components + ''.join(x.title() for x in components[1:])
    
    # ========== Hash & Encryption Helpers ==========
    
    @staticmethod
    def calculate_hash(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        Calculate hash of data
        
        Example:
            calculate_hash("hello")  # "2cf24dba5..."
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data)
        return hash_obj.hexdigest()
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256', chunk_size: int = 8192) -> str:
        """
        Calculate hash of file
        
        Example:
            calculate_file_hash("/path/to/file.txt")
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def mask_sensitive_data(text: str, visible_chars: int = 4, mask_char: str = '*') -> str:
        """
        Mask sensitive data (e.g., passwords, tokens)
        
        Example:
            mask_sensitive_data("secret123", 3)  # "sec******"
        """
        if len(text) <= visible_chars:
            return mask_char * len(text)
        
        return text[:visible_chars] + mask_char * (len(text) - visible_chars)
    
    # ========== Date/Time Helpers ==========
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        Format datetime object
        
        Example:
            format_datetime(datetime.now())  # "2025-10-22 10:30:00"
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(date_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> datetime:
        """
        Parse datetime string
        
        Example:
            parse_datetime("2025-10-22 10:30:00")
        """
        return datetime.strptime(date_str, format_str)
    
    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """
        Get human-readable time ago string
        
        Example:
            get_time_ago(datetime.now() - timedelta(hours=2))  # "2 hours ago"
        """
        now = datetime.utcnow()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds / 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hours ago"
        elif seconds < 604800:
            return f"{int(seconds / 86400)} days ago"
        elif seconds < 2592000:
            return f"{int(seconds / 604800)} weeks ago"
        elif seconds < 31536000:
            return f"{int(seconds / 2592000)} months ago"
        else:
            return f"{int(seconds / 31536000)} years ago"
    
    @staticmethod
    def add_time(dt: datetime, **kwargs) -> datetime:
        """
        Add time to datetime
        
        Example:
            add_time(datetime.now(), hours=2, minutes=30)
        """
        return dt + timedelta(**kwargs)
    
    # ========== File Size Helpers ==========
    
    @staticmethod
    def format_file_size(size_bytes: int, decimal_places: int = 2) -> str:
        """
        Format file size in human-readable format
        
        Example:
            format_file_size(1536)        # "1.50 KB"
            format_file_size(1073741824)  # "1.00 GB"
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.{decimal_places}f} {units[unit_index]}"
    
    @staticmethod
    def parse_file_size(size_str: str) -> int:
        """
        Parse human-readable file size to bytes
        
        Example:
            parse_file_size("1.5 GB")  # 1610612736
            parse_file_size("500 MB")  # 524288000
        """
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 
                'TB': 1024**4, 'PB': 1024**5}
        
        size_str = size_str.strip().upper()
        
        for unit, multiplier in units.items():
            if unit in size_str:
                number = float(size_str.replace(unit, '').strip())
                return int(number * multiplier)
        
        return int(float(size_str))
    
    # ========== JSON Helpers ==========
    
    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """
        Safely load JSON, return default on error
        
        Example:
            safe_json_loads('{"key": "value"}')  # {'key': 'value'}
            safe_json_loads('invalid', {})       # {}
        """
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def safe_json_dumps(obj: Any, default: str = '{}', indent: int = None) -> str:
        """
        Safely dump JSON, return default on error
        
        Example:
            safe_json_dumps({'key': 'value'})  # '{"key": "value"}'
        """
        try:
            return json.dumps(obj, indent=indent, default=str)
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def pretty_json(obj: Any) -> str:
        """
        Format JSON with indentation
        
        Example:
            pretty_json({'key': 'value'})
        """
        return json.dumps(obj, indent=2, default=str)
    
    # ========== Dictionary Helpers ==========
    
    @staticmethod
    def deep_get(dictionary: Dict, keys: str, default: Any = None) -> Any:
        """
        Get nested dictionary value using dot notation
        
        Example:
            data = {'a': {'b': {'c': 123}}}
            deep_get(data, 'a.b.c')  # 123
            deep_get(data, 'a.b.x', 0)  # 0
        """
        keys_list = keys.split('.')
        value = dictionary
        
        for key in keys_list:
            try:
                value = value[key]
            except (KeyError, TypeError, IndexError):
                return default
        
        return value
    
    @staticmethod
    def deep_set(dictionary: Dict, keys: str, value: Any) -> None:
        """
        Set nested dictionary value using dot notation
        
        Example:
            data = {}
            deep_set(data, 'a.b.c', 123)
            # data = {'a': {'b': {'c': 123}}}
        """
        keys_list = keys.split('.')
        current = dictionary
        
        for key in keys_list[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        current[keys_list[-1]] = value
    
    @staticmethod
    def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        Flatten nested dictionary
        
        Example:
            flatten_dict({'a': {'b': 1, 'c': 2}})
            # {'a.b': 1, 'a.c': 2}
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(Helpers.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def merge_dicts(*dicts: Dict) -> Dict:
        """
        Merge multiple dictionaries
        
        Example:
            merge_dicts({'a': 1}, {'b': 2}, {'c': 3})
            # {'a': 1, 'b': 2, 'c': 3}
        """
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    # ========== List Helpers ==========
    
    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """
        Split list into chunks
        
        Example:
            chunk_list([1,2,3,4,5], 2)  # [[1,2], [3,4], ]
        """
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def deduplicate_list(lst: List, key: Optional[callable] = None) -> List:
        """
        Remove duplicates from list
        
        Example:
            deduplicate_list([1, 2, 2, 3, 3, 3])  # [1, 2, 3]
        """
        if key:
            seen = set()
            result = []
            for item in lst:
                k = key(item)
                if k not in seen:
                    seen.add(k)
                    result.append(item)
            return result
        return list(dict.fromkeys(lst))
    
    # ========== System Information Helpers ==========
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get system information
        
        Returns:
            Dict with hostname, IP, OS, CPU, memory, disk
        """
        return {
            'hostname': socket.gethostname(),
            'ip_address': Helpers.get_local_ip(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'memory_percent': psutil.virtual_memory().percent,
            'disk_total': psutil.disk_usage('/').total,
            'disk_used': psutil.disk_usage('/').used,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    @staticmethod
    def get_local_ip() -> str:
        """
        Get local IP address
        
        Example:
            get_local_ip()  # "192.168.1.100"
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def get_mac_address() -> str:
        """
        Get MAC address
        
        Example:
            get_mac_address()  # "00:11:22:33:44:55"
        """
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        return mac
    
    # ========== Retry Helper ==========
    
    @staticmethod
    def retry(
        func: callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Retry function with exponential backoff
        
        Example:
            result = retry(my_function, max_attempts=5, delay=1.0)
        """
        import time
        
        for attempt in range(max_attempts):
            try:
                return func()
            except exceptions as e:
                if attempt == max_attempts - 1:
                    raise
                
                wait_time = delay * (backoff ** attempt)
                time.sleep(wait_time)
    
    # ========== Pagination Helper ==========
    
    @staticmethod
    def paginate(items: List, page: int = 1, per_page: int = 10) -> Dict:
        """
        Paginate list of items
        
        Returns:
            Dict with items, total, page, per_page, total_pages
        
        Example:
            result = paginate([1,2,3,4,5], page=1, per_page=2)
            # {'items': [1,2], 'total': 5, 'page': 1, ...}
        """
        total = len(items)
        total_pages = (total + per_page - 1) // per_page
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': items[start:end],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    
    # ========== Conversion Helpers ==========
    
    @staticmethod
    def bytes_to_mb(bytes_value: int) -> float:
        """Convert bytes to megabytes"""
        return bytes_value / (1024 ** 2)
    
    @staticmethod
    def mb_to_bytes(mb_value: float) -> int:
        """Convert megabytes to bytes"""
        return int(mb_value * (1024 ** 2))
    
    @staticmethod
    def seconds_to_human(seconds: int) -> str:
        """
        Convert seconds to human-readable format
        
        Example:
            seconds_to_human(3665)  # "1h 1m 5s"
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)


# Convenience functions
def get_env(key: str, default: Any = None) -> Any:
    """
    Get environment variable with default
    
    Example:
        db_host = get_env('DB_HOST', 'localhost')
    """
    import os
    return os.getenv(key, default)


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safely divide, return default if division by zero
    
    Example:
        safe_divide(10, 2)  # 5.0
        safe_divide(10, 0)  # 0.0
    """
    try:
        return a / b
    except ZeroDivisionError:
        return default


# Example usage
if __name__ == "__main__":
    # Test helpers
    print("Random string:", Helpers.generate_random_string(16))
    print("Token:", Helpers.generate_token(16))
    print("Slug:", Helpers.slugify("Hello World!"))
    print("File size:", Helpers.format_file_size(1073741824))
    print("Time ago:", Helpers.get_time_ago(datetime.now() - timedelta(hours=2)))
    print("System info:", Helpers.get_system_info())
    print("Masked:", Helpers.mask_sensitive_data("secret123", 3))
    
    # Test pagination
    items = list(range(1, 26))
    page_result = Helpers.paginate(items, page=2, per_page=5)
    print("Paginated:", page_result)
