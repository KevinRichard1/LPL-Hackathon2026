"""
File format detection and validation module for Audio Transcription Pipeline.

This module provides functionality to extract file extensions from S3 object keys
and validate whether files are supported audio formats (.mp3, .wav) with
case-insensitive matching.
"""

import os
from typing import Optional, Tuple
from .config import Config


def extract_file_extension(s3_object_key: str) -> Optional[str]:
    """
    Extract file extension from S3 object key.
    
    Args:
        s3_object_key: The S3 object key (file path) to extract extension from
        
    Returns:
        The file extension including the dot (e.g., '.mp3', '.wav') or None if no extension
        
    Examples:
        >>> extract_file_extension("audio/meeting.mp3")
        '.mp3'
        >>> extract_file_extension("folder/interview.WAV")
        '.WAV'
        >>> extract_file_extension("no_extension")
        None
    """
    if not s3_object_key:
        return None
    
    # Use os.path.splitext to handle the extension extraction
    _, extension = os.path.splitext(s3_object_key)
    
    # Return None if no extension found
    return extension if extension else None


def is_supported_audio_format(s3_object_key: str) -> bool:
    """
    Check if the file has a supported audio format extension (.mp3 or .wav).
    
    Performs case-insensitive matching against supported audio formats.
    
    Args:
        s3_object_key: The S3 object key (file path) to validate
        
    Returns:
        True if the file has a supported audio extension, False otherwise
        
    Examples:
        >>> is_supported_audio_format("meeting.mp3")
        True
        >>> is_supported_audio_format("interview.WAV")
        True
        >>> is_supported_audio_format("document.pdf")
        False
        >>> is_supported_audio_format("no_extension")
        False
    """
    extension = extract_file_extension(s3_object_key)
    
    if not extension:
        return False
    
    # Use the config module for case-insensitive validation
    return Config.is_supported_audio_format(extension)


def get_file_info(s3_object_key: str) -> Tuple[Optional[str], bool]:
    """
    Get comprehensive file information including extension and format validation.
    
    Args:
        s3_object_key: The S3 object key (file path) to analyze
        
    Returns:
        Tuple containing:
        - File extension (with dot) or None if no extension
        - Boolean indicating if it's a supported audio format
        
    Examples:
        >>> get_file_info("audio/meeting.mp3")
        ('.mp3', True)
        >>> get_file_info("docs/report.pdf")
        ('.pdf', False)
        >>> get_file_info("no_extension")
        (None, False)
    """
    extension = extract_file_extension(s3_object_key)
    is_supported = is_supported_audio_format(s3_object_key)
    
    return extension, is_supported


def should_process_file(s3_object_key: str) -> bool:
    """
    Determine if a file should be processed by the transcription pipeline.
    
    This is the main entry point for file filtering logic.
    
    Args:
        s3_object_key: The S3 object key (file path) to evaluate
        
    Returns:
        True if the file should be processed (is a supported audio format), False otherwise
        
    Examples:
        >>> should_process_file("recordings/meeting.mp3")
        True
        >>> should_process_file("recordings/interview.wav")
        True
        >>> should_process_file("documents/notes.txt")
        False
    """
    return is_supported_audio_format(s3_object_key)