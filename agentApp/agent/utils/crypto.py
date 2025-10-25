"""
Encryption and decryption utilities for agent
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional, Tuple
import json
from pathlib import Path

from agent.utils.logger import setup_logger

logger = setup_logger()


class CryptoManager:
    """
    Handle encryption and decryption operations
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize crypto manager
        
        Args:
            key: Encryption key (32 bytes). If None, generates new key.
        """
        if key is None:
            self.key = Fernet.generate_key()
        else:
            self.key = key
        
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate new encryption key
        
        Returns:
            32-byte encryption key
        """
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key_from_password(
        password: str,
        salt: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password
        
        Args:
            password: Password string
            salt: Salt bytes (generates new if None)
        
        Returns:
            Tuple of (key, salt)
        
        Example:
            key, salt = CryptoManager.derive_key_from_password("my_password")
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        return key, salt
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt string
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64 encoded encrypted string
        
        Example:
            crypto = CryptoManager()
            encrypted = crypto.encrypt_string("secret data")
        """
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt string
        
        Args:
            ciphertext: Encrypted string
        
        Returns:
            Decrypted plaintext string
        
        Example:
            crypto = CryptoManager(key)
            plaintext = crypto.decrypt_string(encrypted)
        """
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_file(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        chunk_size: int = 64 * 1024
    ) -> str:
        """
        Encrypt file
        
        Args:
            input_file: Path to file to encrypt
            output_file: Path to output encrypted file (defaults to input + .enc)
            chunk_size: Size of chunks to read/write
        
        Returns:
            Path to encrypted file
        
        Example:
            crypto = CryptoManager()
            encrypted_path = crypto.encrypt_file("data.txt")
        """
        input_path = Path(input_file)
        
        if output_file is None:
            output_file = str(input_path) + '.enc'
        
        output_path = Path(output_file)
        
        try:
            # Read input file
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            encrypted_data = self.cipher.encrypt(data)
            
            # Write output file
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"File encrypted: {input_file} -> {output_file}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(
        self,
        input_file: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Decrypt file
        
        Args:
            input_file: Path to encrypted file
            output_file: Path to output decrypted file
        
        Returns:
            Path to decrypted file
        
        Example:
            crypto = CryptoManager(key)
            decrypted_path = crypto.decrypt_file("data.txt.enc", "data.txt")
        """
        input_path = Path(input_file)
        
        if output_file is None:
            # Remove .enc extension if present
            if input_path.suffix == '.enc':
                output_file = str(input_path.with_suffix(''))
            else:
                output_file = str(input_path) + '.dec'
        
        output_path = Path(output_file)
        
        try:
            # Read encrypted file
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Write output file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"File decrypted: {input_file} -> {output_file}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise
    
    def save_key(self, key_file: str) -> None:
        """
        Save encryption key to file
        
        Args:
            key_file: Path to save key
        """
        try:
            key_path = Path(key_file)
            key_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(key_path, 'wb') as f:
                f.write(self.key)
            
            logger.info(f"Encryption key saved to {key_file}")
        except Exception as e:
            logger.error(f"Failed to save key: {e}")
            raise
    
    @staticmethod
    def load_key(key_file: str) -> bytes:
        """
        Load encryption key from file
        
        Args:
            key_file: Path to key file
        
        Returns:
            Encryption key bytes
        """
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
            
            logger.info(f"Encryption key loaded from {key_file}")
            return key
        except Exception as e:
            logger.error(f"Failed to load key: {e}")
            raise


class SecureStorage:
    """
    Secure storage for sensitive configuration data
    """
    
    def __init__(self, storage_file: str = "data/secure_config.enc", password: str = None):
        """
        Initialize secure storage
        
        Args:
            storage_file: Path to encrypted storage file
            password: Password for encryption (prompts if None)
        """
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Derive key from password
        if password is None:
            password = self._get_password()
        
        # Load or create salt
        salt_file = self.storage_file.with_suffix('.salt')
        if salt_file.exists():
            with open(salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(salt_file, 'wb') as f:
                f.write(salt)
        
        key, _ = CryptoManager.derive_key_from_password(password, salt)
        self.crypto = CryptoManager(key)
        
        # Load existing data
        self.data = self._load_data()
    
    def _get_password(self) -> str:
        """Get password from environment or prompt"""
        password = os.getenv('AGENT_SECURE_PASSWORD')
        if password:
            return password
        
        # In production, you might want to use getpass
        import getpass
        return getpass.getpass("Enter password for secure storage: ")
    
    def _load_data(self) -> dict:
        """Load encrypted data from file"""
        if not self.storage_file.exists():
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                encrypted = f.read()
            
            decrypted = self.crypto.decrypt_string(encrypted)
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Failed to load secure data: {e}")
            return {}
    
    def _save_data(self) -> None:
        """Save encrypted data to file"""
        try:
            plaintext = json.dumps(self.data, indent=2)
            encrypted = self.crypto.encrypt_string(plaintext)
            
            with open(self.storage_file, 'w') as f:
                f.write(encrypted)
            
            logger.debug("Secure data saved")
        except Exception as e:
            logger.error(f"Failed to save secure data: {e}")
            raise
    
    def set(self, key: str, value: any) -> None:
        """
        Store value securely
        
        Args:
            key: Key name
            value: Value to store
        """
        self.data[key] = value
        self._save_data()
    
    def get(self, key: str, default: any = None) -> any:
        """
        Retrieve stored value
        
        Args:
            key: Key name
            default: Default value if key not found
        
        Returns:
            Stored value or default
        """
        return self.data.get(key, default)
    
    def delete(self, key: str) -> None:
        """Delete stored value"""
        if key in self.data:
            del self.data[key]
            self._save_data()
    
    def list_keys(self) -> list:
        """Get list of stored keys"""
        return list(self.data.keys())
    
    def clear(self) -> None:
        """Clear all stored data"""
        self.data = {}
        self._save_data()


# Convenience functions
def encrypt_password(password: str, key: Optional[bytes] = None) -> Tuple[str, bytes]:
    """
    Encrypt password
    
    Args:
        password: Password to encrypt
        key: Encryption key (generates new if None)
    
    Returns:
        Tuple of (encrypted_password, key)
    """
    crypto = CryptoManager(key)
    encrypted = crypto.encrypt_string(password)
    return encrypted, crypto.key


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """
    Decrypt password
    
    Args:
        encrypted_password: Encrypted password
        key: Encryption key
    
    Returns:
        Decrypted password
    """
    crypto = CryptoManager(key)
    return crypto.decrypt_string(encrypted_password)


# Example usage
if __name__ == "__main__":
    # Basic encryption/decryption
    crypto = CryptoManager()
    
    secret = "my_secret_password"
    encrypted = crypto.encrypt_string(secret)
    print(f"Encrypted: {encrypted}")
    
    decrypted = crypto.decrypt_string(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # File encryption
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Secret file content\n" * 100)
    
    print(f"\nTest file: {test_file}")
    
    # Encrypt file
    encrypted_file = crypto.encrypt_file(test_file)
    print(f"Encrypted file: {encrypted_file}")
    
    # Decrypt file
    decrypted_file = crypto.decrypt_file(encrypted_file, test_file + '.dec')
    print(f"Decrypted file: {decrypted_file}")
    
    # Verify contents match
    with open(test_file, 'r') as f:
        original = f.read()
    with open(decrypted_file, 'r') as f:
        recovered = f.read()
    
    print(f"Contents match: {original == recovered}")
    
    # Cleanup
    Path(test_file).unlink()
    Path(encrypted_file).unlink()
    Path(decrypted_file).unlink()
    
    # Secure storage example
    print("\nSecure storage:")
    storage = SecureStorage(password="test_password")
    storage.set("ftp_username", "admin")
    storage.set("ftp_password", "secret123")
    
    print(f"Stored keys: {storage.list_keys()}")
    print(f"FTP username: {storage.get('ftp_username')}")