# agent/core/compressor.py
import gzip
import lz4.frame
import zipfile
from pathlib import Path
from typing import Optional

from agent.utils.logger import setup_logger

logger = setup_logger()

class FileCompressor:
    @staticmethod
    def compress_file(
        input_path: str,
        output_path: str,
        compression_type: str = 'gzip'
    ) -> Optional[str]:
        """
        Compress file using specified algorithm
        Returns: path to compressed file or None on failure
        """
        try:
            input_file = Path(input_path)
            
            if not input_file.exists():
                logger.error(f"Input file not found: {input_path}")
                return None
            
            if compression_type == 'gzip':
                return FileCompressor._compress_gzip(input_path, output_path)
            elif compression_type == 'lz4':
                return FileCompressor._compress_lz4(input_path, output_path)
            elif compression_type == 'zip':
                return FileCompressor._compress_zip(input_path, output_path)
            else:
                logger.error(f"Unsupported compression type: {compression_type}")
                return None
        
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return None
    
    @staticmethod
    def _compress_gzip(input_path: str, output_path: str) -> str:
        """Compress using gzip"""
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb', compresslevel=6) as f_out:
                f_out.writelines(f_in)
        
        logger.info(f"Compressed with gzip: {input_path} -> {output_path}")
        return output_path
    
    @staticmethod
    def _compress_lz4(input_path: str, output_path: str) -> str:
        """Compress using lz4"""
        with open(input_path, 'rb') as f_in:
            with lz4.frame.open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        logger.info(f"Compressed with lz4: {input_path} -> {output_path}")
        return output_path
    
    @staticmethod
    def _compress_zip(input_path: str, output_path: str) -> str:
        """Compress using zip"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(input_path, Path(input_path).name)
        
        logger.info(f"Compressed with zip: {input_path} -> {output_path}")
        return output_path
    
    @staticmethod
    def get_compression_ratio(original_size: int, compressed_size: int) -> float:
        """Calculate compression ratio"""
        if original_size == 0:
            return 0
        return (1 - (compressed_size / original_size)) * 100
