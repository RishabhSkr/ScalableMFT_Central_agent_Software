"""
File checksum calculation and verification
"""
import hashlib
from pathlib import Path
from typing import Optional, Tuple
import zlib

from agent.utils.logger import setup_logger

logger = setup_logger()


class ChecksumCalculator:
    """
    Calculate and verify file checksums
    """
    
    # Supported algorithms
    ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
        'crc32': None  # Special handling
    }
    
    @staticmethod
    def calculate_file_checksum(
        file_path: str,
        algorithm: str = 'sha256',
        chunk_size: int = 8192
    ) -> Optional[str]:
        """
        Calculate checksum of a file
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256, sha512, crc32)
            chunk_size: Size of chunks to read (bytes)
        
        Returns:
            Hexadecimal checksum string or None on error
        
        Example:
            checksum = ChecksumCalculator.calculate_file_checksum('/path/file.txt')
        """
        algorithm = algorithm.lower()
        
        if algorithm not in ChecksumCalculator.ALGORITHMS:
            logger.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            if not file_path_obj.is_file():
                logger.error(f"Not a file: {file_path}")
                return None
            
            if algorithm == 'crc32':
                return ChecksumCalculator._calculate_crc32(file_path, chunk_size)
            
            # Create hash object
            hash_obj = ChecksumCalculator.ALGORITHMS[algorithm]()
            
            # Read file in chunks
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
            
            checksum = hash_obj.hexdigest()
            logger.debug(f"Calculated {algorithm} checksum for {file_path}: {checksum}")
            
            return checksum
        
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return None
    
    @staticmethod
    def _calculate_crc32(file_path: str, chunk_size: int = 8192) -> str:
        """
        Calculate CRC32 checksum
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read
        
        Returns:
            CRC32 checksum as hex string
        """
        crc = 0
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                crc = zlib.crc32(chunk, crc)
        
        # Convert to unsigned 32-bit value and format as hex
        crc = crc & 0xFFFFFFFF
        return format(crc, '08x')
    
    @staticmethod
    def calculate_string_checksum(
        data: str,
        algorithm: str = 'sha256'
    ) -> Optional[str]:
        """
        Calculate checksum of a string
        
        Args:
            data: String data
            algorithm: Hash algorithm
        
        Returns:
            Hexadecimal checksum string
        
        Example:
            checksum = ChecksumCalculator.calculate_string_checksum("hello world")
        """
        algorithm = algorithm.lower()
        
        if algorithm not in ChecksumCalculator.ALGORITHMS:
            logger.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        try:
            if algorithm == 'crc32':
                crc = zlib.crc32(data.encode('utf-8')) & 0xFFFFFFFF
                return format(crc, '08x')
            
            hash_obj = ChecksumCalculator.ALGORITHMS[algorithm]()
            hash_obj.update(data.encode('utf-8'))
            return hash_obj.hexdigest()
        
        except Exception as e:
            logger.error(f"Failed to calculate checksum: {e}")
            return None
    
    @staticmethod
    def verify_checksum(
        file_path: str,
        expected_checksum: str,
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify file checksum matches expected value
        
        Args:
            file_path: Path to file
            expected_checksum: Expected checksum value
            algorithm: Hash algorithm used
        
        Returns:
            True if checksums match
        
        Example:
            is_valid = ChecksumCalculator.verify_checksum(
                '/path/file.txt',
                'abc123...',
                'sha256'
            )
        """
        calculated = ChecksumCalculator.calculate_file_checksum(
            file_path,
            algorithm
        )
        
        if calculated is None:
            return False
        
        match = calculated.lower() == expected_checksum.lower()
        
        if match:
            logger.info(f"Checksum verification passed for {file_path}")
        else:
            logger.error(
                f"Checksum mismatch for {file_path}:\n"
                f"  Expected:   {expected_checksum}\n"
                f"  Calculated: {calculated}"
            )
        
        return match
    
    @staticmethod
    def calculate_multiple_checksums(
        file_path: str,
        algorithms: list = None
    ) -> dict:
        """
        Calculate multiple checksums for a file
        
        Args:
            file_path: Path to file
            algorithms: List of algorithms (default: ['md5', 'sha256'])
        
        Returns:
            Dict with algorithm: checksum pairs
        
        Example:
            checksums = ChecksumCalculator.calculate_multiple_checksums(
                '/path/file.txt',
                ['md5', 'sha256', 'sha512']
            )
            # {'md5': 'abc...', 'sha256': 'def...', 'sha512': 'ghi...'}
        """
        if algorithms is None:
            algorithms = ['md5', 'sha256']
        
        results = {}
        
        for algorithm in algorithms:
            checksum = ChecksumCalculator.calculate_file_checksum(
                file_path,
                algorithm
            )
            if checksum:
                results[algorithm] = checksum
        
        return results
    
    @staticmethod
    def get_file_info_with_checksum(
        file_path: str,
        algorithm: str = 'sha256'
    ) -> Optional[dict]:
        """
        Get file info including checksum
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm
        
        Returns:
            Dict with file info and checksum
        
        Example:
            info = ChecksumCalculator.get_file_info_with_checksum('/path/file.txt')
            # {
            #     'path': '/path/file.txt',
            #     'name': 'file.txt',
            #     'size_bytes': 1024,
            #     'checksum': 'abc123...',
            #     'algorithm': 'sha256'
            # }
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            checksum = ChecksumCalculator.calculate_file_checksum(
                file_path,
                algorithm
            )
            
            if checksum is None:
                return None
            
            stat = file_path_obj.stat()
            
            return {
                'path': str(file_path_obj.absolute()),
                'name': file_path_obj.name,
                'size_bytes': stat.st_size,
                'checksum': checksum,
                'algorithm': algorithm,
                'modified_time': stat.st_mtime
            }
        
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None


class ChecksumVerifier:
    """
    High-level checksum verification for transfers
    """
    
    def __init__(self, algorithm: str = 'sha256'):
        """
        Initialize verifier
        
        Args:
            algorithm: Default hash algorithm to use
        """
        self.algorithm = algorithm
        self.calculator = ChecksumCalculator()
    
    def calculate_before_transfer(
        self,
        file_path: str
    ) -> Tuple[Optional[str], Optional[int]]:
        """
        Calculate checksum before transfer
        
        Args:
            file_path: Path to file
        
        Returns:
            Tuple of (checksum, file_size) or (None, None) on error
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None, None
            
            # Get file size
            file_size = file_path_obj.stat().st_size
            
            # Calculate checksum
            checksum = self.calculator.calculate_file_checksum(
                file_path,
                self.algorithm
            )
            
            if checksum:
                logger.info(
                    f"Pre-transfer checksum for {file_path_obj.name}: {checksum}"
                )
            
            return checksum, file_size
        
        except Exception as e:
            logger.error(f"Failed to calculate pre-transfer checksum: {e}")
            return None, None
    
    def verify_after_transfer(
        self,
        local_file: str,
        remote_checksum: str
    ) -> bool:
        """
        Verify file after transfer by comparing checksums
        
        Args:
            local_file: Path to local file
            remote_checksum: Checksum from remote server
        
        Returns:
            True if checksums match
        """
        local_checksum = self.calculator.calculate_file_checksum(
            local_file,
            self.algorithm
        )
        
        if local_checksum is None:
            logger.error("Failed to calculate local checksum")
            return False
        
        match = local_checksum.lower() == remote_checksum.lower()
        
        if match:
            logger.info("Transfer verification successful - checksums match")
        else:
            logger.error(
                f"Transfer verification failed - checksum mismatch:\n"
                f"  Local:  {local_checksum}\n"
                f"  Remote: {remote_checksum}"
            )
        
        return match
    
    def verify_compressed_file(
        self,
        original_file: str,
        compressed_file: str,
        original_checksum: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Verify compressed file integrity
        
        Args:
            original_file: Path to original file
            compressed_file: Path to compressed file
            original_checksum: Pre-calculated original checksum (optional)
        
        Returns:
            Tuple of (is_valid, original_checksum, compressed_checksum)
        """
        # Calculate original checksum if not provided
        if original_checksum is None:
            original_checksum = self.calculator.calculate_file_checksum(
                original_file,
                self.algorithm
            )
        
        # Calculate compressed file checksum
        compressed_checksum = self.calculator.calculate_file_checksum(
            compressed_file,
            self.algorithm
        )
        
        # Both checksums should exist
        is_valid = (original_checksum is not None and 
                   compressed_checksum is not None)
        
        if is_valid:
            logger.info(
                f"Compressed file verification:\n"
                f"  Original:   {original_checksum}\n"
                f"  Compressed: {compressed_checksum}"
            )
        
        return is_valid, original_checksum, compressed_checksum


# Convenience functions
def calculate_checksum(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
    """
    Convenience function to calculate file checksum
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm
    
    Returns:
        Checksum string or None
    """
    return ChecksumCalculator.calculate_file_checksum(file_path, algorithm)


def verify_file(
    file_path: str,
    expected_checksum: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    Convenience function to verify file checksum
    
    Args:
        file_path: Path to file
        expected_checksum: Expected checksum
        algorithm: Hash algorithm
    
    Returns:
        True if checksums match
    """
    return ChecksumCalculator.verify_checksum(file_path, expected_checksum, algorithm)


# Example usage
if __name__ == "__main__":
    import tempfile
    
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Hello, World!\n" * 1000)
    
    print(f"Test file: {test_file}")
    
    # Calculate checksums
    print("\nCalculating checksums...")
    checksums = ChecksumCalculator.calculate_multiple_checksums(
        test_file,
        ['md5', 'sha1', 'sha256', 'sha512', 'crc32']
    )
    
    for algo, checksum in checksums.items():
        print(f"  {algo.upper()}: {checksum}")
    
    # Verify checksum
    print("\nVerifying SHA256...")
    is_valid = ChecksumCalculator.verify_checksum(
        test_file,
        checksums['sha256'],
        'sha256'
    )
    print(f"  Valid: {is_valid}")
    
    # Get file info
    print("\nFile info with checksum:")
    info = ChecksumCalculator.get_file_info_with_checksum(test_file)
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    Path(test_file).unlink()