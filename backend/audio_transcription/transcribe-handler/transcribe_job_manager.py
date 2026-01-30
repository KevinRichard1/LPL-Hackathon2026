"""
Transcribe Job Management Module

This module handles the creation and management of Amazon Transcribe jobs,
including unique job identifier generation, parameter construction, and
media format detection.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .config import Config
from .file_format import extract_file_extension


def generate_unique_job_id(audio_file_key: str) -> str:
    """
    Generate a unique transcription job identifier.
    
    Creates a unique job ID using timestamp and UUID to ensure uniqueness
    across all transcription jobs.
    
    Args:
        audio_file_key: The S3 object key of the audio file
        
    Returns:
        str: Unique job identifier in format 'transcribe-{timestamp}-{uuid}'
        
    Requirements: 2.1
    """
    # Extract base filename without extension for readability
    base_name = audio_file_key.split('/')[-1].split('.')[0]
    
    # Generate timestamp in format YYYYMMDD-HHMMSS
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    
    # Generate short UUID for uniqueness
    unique_id = str(uuid.uuid4())[:8]
    
    # Combine components for unique job ID
    job_id = f"transcribe-{base_name}-{timestamp}-{unique_id}"
    
    return job_id


def detect_media_format(audio_file_key: str) -> str:
    """
    Detect media format based on file extension.
    
    Extracts the file extension and maps it to the appropriate
    Amazon Transcribe media format parameter.
    
    Args:
        audio_file_key: The S3 object key of the audio file
        
    Returns:
        str: Media format ('mp3' or 'wav')
        
    Raises:
        ValueError: If file extension is not supported
        
    Requirements: 2.2
    """
    file_extension = extract_file_extension(audio_file_key)
    
    if not file_extension:
        raise ValueError("No file extension found")
    
    # Map file extensions to Transcribe media formats (case-insensitive)
    format_mapping = {
        '.mp3': 'mp3',
        '.wav': 'wav'
    }
    
    # Convert to lowercase for case-insensitive matching
    extension_lower = file_extension.lower()
    
    if extension_lower not in format_mapping:
        raise ValueError(f"Unsupported audio format: {file_extension}")
    
    return format_mapping[extension_lower]


def construct_job_parameters(
    job_name: str,
    audio_file_key: str,
    media_format: str,
    language_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Construct Amazon Transcribe job parameters.
    
    Creates the complete parameter dictionary required for starting
    a transcription job with correct S3 URIs and configuration.
    
    Args:
        job_name: Unique job identifier
        audio_file_key: S3 object key of the audio file
        media_format: Media format ('mp3' or 'wav')
        language_code: Language code (defaults to config value)
        
    Returns:
        Dict[str, Any]: Complete job parameters for Transcribe API
        
    Requirements: 2.2
    """
    if language_code is None:
        language_code = Config.get_transcribe_language_code()
    
    # Construct input S3 URI
    input_uri = f"s3://{Config.get_audio_upload_bucket()}/{audio_file_key}"
    
    # Construct job parameters
    job_parameters = {
        'TranscriptionJobName': job_name,
        'Media': {
            'MediaFileUri': input_uri
        },
        'MediaFormat': media_format,
        'LanguageCode': language_code,
        'OutputBucketName': Config.get_transcript_storage_bucket()
    }
    
    return job_parameters


def create_transcription_job_config(audio_file_key: str) -> Dict[str, Any]:
    """
    Create complete transcription job configuration.
    
    Combines all job management functions to create a complete
    configuration for starting a transcription job.
    
    Args:
        audio_file_key: S3 object key of the audio file
        
    Returns:
        Dict[str, Any]: Complete job configuration including job name and parameters
        
    Requirements: 2.1, 2.2
    """
    # Generate unique job identifier
    job_name = generate_unique_job_id(audio_file_key)
    
    # Detect media format
    media_format = detect_media_format(audio_file_key)
    
    # Construct job parameters
    job_parameters = construct_job_parameters(job_name, audio_file_key, media_format)
    
    return {
        'job_name': job_name,
        'parameters': job_parameters
    }