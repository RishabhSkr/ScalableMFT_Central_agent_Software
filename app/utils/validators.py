"""
Data validation utilities
"""
import re
import ipaddress
from typing import Optional, List, Any, Dict
from datetime import datetime
from pathlib import Path
import uuid


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class Validators:
    """
    Collection of validation methods
    """
    
    # Regular expressions
    HOSTNAME_REGEX = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$')
    MAC_ADDRESS_REGEX = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    CRON_REGEX = re.compile(r'^(\*|([0-5]?\d)) (\*|(?\d|2[0-3])) (\*|(?\d|2\d|3)) (\*|([1-9]|1[0-2])) (\*|([0-6]))$')
    
    # ========== Network Validation ==========
    
    @staticmethod
    def validate_hostname(hostname: str) -> bool:
        """
        Validate hostname format
        
        Rules:
        - 1-63 characters
        - Alphanumeric and hyphens
        - Cannot start or end with hyphen
        
        Example:
            validate_hostname("server-01")  # True
            validate_hostname("-invalid")   # False
        """
        if not hostname or len(hostname) > 63:
            return False
        return bool(Validators.HOSTNAME_REGEX.match(hostname))
    
    @staticmethod
    def validate_ip_address(ip: str, version: Optional[int] = None) -> bool:
        """
        Validate IP address (IPv4 or IPv6)
        
        Args:
            ip: IP address string
            version: 4 for IPv4, 6 for IPv6, None for either
        
        Example:
            validate_ip_address("192.168.1.1")      # True
            validate_ip_address("2001:db8::1")      # True
            validate_ip_address("999.999.999.999")  # False
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            if version:
                return ip_obj.version == version
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_mac_address(mac: str) -> bool:
        """
        Validate MAC address format
        
        Accepts:
        - Colon separated: 00:11:22:33:44:55
        - Hyphen separated: 00-11-22-33-44-55
        
        Example:
            validate_mac_address("00:11:22:33:44:55")  # True
            validate_mac_address("00-11-22-33-44-55")  # True
            validate_mac_address("invalid")            # False
        """
        if not mac:
            return False
        return bool(Validators.MAC_ADDRESS_REGEX.match(mac))
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """
        Validate port number (1-65535)
        
        Example:
            validate_port(8080)   # True
            validate_port(80000)  # False
        """
        return isinstance(port, int) and 1 <= port <= 65535
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format
        
        Example:
            validate_url("https://example.com")     # True
            validate_url("ftp://ftp.example.com")   # True
            validate_url("not a url")               # False
        """
        url_pattern = re.compile(
            r'^(https?|ftp)://'  # Protocol
            r'([a-zA-Z0-9.-]+)'  # Domain
            r'(:\d+)?'           # Optional port
            r'(/.*)?$'           # Optional path
        )
        return bool(url_pattern.match(url))
    
    # ========== String Validation ==========
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format
        
        Example:
            validate_email("user@example.com")  # True
            validate_email("invalid.email")     # False
        """
        if not email:
            return False
        return bool(Validators.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_string_length(
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Validate string length within bounds
        
        Example:
            validate_string_length("test", min_length=2, max_length=10)  # True
            validate_string_length("x", min_length=2)                    # False
        """
        if not isinstance(value, str):
            return False
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            return False
        
        if max_length is not None and length > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_alphanumeric(value: str, allow_spaces: bool = False) -> bool:
        """
        Validate alphanumeric string
        
        Example:
            validate_alphanumeric("Test123")           # True
            validate_alphanumeric("Test 123", True)    # True
            validate_alphanumeric("Test@123")          # False
        """
        if not value:
            return False
        
        if allow_spaces:
            return value.replace(' ', '').isalnum()
        
        return value.isalnum()
    
    @staticmethod
    def validate_uuid(value: str) -> bool:
        """
        Validate UUID format
        
        Example:
            validate_uuid("123e4567-e89b-12d3-a456-426614174000")  # True
            validate_uuid("invalid-uuid")                          # False
        """
        try:
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False
    
    # ========== File System Validation ==========
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = False) -> bool:
        """
        Validate file path format and optionally existence
        
        Example:
            validate_file_path("/home/user/file.txt")              # True
            validate_file_path("/home/user/file.txt", True)        # True if exists
            validate_file_path("C:\\Users\\file.txt")              # True (Windows)
        """
        try:
            path_obj = Path(path)
            
            if must_exist:
                return path_obj.exists() and path_obj.is_file()
            
            # Check if path format is valid
            return len(str(path_obj)) > 0
        except Exception:
            return False
    
    @staticmethod
    def validate_directory_path(path: str, must_exist: bool = False) -> bool:
        """
        Validate directory path format and optionally existence
        
        Example:
            validate_directory_path("/home/user/")        # True
            validate_directory_path("/home/user/", True)  # True if exists
        """
        try:
            path_obj = Path(path)
            
            if must_exist:
                return path_obj.exists() and path_obj.is_dir()
            
            return len(str(path_obj)) > 0
        except Exception:
            return False
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Validate file has allowed extension
        
        Example:
            validate_file_extension("data.csv", [".csv", ".txt"])  # True
            validate_file_extension("data.exe", [".csv", ".txt"])  # False
        """
        if not filename:
            return False
        
        file_ext = Path(filename).suffix.lower()
        allowed_exts = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                       for ext in allowed_extensions]
        
        return file_ext in allowed_exts
    
    # ========== Numerical Validation ==========
    
    @staticmethod
    def validate_number_range(
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> bool:
        """
        Validate number within range
        
        Example:
            validate_number_range(50, min_value=0, max_value=100)   # True
            validate_number_range(150, min_value=0, max_value=100)  # False
        """
        if not isinstance(value, (int, float)):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
    
    @staticmethod
    def validate_positive(value: float) -> bool:
        """
        Validate number is positive
        
        Example:
            validate_positive(10)   # True
            validate_positive(-5)   # False
        """
        return isinstance(value, (int, float)) and value > 0
    
    @staticmethod
    def validate_percentage(value: float) -> bool:
        """
        Validate percentage (0-100)
        
        Example:
            validate_percentage(50.5)   # True
            validate_percentage(150)    # False
        """
        return Validators.validate_number_range(value, 0, 100)
    
    # ========== Date/Time Validation ==========
    
    @staticmethod
    def validate_date_format(date_string: str, date_format: str = '%Y-%m-%d') -> bool:
        """
        Validate date string matches format
        
        Example:
            validate_date_format("2025-10-22")                      # True
            validate_date_format("22/10/2025", "%d/%m/%Y")         # True
            validate_date_format("invalid")                         # False
        """
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_datetime_iso(datetime_string: str) -> bool:
        """
        Validate ISO 8601 datetime format
        
        Example:
            validate_datetime_iso("2025-10-22T10:30:00")           # True
            validate_datetime_iso("2025-10-22T10:30:00.123456")    # True
            validate_datetime_iso("invalid")                        # False
        """
        try:
            datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_cron_expression(cron: str) -> bool:
        """
        Validate cron expression format
        
        Format: minute hour day month weekday
        Example:
            validate_cron_expression("0 0 * * *")      # True (midnight daily)
            validate_cron_expression("*/5 * * * *")    # True (every 5 minutes)
            validate_cron_expression("invalid")        # False
        """
        if not cron:
            return False
        
        # Simple validation - check 5 fields
        parts = cron.split()
        if len(parts) != 5:
            return False
        
        # Validate each field
        try:
            minute, hour, day, month, weekday = parts
            
            # Minute (0-59)
            if not Validators._validate_cron_field(minute, 0, 59):
                return False
            
            # Hour (0-23)
            if not Validators._validate_cron_field(hour, 0, 23):
                return False
            
            # Day (1-31)
            if not Validators._validate_cron_field(day, 1, 31):
                return False
            
            # Month (1-12)
            if not Validators._validate_cron_field(month, 1, 12):
                return False
            
            # Weekday (0-6)
            if not Validators._validate_cron_field(weekday, 0, 6):
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def _validate_cron_field(field: str, min_val: int, max_val: int) -> bool:
        """Helper method to validate cron field"""
        if field == '*':
            return True
        
        if '/' in field:
            parts = field.split('/')
            if len(parts) == 2 and parts.isdigit():
                return True
        
        if '-' in field:
            parts = field.split('-')
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                start, end = int(parts), int(parts)
                return min_val <= start <= end <= max_val
        
        if field.isdigit():
            return min_val <= int(field) <= max_val
        
        return False
    
    # ========== Protocol/Transfer Validation ==========
    
    @staticmethod
    def validate_protocol(protocol: str) -> bool:
        """
        Validate transfer protocol
        
        Allowed: ftp, sftp, ftps
        
        Example:
            validate_protocol("sftp")   # True
            validate_protocol("http")   # False
        """
        allowed_protocols = ['ftp', 'sftp', 'ftps']
        return protocol.lower() in allowed_protocols
    
    @staticmethod
    def validate_compression_type(compression: str) -> bool:
        """
        Validate compression type
        
        Allowed: gzip, lz4, zip, bz2
        
        Example:
            validate_compression_type("gzip")   # True
            validate_compression_type("rar")    # False
        """
        allowed_types = ['gzip', 'lz4', 'zip', 'bz2']
        return compression.lower() in allowed_types
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_size_bytes: Optional[int] = None) -> bool:
        """
        Validate file size
        
        Example:
            validate_file_size(1024, max_size_bytes=2048)  # True
            validate_file_size(3000, max_size_bytes=2048)  # False
        """
        if not isinstance(size_bytes, int) or size_bytes < 0:
            return False
        
        if max_size_bytes and size_bytes > max_size_bytes:
            return False
        
        return True
    
    # ========== Checksum Validation ==========
    
    @staticmethod
    def validate_checksum(checksum: str, algorithm: str = 'sha256') -> bool:
        """
        Validate checksum format
        
        Example:
            validate_checksum("abc123...", "sha256")  # True if 64 hex chars
            validate_checksum("xyz", "sha256")        # False
        """
        if not checksum:
            return False
        
        expected_lengths = {
            'md5': 32,
            'sha1': 40,
            'sha256': 64,
            'sha512': 128
        }
        
        expected_length = expected_lengths.get(algorithm.lower())
        if not expected_length:
            return False
        
        # Check if it's hex string of correct length
        return (len(checksum) == expected_length and 
                all(c in '0123456789abcdefABCDEF' for c in checksum))
    
    # ========== Batch Validation ==========
    
    @staticmethod
    def validate_dict(
        data: Dict[str, Any],
        schema: Dict[str, Dict[str, Any]]
    ) -> tuple[bool, List[str]]:
        """
        Validate dictionary against schema
        
        Schema format:
        {
            'field_name': {
                'required': bool,
                'type': type,
                'validator': callable,
                'min_length': int,
                'max_length': int,
                ...
            }
        }
        
        Returns:
            (is_valid, list_of_errors)
        
        Example:
            schema = {
                'hostname': {'required': True, 'type': str, 'min_length': 1},
                'port': {'required': False, 'type': int, 'min': 1, 'max': 65535}
            }
            is_valid, errors = validate_dict(data, schema)
        """
        errors = []
        
        for field, rules in schema.items():
            value = data.get(field)
            
            # Check required
            if rules.get('required', False) and value is None:
                errors.append(f"Field '{field}' is required")
                continue
            
            # Skip validation if not required and not present
            if value is None:
                continue
            
            # Check type
            if 'type' in rules and not isinstance(value, rules['type']):
                errors.append(f"Field '{field}' must be of type {rules['type'].__name__}")
                continue
            
            # Check custom validator
            if 'validator' in rules:
                validator = rules['validator']
                if callable(validator) and not validator(value):
                    errors.append(f"Field '{field}' failed validation")
                    continue
            
            # Check min/max for numbers
            if isinstance(value, (int, float)):
                if 'min' in rules and value < rules['min']:
                    errors.append(f"Field '{field}' must be >= {rules['min']}")
                if 'max' in rules and value > rules['max']:
                    errors.append(f"Field '{field}' must be <= {rules['max']}")
            
            # Check length for strings
            if isinstance(value, str):
                if 'min_length' in rules and len(value) < rules['min_length']:
                    errors.append(f"Field '{field}' must be at least {rules['min_length']} characters")
                if 'max_length' in rules and len(value) > rules['max_length']:
                    errors.append(f"Field '{field}' must be at most {rules['max_length']} characters")
        
        return len(errors) == 0, errors


# Convenience function
def validate(value: Any, validator_name: str, **kwargs) -> bool:
    """
    Convenience function to call validators by name
    
    Example:
        validate("192.168.1.1", "ip_address")
        validate("test@example.com", "email")
        validate(8080, "port")
    """
    validator_method = getattr(Validators, f"validate_{validator_name}", None)
    if validator_method:
        return validator_method(value, **kwargs)
    raise ValueError(f"Unknown validator: {validator_name}")


# Example usage
if __name__ == "__main__":
    # Test various validators
    print("Hostname:", Validators.validate_hostname("server-01"))
    print("IP:", Validators.validate_ip_address("192.168.1.1"))
    print("MAC:", Validators.validate_mac_address("00:11:22:33:44:55"))
    print("Email:", Validators.validate_email("test@example.com"))
    print("Port:", Validators.validate_port(8080))
    print("Cron:", Validators.validate_cron_expression("0 0 * * *"))
    print("Protocol:", Validators.validate_protocol("sftp"))
    
    # Test dict validation
    schema = {
        'hostname': {'required': True, 'type': str, 'min_length': 1},
        'port': {'required': False, 'type': int, 'min': 1, 'max': 65535}
    }
    
    test_data = {
        'hostname': 'test-server',
        'port': 8080
    }
    
    is_valid, errors = Validators.validate_dict(test_data, schema)
    print(f"Dict validation: {is_valid}, Errors: {errors}")
