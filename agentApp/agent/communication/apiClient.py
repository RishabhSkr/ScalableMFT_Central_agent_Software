# agent/communication/api_client.py
import requests
from typing import Dict, List, Optional
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from agent.utils.logger import setup_logger

logger = setup_logger()

class CentralAPIClient:
    def __init__(self, base_url: str, agent_id: str):
        self.base_url = base_url.rstrip('/')
        self.agent_id = agent_id
        self.access_token = None
        
        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_token(self, token: str):
        """Set authentication token"""
        self.access_token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def register_agent(self, system_info: Dict) -> Optional[Dict]:
        """Register agent with central server"""
        try:
            payload = {
                'hostname': system_info['hostname'],
                'ip_address': system_info['ip_address'],
                'mac_address': system_info['mac_address'],
                'os_info': system_info['os_info'],
                'agent_version': system_info['agent_version']
            }
            
            response = self.session.post(
                f"{self.base_url}/agents/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Registration request failed: {e}")
            return None
    
    def get_access_token(self) -> Optional[Dict]:
        """Get JWT access token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/token",
                params={'agent_id': self.agent_id},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.set_token(token_data['access_token'])
                return token_data
            
            return None
        
        except Exception as e:
            logger.error(f"Token request failed: {e}")
            return None
    
    def send_heartbeat(self, status: str, system_info: Dict) -> bool:
        """Send heartbeat to central server"""
        try:
            payload = {
                'status': status,
                'system_info': system_info
            }
            
            response = self.session.post(
                f"{self.base_url}/agents/{self.agent_id}/heartbeat",
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            return False
    
    def get_pending_tasks(self) -> List[Dict]:
        """Fetch pending tasks for this agent"""
        try:
            response = self.session.get(
                f"{self.base_url}/agents/{self.agent_id}/tasks",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
        
        except Exception as e:
            logger.error(f"Failed to fetch tasks: {e}")
            return []
    
    def submit_transfer_log(self, log_data: Dict) -> bool:
        """Submit transfer log to central server"""
        try:
            response = self.session.post(
                f"{self.base_url}/logs/",
                json=log_data,
                timeout=15
            )
            
            return response.status_code in [200, 201]
        
        except Exception as e:
            logger.error(f"Failed to submit log: {e}")
            return False
