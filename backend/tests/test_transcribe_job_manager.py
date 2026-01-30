"""
Unit tests for Transcribe Job Manager module.

Tests the job management functionality including unique ID generation,
media format detection, and job parameter construction.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import patch
from audio_transcription.transcribe_job_manager import (
    generate_unique_job_id,
    detect_media_format,
    construct_job_parameters,
    create_transcription_job_config
)


class TestGenerateUniqueJobId:
    """Test unique job ID generation."""
    
    def test_job_id_format(self):
        """Test that job ID follows expected format."""
        audio_file_key = "test-audio.mp3"
        job_id = generate_unique_job_id(audio_file_key)
        
        # Should start with 'transcribe-'
        assert job_id.startswith("transcribe-")
        
        # Should contain the base filename
        assert "test-audio" in job_id
        
        # Should have 4 parts separated by hyphens after 'transcribe-'
        parts = job_id.split('-')
        assert len(parts) >= 4
    
    def test_job_id_uniqueness(self):
        """Test that consecutive calls generate unique IDs."""
        audio_file_key = "test-audio.mp3"
        
        job_id1 = generate_unique_job_id(audio_file_key)
        job_id2 = generate_unique_job_id(audio_file_key)
        
        assert job_id1 != job_id2
    
    def test_job_id_with_path(self):
        """Test job ID generation with file path."""
        audio_file_key = "uploads/2024/test-audio.mp3"
        job_id = generate_unique_job_id(audio_file_key)
        
        # Should extract just the filename
        assert "test-audio" in job_id
        assert "uploads" not in job_id
        assert "2024" not in job_id
    
    def test_job_id_with_special_characters(self):
        """Test job ID generation with special characters in filename."""
        audio_file_key = "test_audio-file.mp3"
        job_id = generate_unique_job_id(audio_file_key)
        
        assert "test_audio-file" in job_id


class TestDetectMediaFormat:
    """Test media format detection."""
    
    def test_mp3_format(self):
        """Test MP3 format detection."""
        result = detect_media_format("test.mp3")
        assert result == "mp3"
    
    def test_wav_format(self):
        """Test WAV format detection."""
        result = detect_media_format("test.wav")
        assert result == "wav"
    
    def test_case_insensitive(self):
        """Test case-insensitive format detection."""
        assert detect_media_format("test.MP3") == "mp3"
        assert detect_media_format("test.WAV") == "wav"
    
    def test_unsupported_format(self):
        """Test error handling for unsupported formats."""
        with pytest.raises(ValueError, match="Unsupported audio format"):
            detect_media_format("test.txt")
    
    def test_no_extension(self):
        """Test error handling for files without extension."""
        with pytest.raises(ValueError, match="No file extension found"):
            detect_media_format("test")


class TestConstructJobParameters:
    """Test job parameter construction."""
    
    def test_basic_parameters(self):
        """Test basic parameter construction."""
        job_name = "test-job-123"
        audio_file_key = "test.mp3"
        media_format = "mp3"
        
        params = construct_job_parameters(job_name, audio_file_key, media_format)
        
        assert params['TranscriptionJobName'] == job_name
        assert params['Media']['MediaFileUri'] == "s3://audio-uploads/test.mp3"
        assert params['MediaFormat'] == media_format
        assert params['LanguageCode'] == "en-US"  # Default from config
        assert params['OutputBucketName'] == "transcripts-raw"
    
    def test_custom_language_code(self):
        """Test parameter construction with custom language code."""
        job_name = "test-job-123"
        audio_file_key = "test.mp3"
        media_format = "mp3"
        language_code = "es-ES"
        
        params = construct_job_parameters(
            job_name, audio_file_key, media_format, language_code
        )
        
        assert params['LanguageCode'] == language_code
    
    def test_wav_format_parameters(self):
        """Test parameter construction for WAV files."""
        job_name = "test-job-456"
        audio_file_key = "audio/test.wav"
        media_format = "wav"
        
        params = construct_job_parameters(job_name, audio_file_key, media_format)
        
        assert params['Media']['MediaFileUri'] == "s3://audio-uploads/audio/test.wav"
        assert params['MediaFormat'] == "wav"


class TestCreateTranscriptionJobConfig:
    """Test complete job configuration creation."""
    
    def test_complete_config_mp3(self):
        """Test complete configuration for MP3 file."""
        audio_file_key = "test-recording.mp3"
        
        config = create_transcription_job_config(audio_file_key)
        
        # Check structure
        assert 'job_name' in config
        assert 'parameters' in config
        
        # Check job name
        job_name = config['job_name']
        assert job_name.startswith("transcribe-")
        assert "test-recording" in job_name
        
        # Check parameters
        params = config['parameters']
        assert params['TranscriptionJobName'] == job_name
        assert params['MediaFormat'] == "mp3"
        assert params['Media']['MediaFileUri'] == "s3://audio-uploads/test-recording.mp3"
    
    def test_complete_config_wav(self):
        """Test complete configuration for WAV file."""
        audio_file_key = "interview.wav"
        
        config = create_transcription_job_config(audio_file_key)
        
        # Check parameters
        params = config['parameters']
        assert params['MediaFormat'] == "wav"
        assert params['Media']['MediaFileUri'] == "s3://audio-uploads/interview.wav"
    
    def test_config_with_unsupported_format(self):
        """Test error handling for unsupported format."""
        audio_file_key = "document.pdf"
        
        with pytest.raises(ValueError, match="Unsupported audio format"):
            create_transcription_job_config(audio_file_key)