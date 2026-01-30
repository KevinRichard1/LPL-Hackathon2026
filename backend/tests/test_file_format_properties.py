"""
Property-based tests for file format detection and validation module.

These tests validate universal properties that should hold across all valid inputs
using the Hypothesis library for property-based testing.
"""

import pytest
from hypothesis import given, strategies as st, assume
from audio_transcription.file_format import (
    extract_file_extension,
    is_supported_audio_format,
    should_process_file
)


# Strategy for generating valid S3 object keys
s3_object_key_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'), whitelist_characters='.-/'),
    min_size=1,
    max_size=100
).filter(lambda x: x and not x.startswith('.') and not x.endswith('.'))

# Strategy for generating file extensions
file_extension_strategy = st.sampled_from(['.mp3', '.wav', '.MP3', '.WAV', '.Mp3', '.Wav', '.txt', '.pdf', '.jpg', '.png', '.doc'])

# Strategy for generating filenames with extensions
filename_with_extension_strategy = st.builds(
    lambda name, ext: f"{name}{ext}",
    s3_object_key_strategy,
    file_extension_strategy
)


class TestFileFormatFilteringProperties:
    """Property-based tests for file format filtering functionality."""
    
    @given(filename_with_extension_strategy)
    def test_property_1_file_format_filtering(self, s3_object_key):
        """
        **Feature: audio-transcription-pipeline, Property 1: File Format Filtering**
        **Validates: Requirements 1.3**
        
        For any file uploaded to the audio bucket, the system should process only files 
        with .mp3 or .wav extensions, while ignoring all other file types and logging 
        the ignored files appropriately.
        """
        # Extract the extension to determine expected behavior
        extension = extract_file_extension(s3_object_key)
        
        # The system should process the file if and only if it has a supported audio extension
        should_process = should_process_file(s3_object_key)
        is_supported = is_supported_audio_format(s3_object_key)
        
        # Both functions should return the same result
        assert should_process == is_supported
        
        # If the file has a supported extension (case-insensitive), it should be processed
        if extension and extension.lower() in {'.mp3', '.wav'}:
            assert should_process is True, f"File with extension {extension} should be processed"
            assert is_supported is True, f"File with extension {extension} should be supported"
        else:
            assert should_process is False, f"File with extension {extension} should not be processed"
            assert is_supported is False, f"File with extension {extension} should not be supported"
    
    @given(st.text(min_size=1, max_size=50))
    def test_extension_extraction_consistency(self, filename):
        """
        Property: Extension extraction should be consistent and handle all input types.
        
        For any filename, extract_file_extension should either return a string starting 
        with '.' or None, and the result should be consistent across multiple calls.
        """
        assume(filename)  # Ensure filename is not empty
        
        extension1 = extract_file_extension(filename)
        extension2 = extract_file_extension(filename)
        
        # Results should be consistent
        assert extension1 == extension2
        
        # If extension exists, it should start with '.'
        if extension1 is not None:
            assert extension1.startswith('.'), f"Extension {extension1} should start with '.'"
    
    @given(s3_object_key_strategy)
    def test_case_insensitive_validation(self, base_filename):
        """
        Property: Case-insensitive validation should work for all case variations.
        
        For any base filename, adding .mp3 or .wav in any case combination should 
        result in the file being recognized as supported.
        """
        assume(base_filename)  # Ensure base filename is not empty
        
        # Test all case variations of .mp3
        mp3_variations = ['.mp3', '.MP3', '.Mp3', '.mP3']
        for ext in mp3_variations:
            filename = f"{base_filename}{ext}"
            assert is_supported_audio_format(filename) is True, f"File {filename} should be supported"
            assert should_process_file(filename) is True, f"File {filename} should be processed"
        
        # Test all case variations of .wav
        wav_variations = ['.wav', '.WAV', '.Wav', '.wAv']
        for ext in wav_variations:
            filename = f"{base_filename}{ext}"
            assert is_supported_audio_format(filename) is True, f"File {filename} should be supported"
            assert should_process_file(filename) is True, f"File {filename} should be processed"
    
    @given(st.text(min_size=1, max_size=50), st.sampled_from(['.txt', '.pdf', '.jpg', '.png', '.doc', '.docx', '.mp4']))
    def test_unsupported_formats_rejected(self, base_filename, unsupported_ext):
        """
        Property: Files with unsupported extensions should always be rejected.
        
        For any filename with a non-audio extension, the system should not process it.
        """
        assume(base_filename)  # Ensure base filename is not empty
        
        filename = f"{base_filename}{unsupported_ext}"
        
        assert is_supported_audio_format(filename) is False, f"File {filename} should not be supported"
        assert should_process_file(filename) is False, f"File {filename} should not be processed"
    
    @given(st.text(min_size=1, max_size=50).filter(lambda x: '.' not in x))
    def test_no_extension_files_rejected(self, filename_without_extension):
        """
        Property: Files without extensions should always be rejected.
        
        For any filename without an extension, the system should not process it.
        """
        assume(filename_without_extension)  # Ensure filename is not empty
        
        assert extract_file_extension(filename_without_extension) is None
        assert is_supported_audio_format(filename_without_extension) is False
        assert should_process_file(filename_without_extension) is False