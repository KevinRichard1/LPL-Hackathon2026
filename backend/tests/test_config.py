"""
Tests for the configuration module.
"""

import os
import pytest
from audio_transcription.config import Config


class TestConfig:
    """Test cases for the Config class."""
    
    def test_default_bucket_names(self):
        """Test default S3 bucket names."""
        assert Config.get_audio_upload_bucket() == "audio-uploads"
        assert Config.get_transcript_storage_bucket() == "transcripts-raw"
    
    def test_default_aws_region(self):
        """Test default AWS region."""
        assert Config.get_aws_region() == "us-east-1"
    
    def test_default_language_code(self):
        """Test default transcribe language code."""
        assert Config.get_transcribe_language_code() == "en-US"
    
    def test_supported_audio_formats(self):
        """Test supported audio format validation."""
        assert Config.is_supported_audio_format(".mp3") is True
        assert Config.is_supported_audio_format(".wav") is True
        assert Config.is_supported_audio_format(".MP3") is True  # Case insensitive
        assert Config.is_supported_audio_format(".WAV") is True  # Case insensitive
        assert Config.is_supported_audio_format(".txt") is False
        assert Config.is_supported_audio_format(".pdf") is False
        assert Config.is_supported_audio_format("") is False
    
    def test_environment_variable_override(self, monkeypatch):
        """Test that environment variables override default values."""
        monkeypatch.setenv("AUDIO_UPLOAD_BUCKET", "custom-audio-bucket")
        monkeypatch.setenv("TRANSCRIPT_STORAGE_BUCKET", "custom-transcript-bucket")
        monkeypatch.setenv("AWS_REGION", "us-west-2")
        monkeypatch.setenv("TRANSCRIBE_LANGUAGE_CODE", "es-ES")
        
        # Need to reload the module to pick up new environment variables
        import importlib
        from audio_transcription import config
        importlib.reload(config)
        
        assert config.Config.get_audio_upload_bucket() == "custom-audio-bucket"
        assert config.Config.get_transcript_storage_bucket() == "custom-transcript-bucket"
        assert config.Config.get_aws_region() == "us-west-2"
        assert config.Config.get_transcribe_language_code() == "es-ES"