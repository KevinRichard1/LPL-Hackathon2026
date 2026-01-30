"""
Configuration module for Audio Transcription Pipeline.

This module centralizes all configuration settings including S3 bucket names,
AWS settings, and other environment-specific parameters.
"""

import os
from typing import Optional


class Config:
    """Configuration class for the Audio Transcription Pipeline."""
    
    # S3 Bucket Configuration
    AUDIO_UPLOAD_BUCKET: str = os.getenv("AUDIO_UPLOAD_BUCKET", "audio-uploads")
    TRANSCRIPT_STORAGE_BUCKET: str = os.getenv("TRANSCRIPT_STORAGE_BUCKET", "transcripts-raw")
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Transcribe Configuration
    TRANSCRIBE_LANGUAGE_CODE: str = os.getenv("TRANSCRIBE_LANGUAGE_CODE", "en-US")
    
    # Supported file formats
    SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav"}
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_audio_upload_bucket(cls) -> str:
        """Get the audio upload bucket name."""
        return cls.AUDIO_UPLOAD_BUCKET
    
    @classmethod
    def get_transcript_storage_bucket(cls) -> str:
        """Get the transcript storage bucket name."""
        return cls.TRANSCRIPT_STORAGE_BUCKET
    
    @classmethod
    def get_aws_region(cls) -> str:
        """Get the AWS region."""
        return cls.AWS_REGION
    
    @classmethod
    def get_transcribe_language_code(cls) -> str:
        """Get the default language code for transcription."""
        return cls.TRANSCRIBE_LANGUAGE_CODE
    
    @classmethod
    def is_supported_audio_format(cls, file_extension: str) -> bool:
        """Check if the file extension is supported for audio transcription."""
        return file_extension.lower() in cls.SUPPORTED_AUDIO_FORMATS