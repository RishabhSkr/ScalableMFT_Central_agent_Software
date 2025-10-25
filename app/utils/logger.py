"""
Centralized logging configuration for the application
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional
import json

class CustomFormatter(logging.Formatter):
    """
    Custom formatter with color coding for console output
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color to level name for console
        if hasattr(record, 'color_output') and record.color_output:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs logs in JSON format for structured logging
    """
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'agent_id'):
            log_data['agent_id'] = record.agent_id
        if hasattr(record, 'task_id'):
            log_data['task_id'] = record.task_id
        
        return json.dumps(log_data)


def setup_logger(
    name: str = 'ftp_transfer_system',
    log_level: str = 'INFO',
    log_dir: str = 'logs',
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup and configure logger with multiple handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        json_format: Use JSON format for file logs
        max_bytes: Maximum size per log file before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    
    Example:
        logger = setup_logger()
        logger.info("Application started")
        logger.error("Something went wrong", extra={'user_id': '123'})
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory
    if log_to_file:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Console handler with color
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        console_format = CustomFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        # Add custom attribute for color detection
        class ColorFilter(logging.Filter):
            def filter(self, record):
                record.color_output = True
                return True
        
        console_handler.addFilter(ColorFilter())
        logger.addHandler(console_handler)
    
    # File handler with rotation (by size)
    if log_to_file:
        log_file = Path(log_dir) / f"{name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Error file handler (only errors and above)
    if log_to_file:
        error_log_file = Path(log_dir) / f"{name}_error.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d\n'
            'Message: %(message)s\n'
            'Exception: %(exc_info)s\n'
            '---',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)
    
    # Daily rotating file handler
    if log_to_file:
        daily_log_file = Path(log_dir) / f"{name}_daily.log"
        daily_handler = TimedRotatingFileHandler(
            daily_log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)
        logger.addHandler(daily_handler)
    
    return logger


class LoggerContextFilter(logging.Filter):
    """
    Filter to add context information to log records
    """
    
    def __init__(self, **context):
        super().__init__()
        self.context = context
    
    def filter(self, record):
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def add_context_to_logger(logger: logging.Logger, **context):
    """
    Add context information to all logs from this logger
    
    Example:
        logger = setup_logger()
        add_context_to_logger(logger, user_id='123', request_id='abc')
        logger.info("User action")  # Will include user_id and request_id
    """
    context_filter = LoggerContextFilter(**context)
    logger.addFilter(context_filter)


class LogCapture:
    """
    Context manager to capture logs for testing
    
    Example:
        with LogCapture() as logs:
            logger.info("Test message")
        
        assert "Test message" in logs.output
    """
    
    def __init__(self, logger_name: str = 'ftp_transfer_system', level: int = logging.INFO):
        self.logger_name = logger_name
        self.level = level
        self.handler = None
        self.output = []
    
    def __enter__(self):
        self.handler = logging.StreamHandler()
        self.handler.setLevel(self.level)
        
        # Capture output
        import io
        self.stream = io.StringIO()
        self.handler.stream = self.stream
        
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(self.handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = logging.getLogger(self.logger_name)
        logger.removeHandler(self.handler)
        self.output = self.stream.getvalue().split('\n')


# Convenience functions
def get_logger(name: str = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (defaults to 'ftp_transfer_system')
    
    Returns:
        Logger instance
    """
    if name is None:
        name = 'ftp_transfer_system'
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger = None):
    """
    Decorator to log function calls
    
    Example:
        @log_function_call()
        def my_function(x, y):
            return x + y
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger()
            
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator


def log_execution_time(logger: logging.Logger = None):
    """
    Decorator to log function execution time
    
    Example:
        @log_execution_time()
        def slow_function():
            time.sleep(2)
    """
    import time
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger()
            
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Basic usage
    logger = setup_logger(log_level='DEBUG')
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # With context
    logger.info("User action", extra={'user_id': '12345', 'action': 'login'})
    
    # Test decorator
    @log_function_call(logger)
    @log_execution_time(logger)
    def test_function(x, y):
        import time
        time.sleep(0.1)
        return x + y
    
    result = test_function(5, 3)
    print(f"Result: {result}")
