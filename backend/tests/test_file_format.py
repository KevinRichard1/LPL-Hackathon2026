"""
Unit tests for file format detection and validation module.

Tests cover file extension extraction, format validation, and edge cases
including case-insensitive matching and various filename patterns.
"""

import pytest
from audio_transcription.file_format import (
    extract_file_extension,
    is_supported_audio_format,
    get_file_info,
    should_process_file
)


class TestExtractFileExtension:
    """Test cases for extract_file_extension function."""
    
    def test_extract_mp3_extension(self):
        """Test extraction of .mp3 extension."""
        assert extract_file_extension("meeting.mp3") == ".mp3"
        assert extract_file_extension("audio/recording.mp3") == ".mp3"
        assert extract_file_extension("folder/subfolder/file.mp3") == ".mp3"
    
    def test_extract_wav_extension(self):
        """Test extraction of .wav extension."""
        assert extract_file_extension("interview.wav") == ".wav"
        assert extract_file_extension("sounds/effect.wav") == ".wav"
    
    def test_extract_case_sensitive_extensions(self):
        """Test that extension extraction preserves case."""
        assert extract_file_extension("file.MP3") == ".MP3"
        assert extract_file_extension("file.WAV") == ".WAV"
        assert extract_file_extension("file.Mp3") == ".Mp3"
    
    def test_extract_other_extensions(self):
        """Test extraction of non-audio extensions."""
        assert extract_file_extension("document.pdf") == ".pdf"
        assert extract_file_extension("image.jpg") == ".jpg"
        assert extract_file_extension("data.txt") == ".txt"
    
    def test_no_extension(self):
        """Test files without extensions."""
        assert extract_file_extension("no_extension") is None
        assert extract_file_extension("folder/no_extension") is None
    
    def test_multiple_dots(self):
        """Test files with multiple dots in filename."""
        assert extract_file_extension("file.backup.mp3") == ".mp3"
        assert extract_file_extension("data.2024.01.15.wav") == ".wav"
    
    def test_empty_and_none_inputs(self):
        """Test edge cases with empty or None inputs."""
        assert extract_file_extension("") is None
        assert extract_file_extension(None) is None
    
    def test_dot_only(self):
        """Test files that end with just a dot."""
        assert extract_file_extension("file.") == "."


class TestIsSupportedAudioFormat:
    """Test cases for is_supported_audio_format function."""
    
    def test_supported_mp3_formats(self):
        """Test that .mp3 files are recognized as supported."""
        assert is_supported_audio_format("meeting.mp3") is True
        assert is_supported_audio_format("audio/recording.mp3") is True
    
    def test_supported_wav_formats(self):
        """Test that .wav files are recognized as supported."""
        assert is_supported_audio_format("interview.wav") is True
        assert is_supported_audio_format("sounds/effect.wav") is True
    
    def test_case_insensitive_matching(self):
        """Test case-insensitive format validation."""
        assert is_supported_audio_format("file.MP3") is True
        assert is_supported_audio_format("file.WAV") is True
        assert is_supported_audio_format("file.Mp3") is True
        assert is_supported_audio_format("file.Wav") is True
    
    def test_unsupported_formats(self):
        """Test that non-audio formats are not supported."""
        assert is_supported_audio_format("document.pdf") is False
        assert is_supported_audio_format("image.jpg") is False
        assert is_supported_audio_format("data.txt") is False
        assert is_supported_audio_format("video.mp4") is False
    
    def test_no_extension_files(self):
        """Test that files without extensions are not supported."""
        assert is_supported_audio_format("no_extension") is False
        assert is_supported_audio_format("folder/no_extension") is False
    
    def test_empty_inputs(self):
        """Test edge cases with empty inputs."""
        assert is_supported_audio_format("") is False


class TestGetFileInfo:
    """Test cases for get_file_info function."""
    
    def test_supported_audio_file_info(self):
        """Test file info for supported audio files."""
        extension, is_supported = get_file_info("meeting.mp3")
        assert extension == ".mp3"
        assert is_supported is True
        
        extension, is_supported = get_file_info("interview.WAV")
        assert extension == ".WAV"
        assert is_supported is True
    
    def test_unsupported_file_info(self):
        """Test file info for unsupported files."""
        extension, is_supported = get_file_info("document.pdf")
        assert extension == ".pdf"
        assert is_supported is False
    
    def test_no_extension_file_info(self):
        """Test file info for files without extensions."""
        extension, is_supported = get_file_info("no_extension")
        assert extension is None
        assert is_supported is False


class TestShouldProcessFile:
    """Test cases for should_process_file function."""
    
    def test_should_process_audio_files(self):
        """Test that audio files should be processed."""
        assert should_process_file("recordings/meeting.mp3") is True
        assert should_process_file("recordings/interview.wav") is True
        assert should_process_file("audio.MP3") is True
    
    def test_should_not_process_non_audio_files(self):
        """Test that non-audio files should not be processed."""
        assert should_process_file("documents/notes.txt") is False
        assert should_process_file("images/photo.jpg") is False
        assert should_process_file("no_extension") is False