"""
Authentication and token management for agent communication with central server
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import json
from pathlib import Path

from agent.utils.logger import setup_logger

logger = setup_logger()


class TokenManager:
    """
    Manage JWT tokens for agent authentication
    """
    
    def __init__(self, token_file: str = "data/token.json"):
        """
        Initialize token manager
        
        Args:
            token_file: Path to store token data
        """
        self.token_file = Path(token_file)
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.agent_id: Optional[str] = None
        
        # Load existing token
        self.load_token()
    
    def save_token(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
        agent_id: Optional[str] = None
    ) -> None:
        """
        Save authentication token
        
        Args:
            access_token: JWT access token
            refresh_token: JWT refresh token (optional)
            expires_in: Token expiry time in seconds
            agent_id: Agent identifier
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        self.agent_id = agent_id
        
        # Save to file
        token_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_expiry': self.token_expiry.isoformat(),
            'agent_id': agent_id
        }
        
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            logger.debug("Token saved to file")
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    def load_token(self) -> bool:
        """
        Load token from file
        
        Returns:
            True if token loaded and valid, False otherwise
        """
        if not self.token_file.exists():
            logger.debug("No token file found")
            return False
        
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            self.agent_id = token_data.get('agent_id')
            
            expiry_str = token_data.get('token_expiry')
            if expiry_str:
                self.token_expiry = datetime.fromisoformat(expiry_str)
            
            logger.debug("Token loaded from file")
            return self.is_token_valid()
        
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """
        Check if current token is valid
        
        Returns:
            True if token exists and not expired
        """
        if not self.access_token:
            return False
        
        if not self.token_expiry:
            return False
        
        # Check if expired (with 5 minute buffer)
        buffer = timedelta(minutes=5)
        return datetime.utcnow() < (self.token_expiry - buffer)
    
    def get_token(self) -> Optional[str]:
        """
        Get current valid access token
        
        Returns:
            Access token if valid, None otherwise
        """
        if self.is_token_valid():
            return self.access_token
        return None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests
        
        Returns:
            Dict with Authorization header
        """
        token = self.get_token()
        if token:
            return {'Authorization': f'Bearer {token}'}
        return {}
    
    def decode_token(self, token: Optional[str] = None, verify: bool = False) -> Optional[Dict]:
        """
        Decode JWT token without verification
        
        Args:
            token: Token to decode (uses stored token if None)
            verify: Whether to verify signature (requires secret key)
        
        Returns:
            Decoded token payload or None
        """
        if token is None:
            token = self.access_token
        
        if not token:
            return None
        
        try:
            if verify:
                # Would need secret key from server for verification
                logger.warning("Token verification not implemented - requires secret key")
                return None
            else:
                # Decode without verification (for debugging only)
                decoded = jwt.decode(token, options={"verify_signature": False})
                return decoded
        except Exception as e:
            logger.error(f"Failed to decode token: {e}")
            return None
    
    def clear_token(self) -> None:
        """Clear stored token"""
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.agent_id = None
        
        if self.token_file.exists():
            try:
                self.token_file.unlink()
                logger.debug("Token file deleted")
            except Exception as e:
                logger.error(f"Failed to delete token file: {e}")
    
    def get_token_info(self) -> Dict:
        """
        Get information about current token
        
        Returns:
            Dict with token information
        """
        info = {
            'has_token': bool(self.access_token),
            'is_valid': self.is_token_valid(),
            'agent_id': self.agent_id,
            'expires_at': self.token_expiry.isoformat() if self.token_expiry else None,
            'time_until_expiry': None
        }
        
        if self.token_expiry:
            remaining = self.token_expiry - datetime.utcnow()
            if remaining.total_seconds() > 0:
                info['time_until_expiry'] = int(remaining.total_seconds())
        
        return info


class AgentAuthenticator:
    """
    Handle agent authentication with central server
    """
    
    def __init__(self, api_client, config):
        """
        Initialize authenticator
        
        Args:
            api_client: API client instance
            config: Agent configuration
        """
        self.api_client = api_client
        self.config = config
        self.token_manager = TokenManager()
        
        logger.debug("AgentAuthenticator initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate agent with central server
        
        Returns:
            True if authentication successful
        """
        # Check if we have valid token
        if self.token_manager.is_token_valid():
            token = self.token_manager.get_token()
            self.api_client.set_token(token)
            logger.info("Using existing valid token")
            return True
        
        # Need to get new token
        logger.info("Requesting new authentication token")
        
        # Get token from server
        token_response = self.api_client.get_access_token()
        
        if not token_response:
            logger.error("Failed to obtain authentication token")
            return False
        
        # Save token
        self.token_manager.save_token(
            access_token=token_response.get('access_token'),
            refresh_token=token_response.get('refresh_token'),
            expires_in=token_response.get('expires_in', 3600),
            agent_id=token_response.get('agent_id')
        )
        
        # Set token in API client
        self.api_client.set_token(token_response['access_token'])
        
        logger.info("Authentication successful")
        return True
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure agent is authenticated, re-authenticate if needed
        
        Returns:
            True if authenticated
        """
        if not self.token_manager.is_token_valid():
            logger.info("Token expired or invalid, re-authenticating")
            return self.authenticate()
        return True
    
    def logout(self) -> None:
        """Logout and clear authentication"""
        logger.info("Logging out agent")
        self.token_manager.clear_token()
        self.api_client.set_token(None)
    
    def get_auth_info(self) -> Dict:
        """
        Get authentication information
        
        Returns:
            Dict with authentication status
        """
        return self.token_manager.get_token_info()


# Convenience functions
def create_authenticator(api_client, config) -> AgentAuthenticator:
    """
    Create authenticator instance
    
    Args:
        api_client: API client instance
        config: Agent configuration
    
    Returns:
        AgentAuthenticator instance
    """
    return AgentAuthenticator(api_client, config)


def authenticate_agent(api_client, config) -> bool:
    """
    Convenience function to authenticate agent
    
    Args:
        api_client: API client instance
        config: Agent configuration
    
    Returns:
        True if authentication successful
    """
    authenticator = AgentAuthenticator(api_client, config)
    return authenticator.authenticate()


# Example usage
if __name__ == "__main__":
    from agent.communication.api_client import CentralAPIClient
    from agent.config import AgentConfig
    
    # Initialize
    config = AgentConfig()
    api_client = CentralAPIClient(config.central_server_url, config.agent_id)
    
    # Authenticate
    authenticator = AgentAuthenticator(api_client, config)
    
    if authenticator.authenticate():
        print("Authentication successful")
        print("Auth info:", authenticator.get_auth_info())
    else:
        print("Authentication failed")