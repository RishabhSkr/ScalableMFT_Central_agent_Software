# agent/config.py
import json
import uuid
from pathlib import Path
from typing import Optional

class AgentConfig:
    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create configuration
        if self.config_path.exists():
            self.load_config()
        else:
            self.create_default_config()
    
    def load_config(self):
        """Load configuration from file"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.agent_id = config.get('agent_id')
        self.central_server_url = config.get('central_server_url', 'http://localhost:8000/api')
        self.heartbeat_interval = config.get('heartbeat_interval', 60)
        self.task_check_interval = config.get('task_check_interval', 30)
        self.max_retries = config.get('max_retries', 3)
        self.compression_enabled = config.get('compression_enabled', True)
        self.compression_type = config.get('compression_type', 'gzip')
        self.access_token = config.get('access_token')
    
    def create_default_config(self):
        """Create default configuration file"""
        self.agent_id = str(uuid.uuid4())
        self.central_server_url = 'http://localhost:8000/api'
        self.heartbeat_interval = 60
        self.task_check_interval = 30
        self.max_retries = 3
        self.compression_enabled = True
        self.compression_type = 'gzip'
        self.access_token = None
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'agent_id': self.agent_id,
            'central_server_url': self.central_server_url,
            'heartbeat_interval': self.heartbeat_interval,
            'task_check_interval': self.task_check_interval,
            'max_retries': self.max_retries,
            'compression_enabled': self.compression_enabled,
            'compression_type': self.compression_type,
            'access_token': self.access_token
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, indent=4, fp=f)
    
    def save_token(self, token: str):
        """Save access token"""
        self.access_token = token
        self.save_config()
