"""
Filename Transformation Module for Audio Transcription Pipeline.

This module provides functionality to transform audio filenames to transcript filenames,
handling special character sanitization and extension conversion.
"""

import re
import os
from typing import Optional
from urllib.parse import unquote


class FilenameTransformer:
    """Handles transformation of audio filenames to transcript filenames."""
    
    # Characters that need to be sanitized in filenames
    UNSAFE_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    
    # Multiple consecutive spaces or underscores
    MULTIPLE_SPACES_PATTERN = re.compile(r'\s+')
    MULTIPLE_UNDERSCORES_PATTERN = re.compile(r'_+')
    
    @staticmethod
    def audio_to_transcript_filename(audio_filename: str) -> str:
        """
        Convert audio filename to transcript filename.
        
        Changes the file extension from .mp3/.wav to .txt while preserving
        the base filename and handling special character sanitization.
        
        Args:
            audio_filename: Original audio filename (e.g., "meeting.mp3")
            
        Returns:
            Transcript filename with .txt extension (e.g., "meeting.txt")
            
        Raises:
            ValueError: If filename is empty or invalid
        """
        if not audio_filename or not isinstance(audio_filename, str):
            raise ValueError("Filename must be a non-empty string")
        
        # URL decode the filename in case it's URL encoded
        decoded_filename = unquote(audio_filename)
        
        # Extract base name without extension
        base_name, ext = os.path.splitext(decoded_filename)
        
        # Handle special case where filename starts with dot and has no real base name
        if decoded_filename.startswith('.') and base_name == decoded_filename:
            # This means the entire filename was treated as base name (e.g., ".mp3" -> (".mp3", ""))
            base_name = "untitled"
        elif not base_name:
            base_name = "untitled"
        
        # Sanitize the base name
        sanitized_base = FilenameTransformer._sanitize_filename(base_name)
        
        # Add .txt extension
        return f"{sanitized_base}.txt"
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing or replacing unsafe characters.
        
        Args:
            filename: Original filename to sanitize
            
        Returns:
            Sanitized filename safe for filesystem use
        """
        # Remove unsafe characters
        sanitized = FilenameTransformer.UNSAFE_CHARS_PATTERN.sub('', filename)
        
        # Replace multiple consecutive spaces with single space
        sanitized = FilenameTransformer.MULTIPLE_SPACES_PATTERN.sub(' ', sanitized)
        
        # Replace multiple consecutive underscores with single underscore
        sanitized = FilenameTransformer.MULTIPLE_UNDERSCORES_PATTERN.sub('_', sanitized)
        
        # Trim whitespace from beginning and end
        sanitized = sanitized.strip()
        
        # Replace remaining spaces with underscores for better filesystem compatibility
        sanitized = sanitized.replace(' ', '_')
        
        # Ensure we don't have an empty filename
        if not sanitized:
            sanitized = "untitled"
        
        return sanitized
    
    @staticmethod
    def extract_base_filename(full_path: str) -> str:
        """
        Extract base filename from full S3 object key path.
        
        Args:
            full_path: Full S3 object key (e.g., "folder/subfolder/file.mp3")
            
        Returns:
            Base filename without path (e.g., "file.mp3")
        """
        if not full_path:
            raise ValueError("Path cannot be empty")
        
        # Extract filename from path
        return os.path.basename(full_path)
    
    @staticmethod
    def preserve_directory_structure(original_key: str, new_filename: str) -> str:
        """
        Preserve directory structure when creating new filename.
        
        Args:
            original_key: Original S3 object key with directory structure
            new_filename: New filename to place in same directory
            
        Returns:
            New S3 object key with preserved directory structure
        """
        if not original_key:
            return new_filename
        
        # Get directory path
        directory = os.path.dirname(original_key)
        
        # Combine directory with new filename
        if directory:
            return f"{directory}/{new_filename}"
        else:
            return new_filename
    
    @staticmethod
    def is_valid_audio_filename(filename: str) -> bool:
        """
        Check if filename has a valid audio extension.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if filename has .mp3 or .wav extension (case-insensitive)
        """
        if not filename:
            return False
        
        _, ext = os.path.splitext(filename.lower())
        return ext in {'.mp3', '.wav'}
    
    @staticmethod
    def get_file_extension(filename: str) -> Optional[str]:
        """
        Get file extension from filename.
        
        Args:
            filename: Filename to extract extension from
            
        Returns:
            File extension including the dot (e.g., ".mp3") or None if no extension
        """
        if not filename:
            return None
        
        _, ext = os.path.splitext(filename)
        return ext.lower() if ext else None