"""
Unit tests for filename transformation module.

Tests cover audio to transcript filename conversion, special character sanitization,
and directory structure preservation.
"""

import pytest
from audio_transcription.filename_transformer import FilenameTransformer


class TestFilenameTransformer:
    """Test cases for FilenameTransformer class."""
    
    def test_basic_mp3_to_txt_conversion(self):
        """Test basic conversion from .mp3 to .txt."""
        result = FilenameTransformer.audio_to_transcript_filename("meeting.mp3")
        assert result == "meeting.txt"
    
    def test_basic_wav_to_txt_conversion(self):
        """Test basic conversion from .wav to .txt."""
        result = FilenameTransformer.audio_to_transcript_filename("interview.wav")
        assert result == "interview.txt"
    
    def test_case_preservation_in_base_name(self):
        """Test that base filename case is preserved."""
        result = FilenameTransformer.audio_to_transcript_filename("ImportantMeeting.mp3")
        assert result == "ImportantMeeting.txt"
    
    def test_mixed_case_extension_handling(self):
        """Test handling of mixed case extensions."""
        result = FilenameTransformer.audio_to_transcript_filename("file.MP3")
        assert result == "file.txt"
        
        result = FilenameTransformer.audio_to_transcript_filename("file.WAV")
        assert result == "file.txt"
    
    def test_special_character_sanitization(self):
        """Test sanitization of special characters in filenames."""
        # Test various unsafe characters
        result = FilenameTransformer.audio_to_transcript_filename("meeting<>:\"/\\|?*.mp3")
        assert result == "meeting.txt"
        
        # Test control characters
        result = FilenameTransformer.audio_to_transcript_filename("file\x00\x1f.mp3")
        assert result == "file.txt"
    
    def test_space_handling(self):
        """Test handling of spaces in filenames."""
        result = FilenameTransformer.audio_to_transcript_filename("team meeting notes.mp3")
        assert result == "team_meeting_notes.txt"
        
        # Test multiple consecutive spaces
        result = FilenameTransformer.audio_to_transcript_filename("file   with   spaces.wav")
        assert result == "file_with_spaces.txt"
    
    def test_underscore_handling(self):
        """Test handling of underscores in filenames."""
        result = FilenameTransformer.audio_to_transcript_filename("file_name.mp3")
        assert result == "file_name.txt"
        
        # Test multiple consecutive underscores
        result = FilenameTransformer.audio_to_transcript_filename("file___name.wav")
        assert result == "file_name.txt"
    
    def test_url_encoded_filename_handling(self):
        """Test handling of URL-encoded filenames."""
        result = FilenameTransformer.audio_to_transcript_filename("meeting%20notes.mp3")
        assert result == "meeting_notes.txt"
        
        result = FilenameTransformer.audio_to_transcript_filename("file%2Bname.wav")
        assert result == "file+name.txt"
    
    def test_multiple_dots_in_filename(self):
        """Test filenames with multiple dots."""
        result = FilenameTransformer.audio_to_transcript_filename("backup.2024.01.15.mp3")
        assert result == "backup.2024.01.15.txt"
        
        result = FilenameTransformer.audio_to_transcript_filename("file.backup.wav")
        assert result == "file.backup.txt"
    
    def test_whitespace_trimming(self):
        """Test trimming of leading and trailing whitespace."""
        result = FilenameTransformer.audio_to_transcript_filename("  meeting  .mp3")
        assert result == "meeting.txt"
        
        result = FilenameTransformer.audio_to_transcript_filename("\t\nfile\t\n.wav")
        assert result == "file.txt"
    
    def test_empty_base_name_handling(self):
        """Test handling of filenames with empty base names."""
        result = FilenameTransformer.audio_to_transcript_filename(".mp3")
        assert result == "untitled.txt"
        
        result = FilenameTransformer.audio_to_transcript_filename("   .wav")
        assert result == "untitled.txt"
    
    def test_extract_base_filename(self):
        """Test extraction of base filename from full path."""
        result = FilenameTransformer.extract_base_filename("folder/subfolder/meeting.mp3")
        assert result == "meeting.mp3"
        
        result = FilenameTransformer.extract_base_filename("meeting.mp3")
        assert result == "meeting.mp3"
        
        result = FilenameTransformer.extract_base_filename("audio/recordings/interview.wav")
        assert result == "interview.wav"
    
    def test_preserve_directory_structure(self):
        """Test preservation of directory structure."""
        result = FilenameTransformer.preserve_directory_structure(
            "audio/recordings/meeting.mp3", 
            "meeting.txt"
        )
        assert result == "audio/recordings/meeting.txt"
        
        result = FilenameTransformer.preserve_directory_structure(
            "meeting.mp3", 
            "meeting.txt"
        )
        assert result == "meeting.txt"
        
        result = FilenameTransformer.preserve_directory_structure(
            "", 
            "meeting.txt"
        )
        assert result == "meeting.txt"
    
    def test_is_valid_audio_filename(self):
        """Test validation of audio filenames."""
        assert FilenameTransformer.is_valid_audio_filename("meeting.mp3") is True
        assert FilenameTransformer.is_valid_audio_filename("interview.wav") is True
        assert FilenameTransformer.is_valid_audio_filename("file.MP3") is True
        assert FilenameTransformer.is_valid_audio_filename("file.WAV") is True
        
        assert FilenameTransformer.is_valid_audio_filename("document.pdf") is False
        assert FilenameTransformer.is_valid_audio_filename("image.jpg") is False
        assert FilenameTransformer.is_valid_audio_filename("no_extension") is False
        assert FilenameTransformer.is_valid_audio_filename("") is False
    
    def test_get_file_extension(self):
        """Test extraction of file extensions."""
        assert FilenameTransformer.get_file_extension("meeting.mp3") == ".mp3"
        assert FilenameTransformer.get_file_extension("interview.WAV") == ".wav"
        assert FilenameTransformer.get_file_extension("document.PDF") == ".pdf"
        assert FilenameTransformer.get_file_extension("no_extension") is None
        assert FilenameTransformer.get_file_extension("") is None


class TestFilenameTransformerErrorHandling:
    """Test error handling in FilenameTransformer."""
    
    def test_empty_filename_error(self):
        """Test error handling for empty filename."""
        with pytest.raises(ValueError, match="Filename must be a non-empty string"):
            FilenameTransformer.audio_to_transcript_filename("")
    
    def test_none_filename_error(self):
        """Test error handling for None filename."""
        with pytest.raises(ValueError, match="Filename must be a non-empty string"):
            FilenameTransformer.audio_to_transcript_filename(None)
    
    def test_non_string_filename_error(self):
        """Test error handling for non-string filename."""
        with pytest.raises(ValueError, match="Filename must be a non-empty string"):
            FilenameTransformer.audio_to_transcript_filename(123)
    
    def test_extract_base_filename_empty_path(self):
        """Test error handling for empty path in extract_base_filename."""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            FilenameTransformer.extract_base_filename("")


class TestFilenameTransformerEdgeCases:
    """Test edge cases for FilenameTransformer."""
    
    def test_very_long_filename(self):
        """Test handling of very long filenames."""
        long_name = "a" * 200 + ".mp3"
        result = FilenameTransformer.audio_to_transcript_filename(long_name)
        expected = "a" * 200 + ".txt"
        assert result == expected
    
    def test_unicode_characters(self):
        """Test handling of unicode characters in filenames."""
        result = FilenameTransformer.audio_to_transcript_filename("会议记录.mp3")
        assert result == "会议记录.txt"
        
        result = FilenameTransformer.audio_to_transcript_filename("réunion.wav")
        assert result == "réunion.txt"
    
    def test_only_special_characters(self):
        """Test filename with only special characters."""
        result = FilenameTransformer.audio_to_transcript_filename("***<>?***.mp3")
        assert result == "untitled.txt"
    
    def test_mixed_separators(self):
        """Test handling of mixed path separators."""
        result = FilenameTransformer.extract_base_filename("folder\\subfolder/file.mp3")
        assert result == "file.mp3"